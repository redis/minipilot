from langchain.schema import BaseRetriever
from langchain.schema import Document
from langchain.schema.vectorstore import VectorStore

from src.common.config import MINIPILOT_RELEVANCE_SCORE


# https://python.langchain.com/docs/integrations/vectorstores/redis

class RedisRetrieverWithScore(BaseRetriever):
    vectorstore: VectorStore
    context: int

    class Config:
        arbitrary_types_allowed = True

    def combine_metadata(self, doc) -> str:
        metadata = doc[0].metadata
        return (
                "Movie Title: " + metadata["names"] + ". " +
                "Movie Genre: " + metadata["genre"] + ". " +
                "Movie Score: " + metadata["score"] + "." +
                "Movie Country: " + metadata["country"] + "." +
                "Movie Revenuw: " + metadata["revenue"] + "." +
                "Movie Relase date: " + metadata["date_x"] + "."
        )

    def get_relevant_documents(self, query) -> []:
        docs = []
        for doc in self.vectorstore.similarity_search_with_relevance_scores(query, k=self.context, score_threshold=MINIPILOT_RELEVANCE_SCORE):
            content = self.combine_metadata(doc)
            docs.append(Document(
                page_content=doc[0].page_content + content,
                metadata=doc[0].metadata
            ))
        return docs