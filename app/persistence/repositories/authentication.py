# This file contains the main logic to manage the authentication with supabase
from gotrue import User
from supabase import Client  # noqa: TC002

from app.persistence.db.connection import get_admin_supabase, get_supabase


class AuthenticationRepository:
    def __init__(self) -> None:
        self.admin_supabase: Client = get_admin_supabase()
        self.supabase: Client = get_supabase()

    async def list_all_users(self) -> list[User]:
        """
        Retrieves all users from Supabase authentication.

        Note: Requires admin privileges and may need pagination
        for large user bases.
        """
        try:
            return self.admin_supabase.auth.admin.list_users()
        except Exception as e:
            msg = "Failed to list users"
            raise Exception(msg, e) from e

    async def logout_user(self, token: str) -> bool:
        """Logs out the currently authenticated user invalidating session."""
        try:
            self.supabase.auth.admin.sign_out(token)
            return True
        except Exception as e:
            msg = "Failed to log out user"
            raise Exception(msg, {e}) from e
