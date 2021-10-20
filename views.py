from telebot import types

from sql.database import db, User, get_user_by_id, add_new_user, apply_db_changes
from flask.blueprints import Blueprint

import telebot
import flask
from flask import request

import logging
import time

from loader import TELEGRAM_TOKEN
from loader import WEBHOOK_HOST
from loader import REDIRECT_FROM_VK

from vk_auth import request_vk_auth

WEBHOOK_URL_BASE = "https://%s" % WEBHOOK_HOST
WEBHOOK_URL_PATH = "/%s/" % TELEGRAM_TOKEN

# Init new module for bot, later the one for the site will appear
bot = Blueprint('bot', __name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# Creates bot
tg_bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded = False)


# Holds server indexes
@bot.route('/', methods = ['GET', 'HEAD'])
def index():
    return "Hello"


@bot.route(REDIRECT_FROM_VK, methods = ['GET'])
def redirect_form_vk():
    code = request.args.get('code')


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
@tg_bot.message_handler(commands = ['start'])
def send_welcome(message):
    user = get_user_by_id(message.chat.id)
    if user is not None:
        tg_bot.send_message(message.chat.id, "Hey! I know you :)")

    else:
        tg_bot.send_message(message.chat.id, "Send /register.")


# Creates a markup with link to auth url
def gen_markup_for_vk_auth():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton(text = "VK auth", url = request_vk_auth()))
    return markup


# Handles '/vk_auth'
@tg_bot.message_handler(commands = ['vk_auth'])
def vk_auth(message):
    tg_bot.send_message(message.chat.id, "Vk auth", reply_markup = gen_markup_for_vk_auth())


# Handles '/register'
@tg_bot.message_handler(commands = ['register'])
def register(message):
    tg_bot.send_message(message.chat.id, "Let's get to know each other :) \n Send me your name:")
    tg_bot.register_next_step_handler(message, process_name_step)


# TODO: strange names, as commands name...
def process_name_step(message):
    name = message.text
    id = message.chat.id
    user = get_user_by_id(id)
    if user is None:
        user = add_new_user(id)
    user.name = name
    apply_db_changes()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard = True)
    markup.add('12-18', '18-21', '24-27', '27+')
    msg = tg_bot.reply_to(message, 'Your age:', reply_markup = markup)
    tg_bot.register_next_step_handler(msg, process_age_step)


def process_age_step(message):
    age = message.text
    user = get_user_by_id(message.chat.id)
    user.age = age
    tg_bot.send_message(message.chat.id, f"Great! Hello, {user.name}, your age is {user.age}")


# Handle all other messages from unregistered users
@tg_bot.message_handler(func = lambda message: get_user_by_id(message.chat.id) is None, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, "Register first!")


# Remove webhook, it fails sometimes the set if there is a previous webhook
tg_bot.remove_webhook()

time.sleep(0.1)

# Set webhook
tg_bot.set_webhook(url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

# TODO: unregistered user can't call smth except /start
