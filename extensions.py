import logging
import telebot
import requests
import json
import re
import os
import sys
import pyodbc
from threading import Timer
from telebot import types
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, ReadTimeout
from telebot.apihelper import ApiTelegramException
from urllib3.exceptions import ReadTimeoutError

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class BotTelegramCurrency(telebot.TeleBot):
    def __init__(self, token, **kw):
        telebot.TeleBot.__init__(self, token, **kw)
        self.token = token
        self.list_message_photo = None
        self.previous_message = None
        self.current_message = None
        self.keyboard = None
        self.list_amount = {"/1": "1", "/2": "2", "/3": "3", "/4": "4", "/5": "5", "/6": "6", "/7": "7", "/8": "8",
                            "/9": "9", "/0": "0"}
        self.list_emoji_numbers = {1: '1⃣', 2: '2⃣', 3: '3⃣', 4: '4⃣', 5: '5⃣', 6: '6⃣', 7: '7⃣', 8: 'м', 9: '9⃣',
                                   10: '🔟'}
        self.data = Currency()
        self.list_currency = {}
        self.history = []
        self.timer_clean = TimerClean()
        self.timer_clean.parent = self
        self.timer_clean_message = None
        self.conn = None

        @self.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            if message:
                self.timer_clean.start()
                self.previous_message = message
                whitespace = '\n'
                name_user = f'{self.previous_message.from_user.first_name} {self.previous_message.from_user.last_name}'
                self.timer_clean_message = self.show_message(["Новости", "Курсы валют", "Каталог"], 2,
                                                             text_message=self.format_text(f"Привет {name_user} , "
                                                                                           f"меня зовут Виктор "
                                                                                           f"Россвикович!{whitespace}"
                                                                                           f"Выберете, "
                                                                                           f"что Вас интересует: "))
                self.delete_message(self.previous_message.chat.id, self.previous_message.id)
            else:
                pass

        @self.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            if call.message:
                self.timer_clean.start()
                self.timer_clean_message = self.select_message(call.data, call.message)
            else:
                pass

    def run(self):
        try:
            self.infinity_polling(timeout=10, long_polling_timeout=5)
        except (ConnectionError, ReadTimeout, ApiTelegramException, ConnectionResetError, ReadTimeoutError) as e:
            sys.stdout.flush()
            os.execv(sys.argv[0], sys.argv)
        else:
            self.infinity_polling(timeout=10, long_polling_timeout=5)
        self.polling(none_stop=True)

    def select_message(self, text_message, item_message):
        if text_message == "/Новости":
            return self.news(item_message)
        elif text_message == "/Меню":
            return self.menu(item_message)
        elif text_message == "/Курсы валют":
            return self.exchange_rate(text_message, item_message)
        elif text_message in self.list_currency.values() and len(self.history) == 1:
            return self.select_base(text_message, item_message)
        elif text_message in self.list_currency.values() and len(self.history) == 2:
            return self.select_quote(text_message, item_message)
        elif text_message in self.list_amount.keys():
            return self.select_amount(text_message, item_message)
        elif text_message == "/=":
            return self.total(text_message, item_message)
        elif text_message == "/Назад":
            self.history.pop()
            current = self.history.pop()
            self.select_message(current, item_message)
        else:
            return None

    def menu(self, current_message):
        self.history = []
        self.list_currency = {}
        self.previous_message = current_message
        return self.show_message(["Новости", "Курсы валют", "Каталог"], 2,
                                 text_message=self.format_text(f"Выберете, что Вас интересует: "))

    def news(self, current_message):
        whitespace = '\n'
        self.previous_message = current_message
        date_news = f'Ближайшие поступления на склад {self.date_news}🚛🚢🛩:'
        return self.show_message_with_image(self.arr_news,
                                            ["Меню"], 1,
                                            f"{self.format_text(date_news)}{whitespace}"
                                            f"{whitespace.join(self.arr_arrival)}",
                                            heading_photo=self.format_text(
                                                "Новости Московского подразделения Россвик🔥⚡📊"))

    def exchange_rate(self, current_history, current_message):
        whitespace = '\n'
        self.history.append(current_history)
        self.list_currency = {}
        self.previous_message = current_message
        for value in self.data.arr_currency.values():
            self.list_currency[value] = ("/" + value)
        return self.show_message(self.list_currency.keys(), 2,
                                 text_message=f"{self.format_text('Выберете валюту, курс которой хотите узнать:')}"
                                              f"{whitespace}",
                                 return_button=["Меню"])

    def select_base(self, current_history, current_message):
        whitespace = '\n'
        self.history.append(current_history)
        self.previous_message = current_message
        self.data.set_base = current_history
        return self.show_message(self.list_currency.keys(), 2,
                                 f"{self.format_text('Выберете валюту, в которой показать курс:')}{whitespace}",
                                 ["Назад"])

    def select_quote(self, current_history, current_message):
        whitespace = '\n'
        self.history.append(current_history)
        self.previous_message = current_message
        self.data.set_quote = current_history
        return self.show_message(self.list_amount.values(), 3,
                                 f"{self.format_text('Выберете количество валюты:')}{whitespace}", ["Назад"])

    def select_amount(self, current_history, current_message):
        self.history.append(current_history)
        self.previous_message = current_message
        selected_amount = ''
        for i in range(3, len(self.history)):
            selected_amount += self.list_amount[self.history[i]]
        self.data.set_amount = selected_amount
        return self.show_message(self.list_amount.values(), 3,
                                 f"{self.format_text(f'{self.data.base} в {self.data.quote} х {self.data.amount}')}",
                                 ["=", "Назад"])

    def total(self, current_history, current_message):
        self.history.append(current_history)
        self.previous_message = current_message
        current_text = f'{self.data.base} к {self.data.quote} х {self.data.amount} = {self.data.answer}'
        return self.show_message(["Меню"], 1, text_message=self.format_text(current_text), return_button=["Назад"])

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

    def show_message(self, arr_button, column, text_message, return_button=None):
        try:
            button_list = []
            for button in arr_button:
                button_list.append(types.InlineKeyboardButton(text=f"{button}", callback_data=f"/{button}"))
            if self.keyboard:
                if return_button:
                    footer = []
                    for button_ in return_button:
                        footer.append(types.InlineKeyboardButton(text=f"{button_}", callback_data=f"/{button_}"))
                    self.keyboard = types.InlineKeyboardMarkup(
                        self.build_menu(button_list, column, footer_buttons=footer))
                    self.current_message = self.edit_message_text(chat_id=self.previous_message.chat.id,
                                                                  message_id=self.previous_message.id,
                                                                  text=f"{text_message}", reply_markup=self.keyboard,
                                                                  parse_mode='html')
                    self.clean_chat_photo()
                    return self.current_message
                else:
                    self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column))
                    self.current_message = self.edit_message_text(chat_id=self.previous_message.chat.id,
                                                                  message_id=self.previous_message.id,
                                                                  text=f"{text_message}", reply_markup=self.keyboard,
                                                                  parse_mode='html')
                    self.clean_chat_photo()
                    return self.current_message
            else:
                if return_button:
                    footer = []
                    for button_ in return_button:
                        footer.append(types.InlineKeyboardButton(text=f"{button_}", callback_data=f"/{button_}"))
                    self.keyboard = types.InlineKeyboardMarkup(
                        self.build_menu(button_list, column, footer_buttons=footer))
                    self.current_message = self.send_message(chat_id=self.previous_message.chat.id,
                                                             reply_to_message_id=self.previous_message.id,
                                                             text=f"{text_message}", reply_markup=self.keyboard,
                                                             parse_mode='html')
                    self.clean_chat_photo()
                    return self.current_message
                else:
                    self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column))
                    self.current_message = self.send_message(chat_id=self.previous_message.chat.id,
                                                             reply_to_message_id=self.previous_message.id,
                                                             text=f"{text_message}", reply_markup=self.keyboard,
                                                             parse_mode='html')
                    self.clean_chat_photo()
                    return self.current_message
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
            return self.current_message

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
            return self.current_message
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
            return self.current_message

    def clean_chat_with_time(self):
        try:
            if self.list_message_photo:
                list_photo = []
                for message_item in self.list_message_photo:
                    list_photo.append(message_item.id)
                self.delete_messages(self.list_message_photo[0].chat.id, list_photo)
                self.list_message_photo = None
            if self.timer_clean_message:
                self.delete_message(self.timer_clean_message.chat.id, self.timer_clean_message.id)
            self.timer_clean_message = None
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
            for item in footer_buttons:
                menu.append([item])
        return menu

    @staticmethod
    # Функция для оборота переменных для запроса
    def quote(request):
        return f"'{request}'"


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


class TimerClean:
    def __init__(self):
        self._clean_time = 15
        self.t = None
        self.parent = None

    def start(self):
        if self.t is not None:
            self.t.cancel()
            self.t = Timer(self._clean_time, self.clean_chat)
            self.t.start()
        else:
            self.t = Timer(self._clean_time, self.clean_chat)
            self.t.start()

    def clean_chat(self):
        self.parent.clean_chat_with_time()
        self.clean_timer()

    def clean_timer(self):
        self.t = None


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


class TimerError(Exception):
    """Пользовательское исключение, используемое для сообщения об ошибках при использовании класса Timer"""
