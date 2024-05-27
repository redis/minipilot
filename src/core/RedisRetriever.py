from langchain.schema import BaseRetriever
from langchain.schema import Document
from langchain.schema.vectorstore import VectorStore


class RedisRetriever(BaseRetriever):
    vectorstore: VectorStore
    context: int

    class Config:
        arbitrary_types_allowed = True

    def combine_metadata(self, doc) -> str:
        metadata = doc.metadata
        return (
                "Movie Title: " + metadata["names"] + ". " +
                "Movie Genre: " + metadata["genre"] + ". " +
                "Movie Score: " + metadata["score"] + "." +
                "Movie Country: " + metadata["country"] + "." +
                "Movie Revenue: " + metadata["revenue"] + "." +
                "Movie Release date: " + metadata["date_x"] + "."
        )

    def get_relevant_documents(self, query) -> []:
        docs = []
        for doc in self.vectorstore.similarity_search(query, k=self.context):
            content = self.combine_metadata(doc)
            docs.append(Document(
                page_content=doc.page_content,
                metadata=doc.metadata
            ))
        return docs