import os
from dotenv import load_dotenv

load_dotenv("consts/token.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
