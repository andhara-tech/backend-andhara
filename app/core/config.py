# This file manage the main configuration for the project
# Environment variables and more...
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Andhara Backend"
    supabase_url: str
    supabase_key: str
    supabase_role_key: str
    allowed_cors: str
    email_admin: str

    class Config:
        env_file = ".env"


settings = Settings()
