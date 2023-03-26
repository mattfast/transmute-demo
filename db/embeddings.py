import uuid

import pinecone

from constants import BASE_EMBEDDING_LENGTH

pinecone.init(
    api_key="7348774e-f6d1-47f6-91c2-b955e910fe4c", environment="us-east1-gcp"
)


def create_new_user_index() -> str:
    """Create new user index in pinecone."""
    new_index_name = str(uuid.uuid4())
    pinecone.create_index(new_index_name, dimension=BASE_EMBEDDING_LENGTH)
    return new_index_name
