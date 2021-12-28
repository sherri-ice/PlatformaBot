import os
from dotenv import load_dotenv
import json

BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Connect the path with your '.env' file name
load_dotenv(os.path.join(BASEDIR, '.env'))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
SQL_HOST = os.getenv("SQL_HOST")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DATABASE = os.getenv("SQL_DATABASE")
VK_API_APP_ID = os.getenv("VK_API_APP_ID")
REDIRECT_FROM_VK: str = os.getenv("REDIRECT_FROM_VK")
VK_CLIENT_SECRET = os.getenv("VK_CLIENT_SECRET")
INSTA_API_APP_ID = os.getenv("INSTA_API_APP_ID")
REDIRECT_FROM_INSTA: str = os.getenv("REDIRECT_FROM_INSTA")
INSTA_CLIENT_SECRET = os.getenv("INSTA_CLIENT_SECRET")
MAPS_TOKEN: str = os.getenv("MAPS_TOKEN")
VK_SERVICE_TOKEN: str = os.getenv("VK_SERVICE_TOKEN")

# project_path = "/home/sherriice/PlatformaBot"


project_path = "/home/sherri.ice/Documents/bot/project"


def load_messages():
    with open(f'{project_path}/meta/messages_answers.json') as json_file:
        data = json.load(json_file)
        return data


def load_buttons():
    with open(f'{project_path}/meta/buttons.json') as json_file:
        data = json.load(json_file)
        return data


def load_photos():
    with open(f'{project_path}/meta/photos.json') as json_file:
        data = json.load(json_file)
        return data


def load_prices():
    with open(f'{project_path}/meta/prices.json') as json_file:
        data = json.load(json_file)
        return data
