import telebot
from file_token import TOKEN

if __name__ == '__main__':

    bot = telebot.TeleBot(TOKEN)


    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, f"Привет, {message.from_user.first_name}!")


    @bot.message_handler(content_types=['photo', ])
    def send_photo(message: telebot.types.Message):
        bot.reply_to(message, f"Прикольная фотка XDD!")


    bot.polling(none_stop=True)
