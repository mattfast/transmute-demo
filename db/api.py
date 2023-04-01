from typing import Dict, List, Optional

from config import supabase
from constants import (
    DEFAULT_PERSONA,
    FRIEND_TABLE_FRIEND_NUM,
    FRIEND_TABLE_NAME,
    FRIEND_TABLE_USER_NUM,
    SUMMARY_TABLE_LINK,
    SUMMARY_TABLE_MAIN_SUMMARY,
    SUMMARY_TABLE_NAME,
    SUMMARY_TABLE_NUM,
    SUMMARY_TABLE_SYNTHESIS,
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
    return users[0] if len(users) > 0 else None


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
    return summaries[0] if len(summaries) > 0 else None


def insert_summary_info(user_num: str, link: str, summary: str, synthesis: str) -> None:
    """Insert summary info."""
    summary_info = {
        SUMMARY_TABLE_NUM: user_num,
        SUMMARY_TABLE_LINK: link,
        SUMMARY_TABLE_MAIN_SUMMARY: summary,
        SUMMARY_TABLE_SYNTHESIS: synthesis,
    }
    resp = supabase.table(SUMMARY_TABLE_NAME).insert(summary_info).execute().data
    assert len(resp) > 0


def update_persona_info(user_num: str, persona: str) -> None:
    """Update Persona Info"""
    user_info = {
        USER_TABLE_PERSONA: persona,
    }
    resp = (
        supabase.table("UserInfo")
        .update(user_info)
        .filter(USER_TABLE_NUM, "eq", user_num)
        .execute()
        .data
    )
    assert len(resp) > 0


def add_friend_info(user_num: str, friend_num: str) -> None:
    """Add friend Info to table."""
    # TODO: Add checks to make sure that ppl aren't already friends
    friend_info = {FRIEND_TABLE_USER_NUM: user_num, FRIEND_TABLE_FRIEND_NUM: friend_num}

    resp = supabase.table(FRIEND_TABLE_NAME).insert(friend_info).execute().data
    assert len(resp) > 0
