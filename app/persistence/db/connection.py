# File to connect with Supabase
# Use Singleton patter to instance and create only one instance
from supabase import Client, create_client
from supabase.lib.client_options import (
    ClientOptions,
)

from app.core.config import settings


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


class AdminSupabaseClient:
    _instance: Client = None

    @classmethod
    def get_admin_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(
                settings.supabase_url,
                settings.supabase_role_key,
                options=ClientOptions(
                    auto_refresh_token=False,
                    persist_session=False,
                ),
            )
        return cls._instance


def get_admin_supabase() -> Client:
    return AdminSupabaseClient.get_admin_client()
