from langchain.schema import BaseRetriever
from langchain.schema import Document
from langchain.schema.vectorstore import VectorStore
from src.common.config import MINIPILOT_CONTEXT_RELEVANCE_SCORE


class RedisRetrieverWithScore(BaseRetriever):
    vectorstore: VectorStore
    context: int        # the maximium number of results returned

    class Config:
        arbitrary_types_allowed = True

    def combine_metadata(self, doc) -> str:
        metadata = doc[0].metadata
        return (
            '\n'.join([f"{key}: {value}" for key, value in metadata.items()])
        )

    # We'll retrieve a maximum number of documents from our RAG database for a maximum of `context` retults that a minimum relevance score.
    def get_relevant_documents(self, query) -> []:
        docs = []
        for doc in self.vectorstore.similarity_search_with_relevance_scores(query, k=self.context, score_threshold=MINIPILOT_CONTEXT_RELEVANCE_SCORE):
            docs.append(Document(
                page_content=doc[0].page_content + self.combine_metadata(doc),
                metadata=doc[0].metadata
            ))
        return docs