import telebot
from telebot import types
import requests
import json
import re
import os
import sys
import pyodbc
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, ReadTimeout
from telebot.apihelper import ApiTelegramException
load_dotenv()


class BotTelegramCurrency(telebot.TeleBot):
    def __init__(self, token, **kw):
        telebot.TeleBot.__init__(self, token, **kw)
        self.token = token
        self.list_message_photo = None
        self.previous_message = None
        self.current_message = None
        self.keyboard = None
        self.selected_base = False
        self.selected_amount = None
        self.list_amount = {"1": "/1", "2": "/2", "3": "/3", "4": "/4", "5": "/5", "6": "/6", "7": "/7", "8": "/8",
                            "9": "/9", "0": "/0"}
        self.list_emoji_numbers = {1: '1⃣', 2: '2⃣', 3: '3⃣', 4: '4⃣', 5: '5⃣', 6: '6⃣', 7: '7⃣', 8: 'м', 9: '9⃣', 10: '🔟'}
        self.data = Currency()
        self.list_currency = []
        self.conn = None

        @self.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.previous_message = message
            whitespace = '\n'
            self.show_message(["Новости", "Курсы валют", "Каталог"], 2,
                              text_message=self.format_text(f"Привет, {self.previous_message.from_user.first_name}, "
                                                            f"меня зовут Виктор Россвикович!{whitespace}"
                                                            f"Выберете, что Вас интересует: "))

        @self.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            whitespace = '\n'
            if call.message:
                if call.data == "/Новости":
                    self.previous_message = call.message
                    date_news = f'Ближайшие поступления на склад {self.date_news}🚛🚚🚢🛩🚀:'
                    self.show_message_with_image(self.arr_news,
                                                 ["Меню"], 1,
                                                 f"{self.format_text(date_news)}{whitespace}"
                                                 f"{whitespace.join(self.arr_arrival)}",
                                                 heading_photo=self.format_text(
                                                     "Новости Московского подразделения Россвик🔥⚡📊"))
                elif call.data == "/Меню":
                    self.selected_base = False
                    self.selected_amount = None
                    self.list_currency = []
                    self.previous_message = call.message
                    self.show_message(["Новости", "Курсы валют", "Каталог"], 2,
                                      text_message=self.format_text(f"Выберете, что Вас интересует: "))
                elif call.data == "/Курсы валют":
                    self.selected_base = False
                    self.selected_amount = None
                    self.list_currency = []
                    self.previous_message = call.message
                    list_currency = []
                    for value in self.data.arr_currency.values():
                        list_currency.append(value)
                        self.list_currency.append("/" + value)
                    self.show_message(list_currency, 2,
                                      text_message=f"{self.format_text('Выберете валюту, курс которой хотите узнать:')}"
                                                   f"{whitespace}",
                                      return_button="Назад")
                elif call.data in self.list_currency:
                    self.previous_message = call.message
                    list_currency = []
                    for value in self.data.arr_currency.values():
                        if value == call.data:
                            list_currency.append(self.format_text(value))
                        else:
                            list_currency.append(value)
                    if self.selected_base:
                        self.data.set_quote = call.data
                        self.show_message(self.list_amount.keys(), 3,
                                          f"{self.format_text('Выберете количество валюты:')}{whitespace}", "Назад")
                    else:
                        self.data.set_base = call.data
                        self.selected_base = True
                        self.show_message(list_currency, 2,
                                          f"{self.format_text('Выберете валюту, в которой показать курс:')}{whitespace}",
                                          "Назад")
                elif call.data in self.list_amount.values():
                    self.previous_message = call.message
                    if self.selected_amount:
                        self.selected_amount = str(self.selected_amount) + "".join(call.data.split("/"))
                        self.show_message(self.list_amount.keys(), 3,
                                          f"{self.format_text(f'{self.data.base} к {self.data.quote} х {self.selected_amount}')}",
                                          "=")
                    else:
                        self.selected_amount = "".join(call.data.split("/"))
                        self.show_message(self.list_amount.keys(), 3,
                                          f"{self.format_text(f'{self.data.base} к {self.data.quote} х {self.selected_amount}')}",
                                          "=")
                    self.data.set_amount = self.selected_amount
                elif call.data == "/=":
                    self.previous_message = call.message
                    self.selected_base = False
                    self.show_message(["Меню"], 1,
                                      text_message=f"{self.format_text(f'{self.data.base} к {self.data.quote} х {self.selected_amount} = {self.data.answer}')}",
                                      return_button="Назад")
                elif call.data == "Назад":
                    self.show_message(["Меню"], 1,
                                      f"{self.data.base} к {self.data.quote} х {self.selected_amount} = "
                                      f"{self.data.answer}", return_button="Назад")
                else:
                    pass
            else:
                pass

    def run(self):
        try:
            self.infinity_polling(timeout=10, long_polling_timeout=5)
        except (ConnectionError, ReadTimeout, ApiTelegramException) as e:
            sys.stdout.flush()
            os.execv(sys.argv[0], sys.argv)
        else:
            self.infinity_polling(timeout=10, long_polling_timeout=5)
        self.polling(none_stop=True)

    def execute_sql_news(self):
        with self.conn.cursor() as curs:
            sql_news = f"SELECT DISTINCT [news] FROM [Arrival] "
            curs.execute(sql_news)
            news_list = []
            for item in curs.fetchall():
                if item[0]:
                    news_list.append(item[0])
            return news_list

    @property
    def arr_news(self):
        try:
            connect_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=\\' + f'{os.getenv("CONNECTION")}'
            with pyodbc.connect(connect_string) as self.conn:
                return self.execute_sql_news()
        except pyodbc.Error as error:
            print("Ошибка чтения данных из таблицы", error)
        finally:
            if self.conn:
                self.conn.close()

    def execute_sql_date_news(self):
        with self.conn.cursor() as curs:
            sql_date = f"SELECT DISTINCT [date_arrival] FROM [Arrival] "
            curs.execute(sql_date)
            news_date = curs.fetchone()[0]
            return news_date

    @property
    def date_news(self):
        try:
            connect_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=\\' + f'{os.getenv("CONNECTION")}'
            with pyodbc.connect(connect_string) as self.conn:
                return self.execute_sql_date_news()
        except pyodbc.Error as error:
            print("Ошибка чтения данных из таблицы", error)
        finally:
            if self.conn:
                self.conn.close()

    def execute_sql_arrival(self):
        with self.conn.cursor() as curs:
            sql_arrival = f"SELECT DISTINCT [description] FROM [Arrival] "
            curs.execute(sql_arrival)
            arrival_list = []
            i = 1
            for item in curs.fetchall():
                if item[0]:
                    arrival_list.append(f'{self.list_emoji_numbers[i]} {item[0]}')
                    i += 1
            return arrival_list

    @property
    def arr_arrival(self):
        try:
            connect_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=\\' + f'{os.getenv("CONNECTION")}'
            with pyodbc.connect(connect_string) as self.conn:
                return self.execute_sql_arrival()
        except pyodbc.Error as error:
            print("Ошибка чтения данных из таблицы", error)
        finally:
            if self.conn:
                self.conn.close()

    def clean_chat(self):
        try:
            if self.previous_message:
                self.delete_message(self.previous_message.chat.id, self.previous_message.id)
                self.previous_message = None
        except ApiTelegramException as e:
            print(e)

    def clean_chat_photo(self):
        try:
            if self.list_message_photo:
                list_photo = []
                for message_item in self.list_message_photo:
                    list_photo.append(message_item.id)
                self.delete_messages(self.list_message_photo[0].chat.id, list_photo)
                self.list_message_photo = None
        except ApiTelegramException as e:
            print(e)

    @staticmethod
    def format_text(text_message):
        return f'<b>{text_message}</b>'

    @staticmethod
    def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            menu.append([footer_buttons])
        return menu

    @staticmethod
    # Функция для оборота переменных для запроса
    def quote(request):
        return f"'{request}'"

    def show_message(self, arr_button, column, text_message, return_button=None):
        try:
            button_list = []
            for button in arr_button:
                button_list.append(types.InlineKeyboardButton(text=f"{button}", callback_data=f"/{button}"))
            if self.keyboard:
                if return_button:
                    footer = types.InlineKeyboardButton(text=f"{return_button}", callback_data=f"/{return_button}")
                    self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column, footer_buttons=footer))
                    self.current_message = self.edit_message_text(chat_id=self.previous_message.chat.id,
                                                                  message_id=self.previous_message.id,
                                                                  text=f"{text_message}", reply_markup=self.keyboard,
                                                                  parse_mode='html')
                    self.clean_chat_photo()
                else:
                    self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column))
                    self.current_message = self.edit_message_text(chat_id=self.previous_message.chat.id,
                                                                  message_id=self.previous_message.id,
                                                                  text=f"{text_message}", reply_markup=self.keyboard,
                                                                  parse_mode='html')
                    self.clean_chat_photo()
            else:
                if return_button:
                    footer = types.InlineKeyboardButton(text=f"{return_button}", callback_data=f"/{return_button}")
                    self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column,
                                                                               footer_buttons=footer))
                    self.current_message = self.send_message(chat_id=self.previous_message.chat.id,
                                                             reply_to_message_id=self.previous_message.id,
                                                             text=f"{text_message}", reply_markup=self.keyboard,
                                                             parse_mode='html')
                    self.clean_chat_photo()
                else:
                    self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column))
                    self.current_message = self.send_message(chat_id=self.previous_message.chat.id,
                                                             reply_to_message_id=self.previous_message.id,
                                                             text=f"{text_message}", reply_markup=self.keyboard,
                                                             parse_mode='html')
                    self.clean_chat_photo()
        except ApiTelegramException as e:
            button_list = []
            for button in arr_button:
                button_list.append(types.InlineKeyboardButton(text=f"{button}", callback_data=f"/{button}"))
            self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column))
            self.current_message = self.send_message(chat_id=self.previous_message.chat.id,
                                                     reply_to_message_id=self.previous_message.id,
                                                     text=f"{text_message}", reply_markup=self.keyboard,
                                                     parse_mode='html')
            self.clean_chat_photo()

    def show_message_with_image(self, arr_url, arr_button, column, text_message, heading_photo, return_button=None):
        media_group = []
        button_list = []
        for button in arr_button:
            button_list.append(types.InlineKeyboardButton(text=f"{button}", callback_data=f"/{button}"))
        for number, url in enumerate(arr_url):
            if number == 0:
                media_group.append(types.InputMediaPhoto(media=url, caption=f"{heading_photo}", parse_mode='html'))
            else:
                media_group.append(types.InputMediaPhoto(media=url))
        if return_button:
            footer = types.InlineKeyboardButton(text=f"{return_button}", callback_data=f"/{return_button}")
            self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column, footer_buttons=footer))
            self.list_message_photo = self.send_media_group(chat_id=self.previous_message.chat.id,
                                                            reply_to_message_id=self.previous_message.id,
                                                            media=media_group)
            self.clean_chat()
            self.current_message = self.send_message(chat_id=self.list_message_photo[0].chat.id,
                                                     reply_to_message_id=self.list_message_photo[0].id,
                                                     text=f"{text_message}", reply_markup=self.keyboard,
                                                     parse_mode='html')
        else:
            self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column))
            self.list_message_photo = self.send_media_group(chat_id=self.previous_message.chat.id,
                                                            reply_to_message_id=self.previous_message.id,
                                                            media=media_group)
            self.clean_chat()
            self.current_message = self.send_message(chat_id=self.list_message_photo[0].chat.id,
                                                     reply_to_message_id=self.list_message_photo[0].id,
                                                     text=f"{text_message}", reply_markup=self.keyboard,
                                                     parse_mode='html')


class Currency:
    def __init__(self):
        self.API_address = 'https://min-api.cryptocompare.com/data/price?'
        self.base = None
        self.quote = None
        self.amount = ""
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
