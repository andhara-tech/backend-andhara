import pytest
from supabase import Client

from app.persistence.db.connection import (
    get_supabase,
)


@pytest.fixture
def supabase_client() -> Client:
    return get_supabase()
