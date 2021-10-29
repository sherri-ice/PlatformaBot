import logging
import time

import telebot
from telebot import types
from vk_auth import request_vk_auth_code
from sql.database import db, apply_db_changes
from sql.user.user import get_user_by_id, add_new_user, get_vk_api

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
        tg_bot.send_message(message.chat.id, messages_templates["registered_user"]["start_message"],
                            reply_markup = keyboard_hider)
    else:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["start_message"],
                            reply_markup = keyboard_hider)


@tg_bot.message_handler(commands = ['vk_auth'])
def vk_auth_register(message):
    # If error while auth appears:
    if get_vk_api(message.chat.id) is None:
        tg_bot.send_message(message.chat.id, messages_templates["vk"]["vk_error_not_found"])
    else:
        # Generate button with link for OAuth VK auth
        tg_bot.send_message(message.chat.id, messages_templates["vk"]["vk_auth_message"],
                            reply_markup = gen_markup_for_vk_auth(
                                message.chat.id))


@tg_bot.message_handler(commands = ['ping_vk'])
def ping_vk(message):
    vk = get_vk_api(message.chat.id)
    if vk is None:
        tg_bot.send_message(message.chat.id, messages_templates["vk"]["vk_not_authorized"])
    else:
        data = vk.users.get()
        # If user is banned or deactivated
        if "deactivated" in data[0]:
            tg_bot.send_message(message.chat.id, messages_templates["vk"]["vk_banned_profile"])
            return
        message_to_user = messages_templates["vk"]["vk_get_user_message"].format(data[0]["first_name"],
                                                                                 data[0]["last_name"], data[0]["id"])
        tg_bot.send_message(message.chat.id, message_to_user)


@tg_bot.message_handler(commands = ['register'])
def register(message):
    # Send next step: name
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["registration_start"])
    tg_bot.register_next_step_handler(message, process_name_step)


# TODO: strange names, as commands name...
def process_name_step(message):
    name = message.text
    user_data = {"name": name}

    # Send next step: age
    markup = types.ReplyKeyboardMarkup()
    markup.row_width = 4
    markup.add(types.KeyboardButton("12-18"),
               types.KeyboardButton("19-24"),
               types.KeyboardButton("25-27"),
               types.KeyboardButton("27+"),
               )
    msg = tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["registration_age_step"],
                              reply_markup = markup)
    tg_bot.register_next_step_handler(msg, process_age_step, user_data)


def process_age_step(message, user_data):
    user_data["age"] = message.text

    # Send next step: city
    msg = tg_bot.send_message(message.chat.id, "В каком городе ты находишься? Будь внимателен при написании имени "
                                               "города!", reply_markup = keyboard_hider)
    tg_bot.register_next_step_handler(msg, process_city_step, user_data)


def process_city_step(message, user_data):
    # TODO: str to low
    user_data["city"] = message.text

    # Send next step: salary
    markup = types.ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.KeyboardButton("Да, я зарабатываю сам и лично \nраспоряжаюсь своими доходами."),
               types.KeyboardButton("Нет, сижу на шее у родителей.")
               )

    msg = tg_bot.send_message(message.chat.id, "Имеешь ли ты личный источник дохода (работа, своё дело)?",
                              reply_markup = markup)
    tg_bot.register_next_step_handler(msg, process_salary_step, user_data)


def process_salary_step(message, user_data):
    # TODO: enum
    user_data["salary"] = message.text

    # End registration:
    user = add_new_user(id = message.chat.id, name = user_data["name"], age = user_data["age"], salary = user_data[
        "salary"], city = user_data["city"])
    apply_db_changes()
    tg_bot.send_message(message.chat.id, f"Супер! \nТебя зовут: {user.name} \nТвой возраст: {user.age} \nГород: "
                                         f"{user.city}",
                        reply_markup = keyboard_hider)
    tg_bot.send_message(message.chat.id, "Для дальнейшей работы понадобится авторизироваться в VK. Пришли /vk_auth.")


# Creates a markup with link to auth url
def gen_markup_for_vk_auth(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton(text = "VK авторизация", url = request_vk_auth_code(chat_id)))
    return markup


@tg_bot.message_handler(commands = ['help'])
def commands_help(message):
    tg_bot.send_message(message.chat.id, messages_templates["help"]["command_help_text"])


@tg_bot.message_handler(commands = ['faq'])
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
