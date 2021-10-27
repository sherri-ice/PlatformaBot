from flask.blueprints import Blueprint

from telegram_bot import get_telegram_bot
from telebot import types
import flask
from flask import request

from loader import TELEGRAM_TOKEN
import time

from sql.user.user import register_vk_session

from loader import WEBHOOK_HOST

from vk_auth import request_vk_auth

WEBHOOK_URL_BASE = "https://%s" % WEBHOOK_HOST
WEBHOOK_URL_PATH = "/%s/" % TELEGRAM_TOKEN

# Init new module for bot, later the one for the site will appear
bot_handler = Blueprint('bot', __name__)

# Get created telegram bot
telegram_bot = get_telegram_bot()


# Holds server indexes
@bot_handler.route('/', methods = ['GET', 'HEAD'])
def index():
    return "Hello"


# Process vk auth calls
@bot_handler.route('/vk_auth', methods = ['GET'])
def redirect_from_vk():
    vk_token = request.args.get('access_token')
    tg_id = request.args.get("tg_id")
    register_vk_session(tg_id, vk_token)
    vk_id = request.args.get("id")
    telegram_bot.send_message(tg_id, f"Registered! Your account id: {vk_id}")
    return ''


# Process webhook calls
@bot_handler.route(WEBHOOK_URL_PATH, methods = ['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        telegram_bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# Remove webhook, it fails sometimes the set if there is a previous webhook
telegram_bot.remove_webhook()

time.sleep(0.1)

# Set webhook
telegram_bot.set_webhook(url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

# TODO: unregistered user can't call smth except /start
