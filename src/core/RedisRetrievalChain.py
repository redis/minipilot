import logging
import time

from flask import current_app
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import RedisChatMessageHistory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.vectorstores.redis import Redis
from langchain.chat_models import ChatOpenAI
import openai
import queue
import threading

from langchain_core.messages import BaseMessage

from src.common.ConfigProvider import ConfigProvider
from src.core.RedisRetriever import RedisRetriever
from src.core.RedisRetrieverWithScore import RedisRetrieverWithScore
from src.core.StreamingStdOutCallbackHandlerYield import StreamingStdOutCallbackHandlerYield, STOP_ITEM
from src.common.config import REDIS_CFG, MINIPILOT_HISTORY_TIMEOUT, OPENAI_MODEL, MINIPILOT_LLM_TIMEOUT, \
    MINIPILOT_HISTORY_LENGTH, MINIPILOT_CONTEXT_LENGTH, MINIPILOT_CACHE_ENABLED, MINIPILOT_DEBUG
from src.common.utils import generate_redis_connection_string
from src.core.Core import Core


class RedisRetrievalChain(Core):
    def __init__(self, session_id):
        super().__init__()
        self.session_id = session_id
        self.queue = queue.Queue()
        self.model = OPENAI_MODEL
        self.llmcache = current_app.llmcache
        self.prompt_manager = current_app.prompt_manager
        self.index_schema = current_app.index_schema
        self.embedding_model = OpenAIEmbeddings()
        self.cfg = ConfigProvider()

        try:
            self.rds = Redis.from_existing_index(
                self.embedding_model,
                index_name="minipilot_rag_alias",
                schema=self.index_schema,
                redis_url=generate_redis_connection_string(REDIS_CFG["host"], REDIS_CFG["port"], REDIS_CFG["password"])
            )
        except Exception as e:
            raise ValueError("Cannot answer. Remember to create a semantic index and make it current")


    def __get_retriever(self, results):
        return RedisRetriever(vectorstore=self.rds, context=results)


    def __get_retriever_with_score(self, results):
        return RedisRetrieverWithScore(vectorstore=self.rds, context=results)


    def ask(self, question):
        self.question = question
        threading.Thread(target=self.__ask_question, args=(question, StreamingStdOutCallbackHandlerYield(self.queue))).start()


    def references(self, q, results=0):
        if results == 0:
            results = MINIPILOT_CONTEXT_LENGTH

        json_data = []
        for doc in self.__get_retriever_with_score(results).invoke(q):
            json_data.append(doc.json())
        return json_data


    def reset_history(self):
        redis_history = RedisChatMessageHistory(url=generate_redis_connection_string(REDIS_CFG["host"], REDIS_CFG["port"], REDIS_CFG["password"]),
                                                session_id=self.session_id,
                                                key_prefix='minipilot:history:',
                                                ttl=MINIPILOT_HISTORY_TIMEOUT)
        redis_history.clear()


    def __ask_question(self, q, callback_fn: StreamingStdOutCallbackHandlerYield):
        # Chatbot with history managed by LangChain
        redis_history = RedisChatMessageHistory(url=generate_redis_connection_string(REDIS_CFG["host"], REDIS_CFG["port"], REDIS_CFG["password"]),
                                                session_id=self.session_id,
                                                key_prefix='minipilot:history:',
                                                ttl=MINIPILOT_HISTORY_TIMEOUT)

        # Managing the semantic cache
        if self.cfg.is_semantic_cache():
            cached = self.llmcache.check(prompt=q, return_fields=["response", "metadata"])
            if len(cached) > 0:
                callback_fn.q.put(cached[0]['response'])
                callback_fn.q.put(STOP_ITEM)

                # The question is in the cache, but we want to save the conversation in the history too
                # but only if the memory is enabled
                if self.cfg.is_memory():
                    metadata = {}
                    if 'metadata' in cached[0]:
                        metadata = cached[0]['metadata']
                    redis_history.add_user_message(q)
                    redis_history.add_message(BaseMessage(content=cached[0]['response'], type="ai", additional_kwargs=metadata))
                    return

        # llm = OpenAI(streaming=True, callbacks=[callback_fn])
        streaming_llm = ChatOpenAI(
            model_name=self.model,
            streaming=True,
            verbose=False,
            temperature=1,
            callbacks=[callback_fn] #, StreamingStdOutCallbackHandler()
        )

        # limit the history length to MINIPILOT_HISTORY_LENGTH
        history_length = redis_history.redis_client.llen(redis_history.key)
        if (history_length > MINIPILOT_HISTORY_LENGTH):
            redis_history.redis_client.rpop(redis_history.key, history_length - MINIPILOT_HISTORY_LENGTH)

        # Chatbot with custom history, here we choose a non-streaming LLM, or we will get the condensed question
        # in the callback
        def get_chat_history(inputs) -> str:
            return inputs

        messages = [
            SystemMessagePromptTemplate.from_template(self.prompt_manager.get_system_prompt()['content']),
            HumanMessagePromptTemplate.from_template(self.prompt_manager.get_user_prompt()['content'])
        ]

        qa_prompt = ChatPromptTemplate.from_messages(messages)

        """
        Chain for having a conversation based on retrieved documents.
        This chain takes in chat history (a list of messages) and new questions, and then returns an answer to that question. The algorithm for this chain consists of three parts:
        1. Use the chat history and the new question to create a "standalone question". This is done so that this question can be passed into the retrieval step to fetch relevant documents. If only the new question was passed in, then relevant context may be lacking. If the whole conversation was passed into retrieval, there may be unnecessary information there that would distract from retrieval.
        2. This new question is passed to the retriever and relevant documents are returned.
        3. The retrieved documents are passed to an LLM along with either the new question (default behavior) or the original question and chat history to generate a final response.
        """

        # now you can rebuild this using https://js.langchain.com/v0.1/docs/use_cases/code_understanding/#chat
        # https://python.langchain.com/v0.2/docs/versions/migrating_chains/conversation_retrieval_chain/
        chatbot = ConversationalRetrievalChain.from_llm(llm=streaming_llm,
                                                        retriever=self.__get_retriever_with_score(MINIPILOT_CONTEXT_LENGTH),    # RAG
                                                        get_chat_history=get_chat_history,                                      # LLM Memory
                                                        rephrase_question=False,
                                                        return_generated_question=True,
                                                        verbose=MINIPILOT_DEBUG,
                                                        return_source_documents=True,
                                                        condense_question_llm = ChatOpenAI(temperature=0, model=self.model),    # LLM Memory part 2: condense
                                                        combine_docs_chain_kwargs={'prompt': qa_prompt})                        # Agentic Memory

        result = None
        try:
            result = chatbot.invoke({"question": q, "chat_history": redis_history})

            references = {}
            for doc in result['source_documents']:
                references[doc.metadata['id'].split('idx:')[-1]] = doc.metadata

            # decide if conversation history should be saved
            if self.cfg.is_memory():
                redis_history.add_user_message(result["question"])
                redis_history.add_message(BaseMessage(content=result["answer"], type="ai", additional_kwargs=references))

            """
            Update the cache only if caching is enabled AND there was context retrieved for RAG
            First, we save the generated standalone question, which also includes summarization of the history
            Second, having references means that there is semantic content available in the database, so the question should make sense
            and it can be stored, otherwise the following might happen:
            1. ask a question "can this or that happen?"
            2. get references for RAG, forward the prompt to the LMM and get an answer, hence cache the pair question/asnwer
            3. the user asks "are you completely sure?"
            4. this interaction will cause the LLM to answer this last question based on conversation history
            5. however, "are you completely sure?" will likely not produce relevant results for RAG (filtered out by a threshold)
               and then it makes no sense to store the pair question/answer
            """

            # decide if the interaction should be cached
            if len(references) and self.cfg.is_semantic_cache():
                self.llmcache.store(prompt=result["generated_question"],
                                    response=result["answer"],
                                    metadata=references)

        except openai.OpenAIError as e:
            callback_fn.notify("This conversation is too long, started a new one")
            logging.warning(f"OpenAIError: {e}")
            redis_history.clear()
            return None
        return result


    def streamer(self):
        answer = ""
        start = time.time()
        ttft = 0
        while True:
            try:
                result = self.queue.get(block=True, timeout=int(MINIPILOT_LLM_TIMEOUT))
                if ttft == 0:
                    ttft = time.time() - start
            except queue.Empty:
                answer = "The server is overloaded, retry later. Thanks for your patience"
                self.log(self.session_id, self.question, answer, int(ttft * 1000), int((time.time() - start) * 1000))
                yield answer
                break
            if result == STOP_ITEM or result is None:
                self.log(self.session_id, self.question, answer, int(ttft*1000), int((time.time() - start)*1000))
                break
            answer += result
            yield result
