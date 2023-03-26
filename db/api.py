from typing import Dict, List, Optional

from config import supabase
from constants import (
    DEFAULT_PERSONA,
    SUMMARY_TABLE_LINK,
    SUMMARY_TABLE_NAME,
    SUMMARY_TABLE_NUM,
    USER_TABLE_NAME,
    USER_TABLE_NUM,
    USER_TABLE_PERSONA,
    USER_TABLE_PINECONE_INDEX,
)


def fetch_user_info(user_num: str) -> Optional[Dict]:
    """Fetch user info from supabase UserInfo Table."""
    users = (
        supabase.table(USER_TABLE_NAME)
        .select("*")
        .filter(USER_TABLE_NUM, "eq", user_num)
        .execute()
        .data
    )
    return users[0] if len(users) > 1 else None


def create_new_user(
    user_num: str, index_name: str, persona: Optional[str] = None
) -> None:
    """Create a new user."""
    persona = DEFAULT_PERSONA if persona is None else persona
    user_info = {
        USER_TABLE_NUM: user_num,
        USER_TABLE_PINECONE_INDEX: index_name,
        USER_TABLE_PERSONA: persona,
    }
    resp = supabase.table("UserInfo").insert(user_info).execute().data
    assert len(resp) > 0


def fetch_link_info(user_num: str, link: str) -> Optional[Dict]:
    """Fetch Link info from supabase Summaries Table."""
    summaries = (
        supabase.table(SUMMARY_TABLE_NAME)
        .select("*")
        .filter(SUMMARY_TABLE_NUM, "eq", user_num)
        .filter(SUMMARY_TABLE_LINK, "eq", link)
        .execute()
        .data
    )
    return summaries[0] if len(summaries) > 1 else None


def insert_summary_info() -> None:
    """Insert summary info."""
