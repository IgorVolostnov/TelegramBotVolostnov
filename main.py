import telebot

if __name__ == '__main__':
    TOKEN = "6401312975:AAG4SgyUP-WQTTPaqDyY1jFPg6wSLwGK-r8"

    bot = telebot.TeleBot(TOKEN)


    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, f"Привет, {message.from_user.first_name}!")


    @bot.message_handler(content_types=['photo', ])
    def send_photo(message: telebot.types.Message):
        bot.reply_to(message, f"Прикольная фотка XDD!")


    bot.polling(none_stop=True)
