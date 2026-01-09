from supabase import Client, create_client

from app.core.config import settings


def get_supabase_client() -> Client:
    """Create & return a Supabase client"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


supabase_client = get_supabase_client()
