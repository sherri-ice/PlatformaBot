import logging
import time

import telebot
from telebot import types
from vk_auth import request_vk_auth_code
from sql.database import db, apply_db_changes
from sql.user.user import get_user_by_id, add_new_user, get_vk_api, delete_user

from loader import TELEGRAM_TOKEN
from loader import load_messages

messages_templates = load_messages()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

tg_bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded = False)
keyboard_hider = types.ReplyKeyboardRemove()


def create_inline_keyboard(data: dict):
    markup = types.InlineKeyboardMarkup()
    for key in data:
        markup.add(types.InlineKeyboardButton(text = key, callback_data = data[key]))
    return markup


def create_reply_keyboard(data: list):
    markup = types.ReplyKeyboardMarkup()
    for button in data:
        markup.add(types.KeyboardButton(text = button))
    return markup


@tg_bot.message_handler(commands = ['start'])
def send_welcome(message):
    user = get_user_by_id(message.chat.id)
    if user is not None:
        tg_bot.send_message(message.chat.id, messages_templates["registered_user"]["start_message"],
                            reply_markup = keyboard_hider)
    else:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["start_message"],
                            reply_markup = keyboard_hider)


# Creates a markup with link to auth url
def gen_markup_for_vk_auth(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton(text = "VK авторизация", url = request_vk_auth_code(chat_id)))
    markup.add(types.InlineKeyboardButton(text = "Привяжу потом", callback_data = "cd_vk_auth_cancel"))
    return markup


@tg_bot.message_handler(commands = ['vk_auth'])
def vk_auth_register(message):
    if get_user_by_id(message.chat.id) is None:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["request_for_registration"])
        return
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
    if get_user_by_id(message.chat.id) is None:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["request_for_registration"])
        return
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
    if get_user_by_id(message.chat.id) is None:
        msg = tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["registration_start"],
                                  reply_markup = create_reply_keyboard(["12-18", "19-24", "25-27", "27+"]))
        tg_bot.register_next_step_handler(msg, process_age_step)
    else:
        keyboards = {"Да!": "cd_yes", "Оставить всё как есть": "cd_no"}
        tg_bot.send_message(message.chat.id, messages_templates["registered_user"]["re_register"],
                            reply_markup = create_inline_keyboard(keyboards))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_yes" or call.data == "cd_no")
def handle_callback_re_auth(call):
    if call.data == "cd_yes":
        tg_bot.answer_callback_query(call.id, "Да")
        msg = tg_bot.send_message(call.message.chat.id,
                                  messages_templates["unregistered_user"]["registration_start"], reply_markup
                                  = create_reply_keyboard(["12-18", "19-24", "25-27", "27+"]))
        tg_bot.register_next_step_handler(msg, process_age_step)
    elif call.data == "cd_no":
        tg_bot.answer_callback_query(call.id, "Оставить всё как есть.")
        tg_bot.send_message(call.message.chat.id, "Окей, оставим как есть.")


def process_age_step(message):
    user_data = {"age": message.text}
    if message.text not in ["12-18", "19-24", "25-27", "27+"]:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["incorrect_input"],
                            reply_markup = keyboard_hider)
        return
    # Send next step: city
    msg = tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["city_reg_step"],
                              reply_markup = keyboard_hider)
    tg_bot.register_next_step_handler(msg, process_city_step, user_data)


def process_city_step(message, user_data):
    # TODO: str to low
    user_data["city"] = message.text

    # Send next step: salary
    msg = tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["salary_reg_step"],
                              reply_markup = create_reply_keyboard(
                                  messages_templates["unregistered_user"]["salary_answers"]))
    tg_bot.register_next_step_handler(msg, process_salary_step, user_data)


def process_salary_step(message, user_data):
    # TODO: enum
    user_data["salary"] = message.text
    if message.text not in messages_templates["unregistered_user"]["salary_answers"]:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["incorrect_input"],
                            reply_markup = keyboard_hider)
        return

    # End registration:
    if get_user_by_id(message.chat.id) is not None:
        delete_user(message.chat.id)
    user = add_new_user(id = message.chat.id, age = user_data["age"], salary = user_data[
        "salary"], city = user_data["city"])
    apply_db_changes()
    tg_bot.send_message(message.chat.id, f"Супер! \nТвой возраст: {user.age} \nГород: "
                                         f"{user.city}",
                        reply_markup = keyboard_hider)

    # Send inline markup with actions after registration
    keyboard = {"Прочитать FAQ": "cd_faq", "Разберусь походу": "cd_faq_cancel"}
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["finish_registration"], reply_markup
    = create_inline_keyboard(keyboard))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_faq" or call.data == "cd_faq_cancel")
def handle_callback_faq(call):
    if call.data == "cd_faq":
        tg_bot.answer_callback_query(call.id, "Прочитать FAQ")
        tg_bot.send_message(call.message.chat.id, messages_templates["faq"], reply_markup = create_inline_keyboard(
            {"Понятно! Продолжить": "cd_next"}))
    elif call.data == "cd_faq_cancel":
        tg_bot.answer_callback_query(call.id, "Не читать FAQ")
        keyboard = gen_markup_for_vk_auth(call.message.chat.id)
        keyboard.add(types.InlineKeyboardButton(text = "Я передумал! Хочу прочитать FAQ", callback_data = "cd_faq"))
        tg_bot.send_message(call.message.chat.id, messages_templates["vk"]["vk_auth_message"], reply_markup = keyboard)


@tg_bot.message_handler(commands = ['help'])
def commands_help(message):
    tg_bot.send_message(message.chat.id, messages_templates["help"]["command_help_text"])


@tg_bot.message_handler(commands = ['faq'])
def faq(message):
    tg_bot.send_message(message.chat.id, messages_templates["faq"])


# Handle all other messages from unregistered users
@tg_bot.message_handler(func = lambda message: get_user_by_id(message.chat.id) is None, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, messages_templates["unregistered_user"]["request_for_registration"])


@tg_bot.message_handler(func = lambda message: get_user_by_id(message.chat.id) is not None, content_types = ['text'])
def echo_message(message):
    tg_bot.reply_to(message, "В разработке! :)")


def get_telegram_bot():
    return tg_bot
