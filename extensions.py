import telebot
import requests
import json


class BotTelegramCurrency(telebot.TeleBot):
    def __init__(self, token, **kw):
        telebot.TeleBot.__init__(self, token, **kw)
        self.token = token
        self.data = Currency()

        @self.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            whitespace = '\n'
            self.reply_to(message, f"Привет, {message.from_user.first_name}, меня зовут Анжела! "
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
            for dict_ in self.data.arr_currency:
                for key in dict_.keys():
                    list_currency.append(dict_[key])
            self.reply_to(message, f"Я умею считать следующие валюты:{whitespace}"
                                   f"{whitespace.join(list_currency)}")

        @self.message_handler(content_types=['text', ])
        def send_price(message: telebot.types.Message):
            list_info = message.text.strip().split()
            self.data.set_base = list_info[0]
            self.data.set_quote = list_info[1]
            self.data.set_amount = list_info[2]
            print(self.data.base, self.data.quote, self.data.amount)
            self.reply_to(message, f"{self.data.get_price}")

    def run(self):
        self.polling(none_stop=True)


class Currency:
    def __init__(self):
        self.API_address = 'https://min-api.cryptocompare.com/data/price?'
        self.base = None
        self.quote = None
        self.amount = 1
        self.arr_currency = [{'RUB': 'Рубль'}, {'USD': 'Доллар'}, {'EUR': 'Евро'}, {'BTC': 'Биткоин'}]

    @property
    def get_price(self):
        try:
            price = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={self.base}&tsyms={self.quote}')
            if price.status_code == 200:
                return str('{:.2f}'.format(float(json.loads(price.content)[self.quote]) * self.amount))
            else:
                raise APIException('Что-то наши аналитики не отвечают, может устали, попробуйте позже)))')
        except APIException as e:
            print(e)

    @property
    def set_base(self):
        return self.base

    @set_base.setter
    def set_base(self, base):
        try:
            for d in self.arr_currency:
                for currency_id, currency_str in d.items():
                    if base == currency_str:
                        self.base = currency_id
            if self.base is None:
                raise APIException('Я не знаю такой Валюты...Расскажете мне о ней?')
        except APIException as e:
            print(e)

    @property
    def set_quote(self):
        return self.quote

    @set_quote.setter
    def set_quote(self, quote):
        try:
            for d in self.arr_currency:
                for currency_id, currency_str in d.items():
                    if quote == currency_str:
                        self.quote = currency_id
            if self.quote is None:
                raise APIException('Я не знаю такой Валюты...Расскажете мне о ней?')
        except APIException as e:
            print(e)

    @property
    def set_amount(self):
        return self.amount

    @set_amount.setter
    def set_amount(self, amount):
        try:
            self.amount = int(amount)
        except ValueError as e:
            print('Я наверное плохо объяснила, как у нас тут всё работает. Сначала валюта, которую переводим, '
                  'потом в какую переводим, а затем сколько  - в виде ЦЕЛОГО ЧИСЛА)))')


class APIException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'Ниче не поняла..., {0} '.format(self.message)
        else:
            return 'Что-то я летаю в облаках, повторите, пожалуйста!'
