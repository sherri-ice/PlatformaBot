import telebot
from sql.mysql_connector import Database
from user import User

from consts.loader import TELEGRAM_TOKEN

bot = telebot.TeleBot(TELEGRAM_TOKEN)

database = Database()


@bot.message_handler(commands = ['start'])
def send_welcome(message):
    user = database.get_user_by_id(message.from_user.id)
    if user is not None:
        bot.reply_to(message, "I know you :) How was your day?")
    else:
        database.insert_new_user(User(message.from_user.id, message.from_user.username))
        bot.reply_to(message, "Hey, nice to meet you! :)")


@bot.message_handler(content_types = ['text'])
def error_message(message):
    print("Got unexpected message token")
    bot.reply_to(message, "I'm still in development :c")


if __name__ == '__main__':
    print("Start loggin...")
    bot.infinity_polling()
