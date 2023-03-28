import uuid
from typing import Dict, List

import pinecone
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings

from constants import BASE_EMBEDDING_LENGTH

pinecone.init(
    api_key="7348774e-f6d1-47f6-91c2-b955e910fe4c", environment="us-east1-gcp"
)
embeddings = OpenAIEmbeddings()


def create_new_user_index() -> str:
    """Create new user index in pinecone."""
    new_index_name = str(uuid.uuid4())
    pinecone.create_index(new_index_name, dimension=BASE_EMBEDDING_LENGTH)
    return new_index_name


def insert_docs(index: pinecone.Index, texts: List[str], metadatas: List[Dict]) -> None:
    """Insert text documents into pinecone"""
    docs = []
    ids = [str(uuid.uuid4()) for _ in texts]
    for i, text in enumerate(texts):
        embedding = embeddings.embed_query(text)
        metadata = metadatas[i] if metadatas else {}
        metadata["text"] = text
        docs.append((ids[i], embedding, metadata))
    # upsert to Pinecone
    index.upsert(vectors=docs, batch_size=30)


def find_docs(index: pinecone.Index, query: str, k: int = 3) -> List[Document]:
    """Return list of closest documents to the current query."""
    query_obj = embeddings.embed_query(query)
    docs = []
    results = index.query(
        [query_obj],
        top_k=k,
        include_metadata=True,
    )
    for res in results["matches"]:
        metadata = res["metadata"]
        text = metadata.pop("text")
        docs.append(Document(page_content=text, metadata=metadata))
    return docs
