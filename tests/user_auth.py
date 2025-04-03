import pytest
from app.persistence.db.connection import (
    get_supabase,
)
from supabase import Client

from app.api.authentication import (
    get_current_user,
)


@pytest.fixture
def supabase_client() -> Client:
    client = get_supabase()
    yield client
