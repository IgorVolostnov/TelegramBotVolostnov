import requests
import json


class Currency:
    def __init__(self):
        self.API_address = 'https://min-api.cryptocompare.com/data/price?'
        self.base = None
        self.quote = None
        self.amount = 1
        self.arr_currency = []

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
            if base in self.arr_currency:
                self.base = base
            else:
                raise APIException('Я не знаю такой Валюты...Расскажете мне о ней?')
        except APIException as e:
            print(e)

    @property
    def set_quote(self):
        return self.quote

    @set_quote.setter
    def set_quote(self, quote):
        try:
            if quote in self.arr_currency:
                self.quote = quote
            else:
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

    @property
    def add_currency(self):
        return self.arr_currency

    @add_currency.setter
    def add_currency(self, currency):
        self.arr_currency.append(currency)


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


r = Currency()
r.add_currency = 'USD'
r.add_currency = 'EUR'
r.add_currency = 'RUB'
r.add_currency = 'BTC'
r.set_base = 'BTC'
r.set_quote = 'RUB'
r.set_amount = 1
print(r.get_price)
