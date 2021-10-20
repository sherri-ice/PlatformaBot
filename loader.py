import os
from dotenv import load_dotenv

load_dotenv(".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
SQL_HOST = os.getenv("SQL_HOST")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DATABASE = os.getenv("SQL_DATABASE")
VK_API_APP_ID = os.getenv("VK_API_APP_ID")
REDIRECT_FROM_VK = os.getenv("REDIRECT_FROM_VK")
