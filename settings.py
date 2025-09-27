import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

FINANCE_ID = int(os.getenv("FINANCE_CHANNEL_ID"))
HABIT_ID = int(os.getenv("HABIT_CHANNEL_ID"))
PROGRESS_ID = int(os.getenv("PROGRESS_CHANNEL_ID"))
GENERAL_ID = int(os.getenv("GENERAL_CHANNEL_ID"))
GIT_ID = int(os.getenv("GITUPDATE_CHANNEL_ID"))
STATUS_ID = int(os.getenv("STATUS_CHANNEL_ID"))

DATABASE_HOSTNAME = os.getenv("DATABASE_HOST_IP")
ACTIVE_USERNAME = os.getenv("DATABASE_USERNAME")
ACTIVE_USER_PWD = os.getenv("USER_PASSWORD")
ACTIVE_DATABASE = os.getenv("DATABASE_NAME")

IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASSWORD")
