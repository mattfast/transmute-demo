from enum import Enum

USER_TABLE_NAME = "UserInfo"
USER_TABLE_NUM = "user_num"
USER_TABLE_PINECONE_INDEX = "pinecone_index"
USER_TABLE_PERSONA = "persona"

FRIEND_TABLE_NAME = "Friends"
FRIEND_TABLE_USER_NUM = "user_num"
FRIEND_TABLE_FRIEND_NUM = "friend_num"
FRIEND_TABLE_ACCEPTED = "accepted"


SUMMARY_TABLE_NAME = "Summaries"
SUMMARY_TABLE_NUM = "user_num"
SUMMARY_TABLE_LINK = "link"
SUMMARY_TABLE_MAIN_SUMMARY = "summary"
SUMMARY_TABLE_PERSONA = "persona"
SUMMARY_TABLE_SYNTHESIS = "synthesis"

DEFAULT_PERSONA = "valley girl"

# Hardcode OpenAI Embedding length. Should change in future
BASE_EMBEDDING_LENGTH = 1536


class MessageType(Enum):
    INFO_MESSAGE = "info"
    PERSONA_MESSAGE = "persona"
    ADD_FRIEND_MESSAGE = "add_friend"
    ADD_NAME_MESSAGE = "add_name"
    INSIGHTS_MESSAGE = "insights"
