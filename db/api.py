from config import supabase
from typing import Optional, List, Dict
from constants import USER_TABLE_NAME, USER_TABLE_NUM, USER_TABLE_PINECONE_INDEX, USER_TABLE_PERSONA, DEFAULT_PERSONA


def fetch_user_info(user_num: str) -> Optional[List[Dict]]:
    """Fetch user info from supabase UserInfo Table."""
    users = (
        supabase.table(USER_TABLE_NAME)
            .select("*")
            .filter(USER_TABLE_NUM, "eq", user_num)
            .execute()
            .data
    )
    return users[0] if len(users) > 1 else None


def create_new_user(user_num: str, index_name: str, persona: Optional[str] = None) -> None:
    """Crete a new user."""
    persona = DEFAULT_PERSONA if persona is None else persona
    user_info = {
        USER_TABLE_NUM: user_num,
        USER_TABLE_PINECONE_INDEX: index_name,
        USER_TABLE_PERSONA: persona,
    }
    resp = supabase.table("UserInfo").insert(user_info).execute().data
    assert len(resp) > 0