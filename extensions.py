import telebot
import requests
import json
import re


class BotTelegramCurrency(telebot.TeleBot):
    def __init__(self, token, **kw):
        telebot.TeleBot.__init__(self, token, **kw)
        self.token = token
        self.data = Currency()

        @self.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            whitespace = '\n'
            self.reply_to(message, f"Привет, {message.from_user.first_name}, меня зовут Виктор Россвикович! "
                                   f"Я умею считать курсы валют! Для этого напиши мне сообщение в виде:{whitespace}"
                                   f"<имя валюты, цену которой ты хочет узнать><пробел>{whitespace}"
                                   f"<имя валюты, в которой надо узнать цену первой валюты><пробел>{whitespace}"
                                   f"<количество первой валюты>.{whitespace}"
                                   f"Чтобы посмотреть доступные валюты - напиши:{whitespace}"
                                   f"/values{whitespace}")

        @self.message_handler(commands=['values'])
        def show_currency(message):
            whitespace = '\n'
            list_currency = []
            for value in self.data.arr_currency.values():
                list_currency.append(value)
            self.reply_to(message, f"Я умею считать следующие валюты:{whitespace}"
                                   f"{whitespace.join(list_currency)}")

        @self.message_handler(content_types=['text', ])
        def send_price(message: telebot.types.Message):
            list_info = message.text.strip().split()
            if len(list_info) == 3:
                self.data.set_base = list_info[0]
                self.data.set_quote = list_info[1]
                self.data.set_amount = list_info[2]
                self.reply_to(message, f"{self.data.answer}")

    def run(self):
        self.polling(none_stop=True)


class Currency:
    def __init__(self):
        self.API_address = 'https://min-api.cryptocompare.com/data/price?'
        self.base = None
        self.quote = None
        self.amount = 1
        self.arr_currency = {'RUB': 'РУБЛЬ', 'USD': 'ДОЛЛАР', 'EUR': 'ЕВРО', 'BTC': 'БИТКОИН'}
        self.error = []

    @property
    def answer(self):
        whitespace = '\n'
        if len(self.error) == 0:
            answer = self.get_price(self.base, self.quote, self.amount)
            self.clear()
            return answer
        else:
            answer = whitespace.join(self.error)
            self.clear()
            return answer

    @property
    def set_base(self):
        return self.base

    @set_base.setter
    def set_base(self, base):
        try:
            self.base = self.search_key(base)
            if ''.join(self.base) == '':
                raise APIException(f'Я не знаю что такое {base}...Расскажете мне об этом?')
        except APIException as e:
            self.error.append(str(e))

    @property
    def set_quote(self):
        return self.quote

    @set_quote.setter
    def set_quote(self, quote):
        try:
            self.quote = self.search_key(quote)
            if ''.join(self.quote) == '':
                raise APIException(f'{quote} cтранная какая-то Валюта...Пойду погуглю о ней')
        except APIException as e:
            self.error.append(str(e))

    @property
    def set_amount(self):
        return self.amount

    @set_amount.setter
    def set_amount(self, amount):
        try:
            self.amount = int(amount)
        except ValueError as e:
            self.error.append('Я наверное плохо рассказал, как у нас тут всё работает. Сначала валюта, '
                              'которую переводим, потом в какую переводим, '
                              'а затем какое количество в виде ЦЕЛОГО ЧИСЛА)))')

    def search_key(self, search_string):
        search = re.sub('\W+', '', search_string).upper()
        return ''.join([key for key, val in self.arr_currency.items() if search in val])

    def clear(self):
        self.base = None
        self.quote = None
        self.amount = 1
        self.error = []

    @staticmethod
    def get_price(base, quote, amount):
        try:
            price = requests.get(
                f'https://min-api.cryptocompare.com/data/price?fsym={base}&tsyms={quote}')
            if price.status_code == 200:
                answer = f"{str('{:.2f}'.format(float(json.loads(price.content)[quote]) * amount))} " \
                         f"{quote}"
                return answer
            else:
                raise APIException('Что-то наши аналитики не отвечают, может устали, попробуйте позже)))')
        except APIException as e:
            print(e)


class APIException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'Ниче не понял..., {0} '.format(self.message)
        else:
            return 'Что-то я летаю в облаках, повторите, пожалуйста!'
