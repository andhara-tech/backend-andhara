# File to connect with Supabase
# Use Singleton patter to instance and create only one instance
from app.core.config import settings

from supabase import create_client, Client


class SupabaseClient:
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(
                settings.supabase_url,
                settings.supabase_key,
            )
        return cls._instance


def get_supabase() -> Client:
    return SupabaseClient.get_client()
