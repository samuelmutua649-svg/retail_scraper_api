import os
from dotenv import load_dotenv

load_dotenv()

# Reads from .env locally or environment variables in production
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TARGET_URL = os.getenv("TARGET_URL")

# Database Configuration
DB_FILE = os.getenv("DB_FILE", "jumia_tracker.db")


