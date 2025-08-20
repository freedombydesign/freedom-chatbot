from supabase import create_client
import os

# Supabase client setup
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


def save_user(user_id: str):
    """Insert a new user into the users table if not exists."""
    existing = supabase.table("users").select("*").eq("id", user_id).execute()
    if not existing.data:
        supabase.table("users").insert({"id": user_id}).execute()


def get_user(user_id: str):
    """Get user details from the users table."""
    return supabase.table("users").select("*").eq("id", user_id).execute().data


def save_message(user_id: str, role: str, content: str):
    """Save a chat message to the messages table."""
    supabase.table("messages").insert({
        "user_id": user_id,
        "role": role,
        "content": content
    }).execute()


def get_messages(user_id: str, limit: int = 10):
    """Retrieve the most recent chat messages for a user."""
    response = supabase.table("messages")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    # return in chronological order (oldest first)
    return list(reversed(response.data))
