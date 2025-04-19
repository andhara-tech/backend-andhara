import pytest
from app.persistence.db.connection import (
    get_supabase,
)
from supabase import Client


@pytest.fixture
def supabase_client() -> Client:
    client = get_supabase()
    yield client
