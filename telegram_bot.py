import logging
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

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard


@tg_bot.message_handler(commands = ['start'])
def send_welcome(message):
    user = get_user_by_id(message.chat.id)
    if user is not None:
        tg_bot.send_message(message.chat.id, messages_templates["registered_user"]["start_message"])
    else:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["start_message"])


@tg_bot.message_handler(commands = ['vk_auth'])
def vk_auth_register(message):
    # if get_vk_token(message.chat.id) is None:
    tg_bot.send_message(message.chat.id, "Vk auth", reply_markup = gen_markup_for_vk_auth(message.chat.id))


# else:
#     tg_bot.send_message(message.chat.id, "You've already connected vk")


@tg_bot.message_handler(commands = ['ping_vk'])
def vk_auth_register(message):
    vk = get_vk_token(message.chat.id)
    data = vk.users.get()
    tg_bot.send_message(message.chat.id, f"Your vk name: {data[0]['first_name']}")


# Handles '/register'
@tg_bot.message_handler(commands = ['register'])
def register(message):
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["registration_start"])
    tg_bot.register_next_step_handler(message, process_name_step)


def gen_markup_age():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(types.InlineKeyboardButton("12-18", callback_data = "cb_12_18"),
               types.InlineKeyboardButton("19-24", callback_data = "cb_19_24"),
               types.InlineKeyboardButton("25-27", callback_data = "cb_25_27"),
               types.InlineKeyboardButton("27+", callback_data = "cb_27_plus"),
               )
    return markup


# TODO: strange names, as commands name...
def process_name_step(message):
    name = message.text
    id = message.chat.id
    user = get_user_by_id(id)
    if user is None:
        user = add_new_user(id)
    user.name = name
    apply_db_changes()
    msg = tg_bot.reply_to(message, messages_templates["unregistered_user"]["registration_age_step"],
                          reply_markup = gen_markup_age())
    tg_bot.register_next_step_handler(msg, complete_registration)


@tg_bot.callback_query_handler(func = lambda call: True)
def callback_query(call):
    user = get_user_by_id(call.id)
    if call.data == "cb_12_18":
        tg_bot.answer_callback_query(call.id, "Возраст: 12-18")
        user.age = "12-18"
    elif call.data == "cb_19_24":
        tg_bot.answer_callback_query(call.id, "Возраст: 19-24")
        user.age = "19-24"
    elif call.data == "cb_25_27":
        tg_bot.answer_callback_query(call.id, "Возраст: 25-27")
        user.age = "25-27"
    elif call.data == "cb_27_plus":
        tg_bot.answer_callback_query(call.id, "Возраст: 27+")
        user.age = "27+"
    apply_db_changes()


def complete_registration(message):
    user = get_user_by_id(message.chat.id)
    tg_bot.send_message(message.chat.id, f"Супер! \n Тебя зовут: {user.name} \n Твой возраст: {user.age}")


# Creates a markup with link to auth url
def gen_markup_for_vk_auth(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton(text = "VK auth", url = request_vk_auth_code(chat_id)))
    return markup


@tg_bot.message_handler(commands = ['help, faq'])
def faq(message):
    tg_bot.send_message(message.chat.id, "Пока в разработке...")


# Handle all other messages from unregistered users
@tg_bot.message_handler(func = lambda message: get_user_by_id(message.chat.id) is None, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, "Register first!")


@tg_bot.message_handler(func = lambda message: get_user_by_id(message.chat.id) is not None, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, "Sorry, now I can't answer for this...")


def get_telegram_bot():
    return tg_bot
