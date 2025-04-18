# This file contains the main logic to manage the authentication interaction with supabase
from typing import List

from gotrue import User

from app.persistence.db.connection import (
    get_admin_supabase,
)


class AuthenticationRepository:
    def __init__(self):
        self.supabase = get_admin_supabase()

    async def list_all_users(self) -> List[User]:
        return (
            self.supabase.auth.admin.list_users()
        )
