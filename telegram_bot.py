import logging
import telebot
from telebot import types
from vk_auth import request_vk_auth_code
from sql.database import db, apply_db_changes
from sql.user.user import get_user_by_id, add_new_user, get_vk_api

from loader import TELEGRAM_TOKEN

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

tg_bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded = False)


@tg_bot.message_handler(commands = ['start'])
def send_welcome(message):
    user = get_user_by_id(message.chat.id)
    if user is not None:
        tg_bot.send_message(message.chat.id, "Hey! I know you :)")

    else:
        tg_bot.send_message(message.chat.id, "Send /register.")


@tg_bot.message_handler(commands = ['vk_auth'])
def vk_auth_register(message):
    tg_bot.send_message(message.chat.id, "Vk auth", reply_markup = gen_markup_for_vk_auth(message.chat.id))


@tg_bot.message_handler(commands = ['ping_vk'])
def vk_auth_register(message):
    vk = get_vk_api(message.chat.id)
    data = vk.getProfileInfo()
    tg_bot.send_message(message.chat.id, f"Your profile name: {data['first_name']}")


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
    tg_bot.send_message(message.chat.id, f"Great! Hello, {user.name}, your age is {user.age}."
                                         f"Now connect your vk account:")
    tg_bot.register_next_step_handler(message, vk_auth_register)


# Creates a markup with link to auth url
def gen_markup_for_vk_auth(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton(text = "VK auth", url = request_vk_auth_code(chat_id)))
    return markup


# Handle all other messages from unregistered users
@tg_bot.message_handler(func = lambda message: get_user_by_id(message.chat.id) is None, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, "Register first!")


@tg_bot.message_handler(func = lambda message: get_user_by_id(message.chat.id) is not None, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, "Sorry, now I can't answer for this...")


def get_telegram_bot():
    return tg_bot
