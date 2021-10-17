from sql.database import db
from flask.blueprints import Blueprint

import telebot
import flask

import logging
import time

from loader import TELEGRAM_TOKEN
from loader import WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://%s" % WEBHOOK_HOST
WEBHOOK_URL_PATH = "/%s/" % TELEGRAM_TOKEN

bot = Blueprint('bot', __name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

tg_bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded = False)
print(tg_bot.get_me())


# Create table user with pole id
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)


@bot.route('/', methods = ['GET', 'HEAD'])
def index():
    return "Hello"


# Process webhook calls
@bot.route(WEBHOOK_URL_PATH, methods = ['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        tg_bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# Handle '/start' and '/help'
@tg_bot.message_handler(commands = ['help', 'start'])
def send_welcome(message):
    print("start command")
    if User.query.filter_by(id = message.char.id):
        tg_bot.send_message(message.chat.id, "Hey!")
    else:
        tg_bot.send_message(message.chat.id, "Register first!")
        db.session.add(User(id = message.char.id))
        db.session.commit()


# Handle all other messages
@tg_bot.message_handler(func = lambda message: True, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, message.text)


# Remove webhook, it fails sometimes the set if there is a previous webhook
tg_bot.remove_webhook()

time.sleep(0.1)

# Set webhook
tg_bot.set_webhook(url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
