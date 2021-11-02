import logging
import telebot
from telebot import types
from vk_auth import request_vk_auth_code
from sql.database import db, apply_db_changes
from sql.user.user import user_table, employee_table, customer_table

from loader import TELEGRAM_TOKEN
from loader import load_messages, load_buttons

from telebot import custom_filters

messages_templates = load_messages()
buttons = load_buttons()
keyboard_hider = types.ReplyKeyboardRemove()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

tg_bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded = False)


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
def command_send_welcome(message):
    user = user_table.get_user_by_tg_id(message.chat.id)
    if user is not None:
        message_to_user, keyboard = messages_templates["registered_user"]["start_message"], create_inline_keyboard(
            buttons["start_buttons"])
    else:
        message_to_user, keyboard = messages_templates["unregistered_user"]["start_message"], create_inline_keyboard(
            buttons["reg"])
    tg_bot.send_message(message.chat.id, message_to_user, reply_markup = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_reg")
def command_register(call):
    '''
    Register function.
    '''
    message = call.message
    # Send next step: name
    if user_table.get_user_by_tg_id(message.chat.id) is None:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["registration_start"],
                            reply_markup = create_reply_keyboard(buttons["ages"]))
        tg_bot.set_state(message.chat.id, "get_age")
    else:
        tg_bot.send_message(message.chat.id, messages_templates["registered_user"]["re_register"],
                            reply_markup = create_inline_keyboard(buttons["re_register"]))


@tg_bot.message_handler(state = "get_age")
def process_age_step(message):
    if message.text not in buttons["ages"]:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["incorrect_input"],
                            reply_markup = keyboard_hider)
        return
    with tg_bot.retrieve_data(message.chat.id) as data:
        data['age'] = message.text

    # Send next step: city
    tg_bot.set_state(message.chat.id, "get_city")
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["city_reg_step"],
                        reply_markup = keyboard_hider)


@tg_bot.message_handler(state = "get_city", content_types=["location"])
def process_city_step(message):
    with tg_bot.retrieve_data(message.chat.id) as data:
        data['city'] = message.text
    # Send next step: salary
    tg_bot.set_state(message.chat.id, "get_salary")
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["salary_reg_step"],
                        reply_markup = create_reply_keyboard(
                            messages_templates["unregistered_user"]["salary_answers"]))


@tg_bot.message_handler(state = "get_salary")
def process_salary_step(message):
    if message.text not in messages_templates["unregistered_user"]["salary_answers"]:
        tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["incorrect_input"],
                            reply_markup = keyboard_hider)
        return
    with tg_bot.retrieve_data(message.chat.id) as data:
        data['salary'] = message.text

    # Next step: finish registration
    process_end_reg(message)


def process_end_reg(message):
    # End registration:
    if user_table.get_user_by_tg_id(message.chat.id) is not None:
        user_table.delete_user(message.chat.id)

    with tg_bot.retrieve_data(message.chat.id) as data:
        user = user_table.add_new_user(tg_id = message.chat.id, age = data["age"], salary = data['salary'], city = data[
            "city"])
    apply_db_changes()
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"][
        "get_data_register_finished"].format(user.age, user.city), reply_markup = keyboard_hider)

    tg_bot.delete_state(message.chat.id)
    # Send inline markup with actions after registration
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["finish_registration"],
                        reply_markup = create_inline_keyboard(buttons["read_faq_after_reg"]))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_faq" or call.data == "cd_faq_cancel")
def handle_callback_faq(call):
    if call.data == "cd_faq":
        tg_bot.answer_callback_query(call.id, "Прочитать FAQ")
        tg_bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                 text = messages_templates["reg_faq"])
        tg_bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                         reply_markup = create_inline_keyboard(buttons["have_read_faq"]))
    elif call.data == "cd_faq_cancel":
        tg_bot.answer_callback_query(call.id, "Не читать FAQ")
        keyboard = create_inline_keyboard(buttons["user_ready"])
        tg_bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                 text = messages_templates["is_user_ready"])
        tg_bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                         reply_markup = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_user_ready")
def user_ready(call):
    tg_bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id)
    tg_bot.send_message(call.from_user.id, messages_templates["is_user_ready"])


@tg_bot.message_handler(commands = ['choose_role'])
def command_choose_role(message):
    tg_bot.send_message(message.chat.id, messages_templates["choose_role"], reply_markup = create_inline_keyboard(
        buttons["choose_type_of_account"]))


def get_employee_profile_info(user_id):
    employee = employee_table.get_employee_by_id(user_id)
    keyboard = create_inline_keyboard(buttons["employee_profile_buttons"])
    if employee.vk_access_token is None:
        keyboard.add(types.InlineKeyboardButton("VK auth", callback_data = "cd_vk_auth"))
    if employee.insta_access_token is None:
        keyboard.add(types.InlineKeyboardButton("Insta auth", callback_data = "cd_vk_auth"))
    message = messages_templates["employee"]["profile"].format(get_vk_profile_info_for_employee(user_id),
                                                               employee.insta_access_token,
                                                               employee.balance)
    return message, keyboard


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_employee")
def switch_to_employee(call):
    user = user_table.get_user_by_tg_id(user_id = call.from_user.id)
    employee = employee_table.get_employee_by_id(user.id)
    if employee is None:
        employee_table.add_employee(id = user.id)
    tg_bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                             text = messages_templates["chosen_role"].format("исполнитель."))
    employee_data, keyboard = get_employee_profile_info(user.id)
    tg_bot.send_message(user.tg_id, employee_data, reply_markup = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_vk_auth")
def callback_vk_auth(call):
    keyboard = gen_markup_for_vk_auth(call.from_user.id)
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                             text = messages_templates["vk"]["vk_not_authorized"])
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
    = keyboard)


def gen_markup_for_vk_auth(tg_id, additional_buttons = None):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton(text = "VK авторизация", url = request_vk_auth_code(tg_id)))
    if additional_buttons is not None:
        for button in additional_buttons:
            markup.add(button)

    return markup


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_vk_auth_cancel")
def cancel_vk_auth(call):
    tg_bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                             text = messages_templates["vk"]["vk_cancel_auth"])


def get_vk_profile_info_for_employee(user_id) -> str:
    vk = employee_table.get_vk_api(user_id)
    if vk is None:
        return "Not authorized"
    data = vk.users.get()[0]
    return "Профиль: {} {}, \nСсылка: vk.com/id{}".format(data["first_name"], data["last_name"], data["id"])


def after_vk_auth_in_server(tg_id):
    user = user_table.get_user_by_tg_id(tg_id)
    tg_bot.send_message(tg_id, get_vk_profile_info_for_employee(user.id), reply_markup = create_inline_keyboard(
        buttons["employee_vk_auth_confirmation"]))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_profile")
def callback_profile(call):
    user = user_table.get_user_by_tg_id(call.from_user.id)
    employee_data, _ = get_employee_profile_info(user.id)
    message = messages_templates["registered_user"]["profile"].format(employee_data, "Профиль заказчика:")
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id, text = message)
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
    = create_inline_keyboard(buttons["profile_buttons"]))


@tg_bot.message_handler(commands = ['help'])
def command_help(message):
    tg_bot.send_message(message.chat.id, messages_templates["help"]["command_help_text"])


@tg_bot.message_handler(commands = ['faq'])
def command_faq(message):
    tg_bot.send_message(message.chat.id, messages_templates["faq"])


# Handle all other messages from unregistered users
@tg_bot.message_handler(func = lambda message: user_table.get_user_by_tg_id(message.chat.id) is None, content_types =
['text'])
def echo_message(message):
    tg_bot.reply_to(message, messages_templates["unregistered_user"]["request_for_registration"])


@tg_bot.message_handler(func = lambda message: user_table.get_user_by_tg_id(message.chat.id) is not None,
                        content_types = [
                            'text'])
def echo_message(message):
    tg_bot.reply_to(message, "В разработке! :)")


def get_telegram_bot():
    return tg_bot


tg_bot.add_custom_filter(custom_filters.StateFilter(tg_bot))
