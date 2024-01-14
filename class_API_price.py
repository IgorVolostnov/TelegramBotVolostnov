import requests
import json
from APIException import MyCustomError


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
                raise MyCustomError('Что-то наши аналитики не отвечают, может устали, попробуйте позже)))')
        except MyCustomError as e:
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
                raise MyCustomError('Я не знаю такой Валюты...Расскажете мне о ней?')
        except MyCustomError as e:
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
                raise MyCustomError('Я не знаю такой Валюты...Расскажете мне о ней?')
        except MyCustomError as e:
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


r = Currency()
r.add_currency = 'USD'
r.add_currency = 'EUR'
r.add_currency = 'RUB'
r.add_currency = 'BTC'
r.set_base = 'BTC'
r.set_quote = 'RUB'
r.set_amount = 1
print(r.get_price)
