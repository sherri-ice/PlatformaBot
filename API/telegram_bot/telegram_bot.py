from telegram.ext import Updater

from telegram.ext import CommandHandler


class TelegramBot:
    def __init__(self, token: str):
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher

    def add_handler_for_command(self, handler: CommandHandler):
        self.dispatcher.add_handler(handler)

    def start(self, update, context):
        context.bot.send_message(chat_id = update.effective_chat.id, text = "I'm a bot, please talk to me!")

    def start_polling(self):
        self.add_handler_for_command(CommandHandler('start', self.start))
        self.updater.start_polling()
