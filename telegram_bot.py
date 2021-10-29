import logging
import time

import telebot
import vk_api
from telebot import types
from vk_auth import request_vk_auth_code
from sql.database import db, apply_db_changes
from sql.user.user import get_user_by_id, add_new_user, get_vk_token

from loader import TELEGRAM_TOKEN
from loader import load_messages

messages_templates = load_messages()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

tg_bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded = False)
keyboard_hider = types.ReplyKeyboardRemove()


@tg_bot.message_handler(commands = ['start'])
def send_welcome(message):
    user = get_user_by_id(message.chat.id)
    if user is not None:
        tg_bot.send_message(message.chat.id, messages_templates["registered_user"]["start_message"])
    else:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["start_message"])


@tg_bot.message_handler(commands = ['vk_auth'])
def vk_auth_register(message):
    if get_vk_token(message.chat.id) is None:
        tg_bot.send_message(message.chat.id, messages_templates["vk"]["vk_error_not_found"])
    else:
        old = tg_bot.send_message(message.chat.id, messages_templates["vk"]["vk_auth_message"],
                                  reply_markup = gen_markup_for_vk_auth(
                                      message.chat.id))
        tg_bot.edit_message_text("Ждём авторизации...", old.chat.id, old.message_id)


@tg_bot.message_handler(commands = ['ping_vk'])
def ping_vk(message):
    vk = get_vk_token(message.chat.id)
    if vk is None:
        tg_bot.send_message(message.chat.id, messages_templates["vk"]["vk_not_authorized"])
    else:
        data = vk.users.get()
        if "deactivated" in data[0]:
            tg_bot.send_message(message.chat.id, messages_templates["vk"]["vk_banned_profile"])
            return
        message_to_user = messages_templates["vk"]["vk_get_user_message"].format(data[0]["first_name"],
                                                                                 data[0]["last_name"], data[0]["id"])
        tg_bot.send_message(message.chat.id, message_to_user)


# Handles '/register'
@tg_bot.message_handler(commands = ['register'])
def register(message):
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["registration_start"])
    tg_bot.register_next_step_handler(message, process_name_step)


def gen_markup_age():
    markup = types.ReplyKeyboardMarkup()
    markup.row_width = 4
    markup.add(types.KeyboardButton("12-18"),
               types.KeyboardButton("19-24"),
               types.KeyboardButton("25-27"),
               types.KeyboardButton("27+"),
               )
    return markup


# TODO: strange names, as commands name...
def process_name_step(message):
    name = message.text
    user = get_user_by_id(message.chat.id)
    if user is None:
        user = add_new_user(message.chat.id)
    user.name = name
    apply_db_changes()
    msg = tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["registration_age_step"],
                              reply_markup = gen_markup_age())
    tg_bot.register_next_step_handler(msg, process_age_step)


def process_age_step(message):
    user = get_user_by_id(message.chat.id)
    user.age = message.text
    apply_db_changes()
    tg_bot.send_message(message.chat.id, f"Супер! \nТебя зовут: {user.name} \nТвой возраст: {user.age}",
                        reply_markup = keyboard_hider)
    time.sleep(0.1)
    message_for_user = messages_templates["vk"]["vk_not_authorized"]
    msg = tg_bot.send_message(message.chat.id, message_for_user)
    tg_bot.register_next_step_handler(msg, vk_auth_register)


@tg_bot.callback_query_handler(func = lambda call: call.data == "pressed_vk_auth_key")
def callback(call):
    tg_bot.edit_message_text("Ждём авторизации...", call.message.chat.id, call.message.message_id)


# Creates a markup with link to auth url
def gen_markup_for_vk_auth(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton(text = "VK авторизация", url = request_vk_auth_code(chat_id), callback_data
    = "pressed_vk_auth_key"))
    return markup


@tg_bot.message_handler(commands = ['help', 'faq'])
def faq(message):
    tg_bot.send_message(message.chat.id, "Пока в разработке...")


# Handle all other messages from unregistered users
@tg_bot.message_handler(func = lambda message: get_user_by_id(message.chat.id) is None, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, messages_templates["unregistered_user"]["request_for_registration"])


@tg_bot.message_handler(func = lambda message: get_user_by_id(message.chat.id) is not None, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, "В разработке! :)")


def get_telegram_bot():
    return tg_bot
