import logging
import telebot
from telebot import types
from vk.vk_auth import request_vk_auth_code
from sql.database import apply_db_changes
from sql.user.user import user_table, employee_table, customer_table

from meta.loader import TELEGRAM_TOKEN
from meta.loader import load_messages, load_buttons, load_photos

from telebot import custom_filters
from geocode.geo_patcher import get_address_from_coordinates

messages_templates = load_messages()
buttons = load_buttons()
keyboard_hider = types.ReplyKeyboardRemove()
images = load_photos()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

tg_bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded = False)


def create_inline_keyboard(data: dict):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    for key in data:
        markup.add(types.InlineKeyboardButton(text = key, callback_data = data[key]))
    return markup


def create_reply_keyboard(data: list):
    markup = types.ReplyKeyboardMarkup(row_width = 2)
    for button in data:
        markup.add(types.KeyboardButton(text = button))
    return markup


def create_main_buttons_reply_markup():
    button_1 = types.KeyboardButton(buttons["main_buttons"][0])
    button_2 = types.KeyboardButton(buttons["main_buttons"][1])
    button_3 = types.KeyboardButton(buttons["main_buttons"][2])
    button_4 = types.KeyboardButton(buttons["main_buttons"][3])
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    markup.add(button_1, button_2)
    markup.add(button_3, button_4)
    return markup


@tg_bot.message_handler(commands = ['start'])
def command_send_welcome(message):
    if not is_unregistered_user(message.chat.id):
        message_to_user = messages_templates["registered_user"]["start_message"]

        tg_bot.send_photo(message.chat.id, photo = images["buttons_helper"], caption = message_to_user, reply_markup
        = create_main_buttons_reply_markup())
    else:
        message_to_user, keyboard = messages_templates["unregistered_user"]["start_message"], create_inline_keyboard(
            buttons["reg"])
        tg_bot.send_photo(message.chat.id, photo = images["welcome"], caption = message_to_user,
                          reply_markup = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_reg")
def callback_reg(call):
    command_register(call.message)


def send_data_warning(message):
    tg_bot.edit_message_media(chat_id = message.chat.id, message_id = message.message_id,
                              media = types.InputMediaPhoto(images["reg_start"],
                                                            caption = messages_templates["unregistered_user"][
                                                                "data_collection_warning"]))


def is_unregistered_user(tg_id):
    return (user_table.get_user_by_tg_id(tg_id) is None) or (user_table.get_user_by_tg_id(tg_id).finished_reg is False)


def command_register(message):
    '''
    Register function.
    '''
    # Send next step: name
    if is_unregistered_user(message.chat.id):
        user_table.add_new_user(message.chat.id)
        apply_db_changes()
    send_data_warning(message)
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["age_reg_step"], reply_markup =
    create_inline_keyboard(buttons["age_reg_buttons"]))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_age_back")
def callback_return_to_age_step(call):
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                             text = messages_templates["unregistered_user"]["age_reg_step"])
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
    = create_inline_keyboard(buttons["age_reg_buttons"]))


@tg_bot.callback_query_handler(func = lambda call: call.data in buttons["age_reg_buttons"].values())
def callback_age_handler(call):
    tg_bot.set_state(call.from_user.id, "registering")
    user = user_table.get_user_by_tg_id(call.from_user.id)
    # Gets text from button
    user.age = list(buttons["age_reg_buttons"].keys())[list(buttons["age_reg_buttons"].values()).index(call.data)]
    apply_db_changes()
    tg_bot.delete_message(chat_id = call.from_user.id, message_id = call.message.message_id)

    tg_bot.send_photo(call.from_user.id, photo = images["geo_send_help"], caption = messages_templates[
        "unregistered_user"]["city_reg_step"])
    tg_bot.set_state(call.from_user.id, "get_city")


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_city_back")
def callback_return_to_city_step(call):
    tg_bot.delete_message(chat_id = call.from_user.id, message_id = call.message.message_id)
    tg_bot.send_photo(call.from_user.id, photo = images["geo_send_help"], caption = messages_templates[
        "unregistered_user"]["city_reg_step"])
    tg_bot.set_state(call.from_user.id, "get_city")


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_accept_city")
def callback_accept_city_step(call):
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                             text = messages_templates["unregistered_user"]["salary_reg_step"])
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id,
                                     reply_markup = create_inline_keyboard(buttons["salary_reg_buttons"]))
    tg_bot.set_state(call.from_user.id, "get_salary")


@tg_bot.message_handler(state = "get_city", content_types = ["location"])
def process_city_step(message):
    user = user_table.get_user_by_tg_id(message.from_user.id)
    user.city_longitude, user.city_latitude = message.location.longitude, message.location.latitude

    address = get_address_from_coordinates(f"{user.city_longitude},{user.city_latitude}")
    if address == "error":
        tg_bot.send_message(message.chat.id, "Упс! Что-то не так с координатами, проверь их и попробуй ещё раз!",
                            reply_markup = create_inline_keyboard(buttons["city_error_button"]))
        return
    user.city_name = address
    apply_db_changes()
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["city_get_data"].format(address),
                        reply_markup = create_inline_keyboard(buttons["city_data_buttons"]))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_salary_back")
def callback_return_to_age_step(call):
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                             text = messages_templates["unregistered_user"]["salary_reg_step"])
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
    = create_inline_keyboard(buttons["salary_reg_buttons"]))


@tg_bot.callback_query_handler(func = lambda call: call.data in buttons["salary_reg_buttons"].values())
def callback_salary_step(call):
    user = user_table.get_user_by_tg_id(call.from_user.id)
    user.salary = call.data
    apply_db_changes()

    finish_registration(call.message)


@tg_bot.callback_query_handler(func = lambda call: call.data in buttons["read_faq_after_reg"].values())
def handle_callback_faq(call):
    if call.data == "cd_faq":
        tg_bot.answer_callback_query(call.id, "Прочитать FAQ")
        tg_bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                 text = messages_templates["reg_faq"])
        tg_bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                         reply_markup = create_inline_keyboard(buttons["have_read_faq"]))
    elif call.data == "cd_faq_cancel":
        tg_bot.answer_callback_query(call.id, "Не читать FAQ")
        keyboard = gen_markup_for_vk_auth(call.from_user.id)
        keyboard.add(types.InlineKeyboardButton("📕 Я передумал! Хочу прочитать FAQ", callback_data = "cd_faq"))
        keyboard.add(types.InlineKeyboardButton("🕔 Привязать позже", callback_data = "cd_vk_auth_cancel"))
        tg_bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                 text = messages_templates["vk"]["vk_auth_message"])

        tg_bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                         reply_markup = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_vk_back")
def callback_return_to_vk_step(call):
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                             text = messages_templates["vk"]["vk_auth_message"])
    keyboard = gen_markup_for_vk_auth(call.from_user.id)
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data = "cd_salary_back"))
    keyboard.add(types.InlineKeyboardButton("Привязать позже", callback_data = "cd_vk_auth_cancel"))
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
    = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_vk_auth")
def callback_vk_auth(call):
    keyboard = gen_markup_for_vk_auth(call.from_user.id)
    keyboard.add(types.InlineKeyboardButton("Привяжу позже", callback_data = "cd_vk_auth_cancel"))
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                             text = messages_templates["vk"]["vk_not_authorized"])
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
    = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_vk_reauth")
def callback_vk_auth(call):
    user = user_table.get_user_by_tg_id(call.from_user.id)
    if user.vk_access_token is not None:
        tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                                 text = messages_templates["vk"]["vk_re_register"])
        tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
        = create_inline_keyboard(buttons["vk_re_auth_buttons"]))
        return
    keyboard = gen_markup_for_vk_auth(call.from_user.id)
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data = "cd_profile"))
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                             text = messages_templates["vk"]["vk_not_authorized"])
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
    = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_vk_auth_cancel")
def cancel_vk_auth(call):
    tg_bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                             text = messages_templates["vk"]["vk_cancel_auth"])
    tg_bot.send_photo(call.from_user.id, photo = images["buttons_helper"], caption = messages_templates[
        "registered_user"]["start_message"])
    tg_bot.send_message(call.from_user.id, messages_templates["unregistered_user"]["after_faq_message"], reply_markup
    = create_main_buttons_reply_markup())
    choose_role(call.message)


def after_vk_auth_in_server(tg_id):
    tg_bot.send_message(tg_id, get_vk_profile_info(tg_id), reply_markup = create_inline_keyboard(
        buttons["vk_auth_confirmation_buttons"]))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_accept_vk")
def callback_accept_vk_account(call):
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                             text = messages_templates["unregistered_user"]["after_faq_message"])
    choose_role(call.message)


def finish_registration(message):
    user = user_table.get_user_by_tg_id(message.chat.id)
    if user.finished_reg:
        tg_bot.edit_message_text(chat_id = message.chat.id, message_id = message.message_id,
                                 text = messages_templates["registered_user"]["re_register_finish"] +
                                        messages_templates["registered_user"]["registration_common_data"].format(
                                            user.id,
                                            user.age,
                                            user.city_name,
                                            user.registered_date))
        return
    user.finished_reg = True
    apply_db_changes()
    tg_bot.delete_message(chat_id = message.chat.id, message_id = message.message_id)
    message = tg_bot.send_message(message.chat.id, messages_templates["registered_user"]["registration_common_data"].format(
        user.id,
        user.age,
        user.city_name,
        user.registered_date))
    # tg_bot.edit_message_reply_markup(chat_id = message.chat.id, message_id = message.message_id, reply_markup =
    # create_reply_keyboard(buttons["main_buttons"]))
    show_faq_after_req(message)


def show_faq_after_req(message):
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["finish_registration"],
                        reply_markup = create_inline_keyboard(buttons["read_faq_after_reg"]))


# Handle all other messages from unregistered users
@tg_bot.message_handler(func = lambda message: is_unregistered_user(message.chat.id))
def unregistered_user_reply(message):
    tg_bot.send_message(message.chat.id, messages_templates["unregistered_user"]["request_for_registration"],
                        reply_markup = create_inline_keyboard(buttons["reg"]))


def choose_role(message):
    tg_bot.send_message(message.chat.id, messages_templates["choose_role"], reply_markup = create_inline_keyboard(
        buttons["choose_type_of_account"]))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_choose_role")
def callback_choose_role(call):
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id,
                             text = messages_templates["choose_role"])
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id,
                                     reply_markup = create_inline_keyboard(
                                         buttons["choose_type_of_account"]))


def get_profile_info(user_id):
    user = user_table.get_user_by_id(user_id)
    employee = employee_table.get_employee_by_id(user.id)
    customer = customer_table.get_customer_by_id(user.id)
    vk_data = get_vk_profile_info(user.tg_id)
    if employee is None:
        employee_data = messages_templates["employee"]["no_profile"]
    else:
        employee_data = str(employee.balance) + " PTF"
    if customer is None:
        customer_data = messages_templates["customer"]["no_profile"]
    else:
        customer_data = str(customer.balance) + " PTF"
    common_data = messages_templates["registered_user"]["profile_common_data"].format(user.id, user.age,
                                                                                      user.city_name,
                                                                                      user.registered_date,
                                                                                      employee_data,
                                                                                      customer_data, vk_data)
    return common_data



def get_employee_profile_info(user_id):
    user = user_table.get_user_by_id(user_id)
    employee = employee_table.get_employee_by_id(user_id)
    keyboard = create_inline_keyboard(buttons["employee_profile_buttons"])
    if employee is None:
        return messages_templates["employee"]["no_profile"], keyboard

    message = messages_templates["employee"]["profile"].format(employee.appeals)
    return message, keyboard


def get_customer_profile_info(user_id):
    customer = customer_table.get_customer_by_id(user_id)
    if customer is None:
        return messages_templates["customer"]["no_profile"]
    message = messages_templates["customer"]["profile"].format()
    return message


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_employee")
def switch_to_employee(call):
    user = user_table.get_user_by_tg_id(user_id = call.from_user.id)
    employee = employee_table.get_employee_by_id(user.id)
    if employee is None:
        employee_table.add_employee(user.id)
    employee_data, keyboard = get_employee_profile_info(user.id)
    tg_bot.delete_message(call.message.chat.id, call.message.message_id)
    tg_bot.send_photo(call.message.chat.id, photo = images["employee"], caption = employee_data,
                      reply_markup = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_employee_get_balance")
def callback_get_employee_balance(call):
    user = user_table.get_user_by_tg_id(call.from_user.id)
    employee = employee_table.get_employee_by_id(user.id)
    message_to_user = messages_templates["employee"]["balance"].format(employee.balance)
    keyboard = create_inline_keyboard(buttons["employee_balance_buttons"])
    tg_bot.delete_message(call.message.chat.id, call.message.message_id)
    tg_bot.send_message(call.message.chat.id, message_to_user, reply_markup = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_employee_faq")
def callback_get_employee_faq(call):
    message_to_user = messages_templates["employee"]["faq"]
    keyboard = create_inline_keyboard(buttons["employee_faq_buttons"])
    tg_bot.delete_message(call.message.chat.id, call.message.message_id)
    tg_bot.send_message(call.message.chat.id, message_to_user, reply_markup = keyboard)


def gen_markup_for_vk_auth(tg_id):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton(text = "🔹 VK авторизация", url = request_vk_auth_code(tg_id)))
    return markup


def get_vk_profile_info(tg_id) -> str:
    vk = user_table.get_vk_api(tg_id)
    if vk is None:
        return "Не авторизирован"
    data = vk.users.get()[0]
    return "\nПрофиль: {} {}, \nСсылка: vk.com/id{}".format(data["first_name"], data["last_name"], data["id"])


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_profile")
def callback_profile(call):
    user = user_table.get_user_by_tg_id(call.from_user.id)
    message = get_profile_info(user_id = user.id) + "\nВыберете действие:"
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id, text = message)
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
    = create_inline_keyboard(buttons["profile_buttons"]))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_re_register")
def callback_re_register(call):
    message = messages_templates["registered_user"]["re_register"]
    tg_bot.edit_message_text(chat_id = call.from_user.id, message_id = call.message.message_id, text = message)
    tg_bot.edit_message_reply_markup(chat_id = call.from_user.id, message_id = call.message.message_id, reply_markup
    = create_inline_keyboard(buttons["re_reg_buttons"]))


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_customer")
def callback_switch_to_customer(call):
    user = user_table.get_user_by_tg_id(call.from_user.id)
    customer = customer_table.get_customer_by_id(user.id)
    if customer is None:
        customer_table.add_customer(user.id)
    message = get_customer_profile_info(user.id)
    keyboard = create_inline_keyboard(buttons["customer_profile_buttons"])
    tg_bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id)
    tg_bot.send_photo(call.message.chat.id, photo = images["customer"], caption = message, reply_markup = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_customer_get_balance")
def callback_get_customer_balance(call):
    user = user_table.get_user_by_tg_id(call.from_user.id)
    customer = customer_table.get_customer_by_id(user.id)
    message_to_user = messages_templates["customer"]["balance"].format(customer.balance)
    keyboard = create_inline_keyboard(buttons["customer_balance_buttons"])
    tg_bot.delete_message(chat_id = call.from_user.id, message_id = call.message.message_id)
    tg_bot.send_message(call.from_user.id, message_to_user, reply_markup = keyboard)


@tg_bot.callback_query_handler(func = lambda call: call.data == "cd_customer_faq")
def callback_get_customer_faq(call):
    message_to_user = messages_templates["customer"]["faq"]
    keyboard = create_inline_keyboard(buttons["customer_faq_buttons"])
    tg_bot.delete_message(chat_id = call.from_user.id, message_id = call.message.message_id)
    tg_bot.send_message(call.from_user.id, message_to_user, reply_markup = keyboard)


@tg_bot.message_handler(func = lambda message: message.text == "🏠 Домой")
def reply_home(message):
    tg_bot.send_photo(message.chat.id, photo = images["buttons_helper"], caption = messages_templates[
        "registered_user"]["start_message"])


@tg_bot.message_handler(func = lambda message: message.text == "👤 Мой профиль")
def reply_home(message):
    user = user_table.get_user_by_tg_id(message.chat.id)
    tg_bot.send_message(message.chat.id, get_profile_info(user.id), reply_markup = create_inline_keyboard(
        buttons["profile_buttons"]))


def get_user_balance(user_id):
    user = user_table.get_user_by_id(user_id)
    employee = employee_table.get_employee_by_id(user.id)
    customer = customer_table.get_customer_by_id(user.id)
    if employee is None:
        employee_balance = messages_templates["employee"]["no_profile"]
    else:
        employee_balance = str(employee.balance) + " PTF"
    if customer is None:
        customer_balance = messages_templates["customer"]["no_profile"]
    else:
        customer_balance = str(customer.balance) + " PTF"
    return messages_templates["registered_user"]["common_balance"].format(customer_balance, employee_balance)


@tg_bot.message_handler(func = lambda message: message.text == "💴 Мой баланс")
def reply_home(message):
    user = user_table.get_user_by_tg_id(message.chat.id)
    message_for_user = get_user_balance(user.id)
    tg_bot.send_message(message.chat.id, message_for_user,
                        reply_markup = create_inline_keyboard(buttons["common_balance_buttons"]))


@tg_bot.message_handler(func = lambda message: message.text == "👥 Сменить роль")
def reply_home(message):
    choose_role(message)


@tg_bot.callback_query_handler(func = lambda call: True)
def handle_unregistered_callback(call):
    tg_bot.send_message(call.from_user.id, "В разработке! :)")


@tg_bot.message_handler(func = lambda message: not is_unregistered_user(message.chat.id), content_types = ['text'])
def echo_message(message):
    tg_bot.send_photo(message.chat.id, photo = images["buttons_helper"], caption = "Если пропали кнопки, то нажми на "
                                                                                   "иконку, как на картинке:")


def get_telegram_bot():
    return tg_bot


tg_bot.add_custom_filter(custom_filters.StateFilter(tg_bot))
