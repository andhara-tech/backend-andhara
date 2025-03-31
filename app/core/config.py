# This file manage the main configuration for the project
# Environment variables and more...
from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    VERSION = os.getenv("VERSION")
    AUTHOR = os.getenv("AUTHOR")
