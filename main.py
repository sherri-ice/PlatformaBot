from API.telegram_bot.telegram_bot import TelegramBot

from loader import TELEGRAM_TOKEN

bot = TelegramBot(TELEGRAM_TOKEN)
print(TELEGRAM_TOKEN)

bot.start_polling()