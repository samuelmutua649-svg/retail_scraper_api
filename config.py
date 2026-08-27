import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1541023573794357271/PLL5RvPBjWBhCBLNZPopsnca6zDJI4L3UxHlrYmRNhZvHZiIJ2Wb6sSOFvkYxyJTOxFW")
# Target Scraper URLs
TARGET_URL = "https://www.jumia.co.ke/smartphones/"

# Database Configuration
DB_FILE = "jumia_tracker.db"


