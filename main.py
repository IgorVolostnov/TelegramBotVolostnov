import telebot
from dotenv import load_dotenv
import os

if __name__ == '__main__':
    load_dotenv()

    bot = telebot.TeleBot(os.getenv('TOKEN'))


    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, f"Привет, {message.from_user.first_name}!")


    @bot.message_handler(content_types=['photo', ])
    def send_photo(message: telebot.types.Message):
        bot.reply_to(message, f"Прикольная фотка XDD!")


    bot.polling(none_stop=True)
