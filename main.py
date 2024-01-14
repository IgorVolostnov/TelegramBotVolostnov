import os
from dotenv import load_dotenv
from extensions import BotTelegramCurrency

if __name__ == '__main__':
    load_dotenv()
    bot = BotTelegramCurrency(os.getenv('TOKEN'))
    bot.run()
