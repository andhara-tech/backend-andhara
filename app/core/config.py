# This file manage the main configuration for the project
# Environment variables and more...
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Andhara Backend"
    project_version: str
    project_author: str
    supabase_url: str
    supabase_key: str

    class Config:
        env_file = ".env"


settings = Settings()
print(settings)
