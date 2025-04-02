import pytest

from supabase import Client
from app.persistence.db.connection import get_supabase


# Get connection
@pytest.fixture
def supabase_client() -> Client:
    client = get_supabase()
    yield client


# Test 1. Verify if the client will connect successfully
def test_supabase_connection(supabase_client: Client) -> None:
    """This test works to ensure the connection was successfully"""
    response = supabase_client.table("ciudad").select("*").limit(1).execute()

    assert response.data is not None
    assert isinstance(response.data, list)
