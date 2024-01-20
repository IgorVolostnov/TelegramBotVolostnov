import telebot
from telebot import types
import requests
import json
import re
import os
import sys
from requests.exceptions import ConnectionError, ReadTimeout


class BotTelegramCurrency(telebot.TeleBot):
    def __init__(self, token, **kw):
        telebot.TeleBot.__init__(self, token, **kw)
        self.token = token
        self.keyboard = None
        self.message_with_photo = None
        self.message_with_description = None
        self.data = Currency()
        self.selected_base = False
        self.list_amount = {"1": "/1", "2": "/2", "3": "/3", "4": "/4", "5": "/5", "6": "/6", "7": "/7", "8": "/8",
                            "9": "/9", "0": "/0"}
        self.list_currency = []
        self.selected_amount = ""

        @self.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.delete_photo_from_chat()
            whitespace = '\n'
            self.show_button(message, ["Новости", "Курсы валют", "Каталог"], 2,
                             f"Привет, {message.from_user.first_name}, "
                             f"меня зовут Виктор Россвикович!{whitespace}"
                             f"Выберете, что Вас интересует: ")

        @self.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            # Если сообщение из чата с ботом
            whitespace = '\n'
            if call.message:
                if call.data == "/Новости":
                    self.show_image(call.message,
                                    'https://www.rossvik.moscow/upload/iblock/bf1/oeomn7el57813mqkkz5fxg5p9ue7dvdy/PGA-4500.jpg https://www.rossvik.moscow/upload/iblock/be2/mvmwacgappw4lbt4rcn8rlr64cynek9m/banner-gaykovert-500-na-500.jpg',
                                    ["Меню"], 1,
                                    f"Ближайшие поступления на склад 24.01.2024:{whitespace}"
                                    f"•	Автоподъемник двухстоечный ROSSVIK V2-4L г/п 4.0т, 380В, "
                                    f"электрогидравлический с верхней синхронизацией{whitespace}"
                                    f"•	Станок балансировочный ROSSVIK VT-63, 220В (LCD, лазер, эл. линейка, "
                                    f"УЗ) RAL3020 КРАСНЫЙ{whitespace}"
                                    f"•	Станок балансировочный ROSSVIK VT-63, 220В (LCD, лазер, эл. линейка, "
                                    f"УЗ) RAL7016 СЕРЫЙ{whitespace}"
                                    f"•	Домкрат подкатной S30-2EL, 15-30т, пневмогидравлический, 150-409мм, "
                                    f"38кг, (дополнительные удлинители){whitespace}"
                                    f"•	Домкрат подкатной S40-2EL, 20-40т, пневмогидравлический 150-409мм, "
                                    f"40кг (дополнительные удлинители){whitespace}"
                                    f"•	Гайковерт пневматический RT-5265 1/2', 850Нм, 2,6кг{whitespace}"
                                    f"•	Гайковерт пневматический RT-5880, 1', 4200Нм, 3500об/мин, 6,2бар, "
                                    f"18кг{whitespace}"
                                    f"•	Кран гаражный REMAX HJ2403, 2т. Цвет серый RAL 7040{whitespace}"
                                    f"•	TMHPC-4500C Аппарат высокого давления, 200бар, 14л/мин, 380В, 4,5кВт, "
                                    f"1450об/мин{whitespace}"
                                    f"•	TMHPC-7500C Аппарат высокого давления, 230бар, 16л/мин, 380В, 7,5кВт, "
                                    f"1450об/мин НОВИНКА!{whitespace}"
                                    f"•	Установка для диагности и УЗ очистки форсунок Thinkcar TK-IMT602{whitespace}"
                                    f"•	Пресс гидравлический 10т HJ0802, настольный Цвет серый RAL 7040{whitespace}"
                                    f"•	Пресс гидравлический 12т HJ0803, напольный. Цвет серый RAL 7040{whitespace}"
                                    f"•	Пресс гидравлический 20т HJ0805C, напольный, с педалью. "
                                    f"Цвет серый RAL 7040{whitespace}"
                                    f"•	Установка для обслуживания кондиционеров ROSSVIK АС1800{whitespace}"
                                    f"•	Станок шиномонтажный ROSSVIK V-524, п/автомат, до 24', "
                                    f"380В Цвет синий RAL5005{whitespace}"
                                    f"•	Станок шиномонтажный ROSSVIK V-624, автомат, до 24', "
                                    f"380В Цвет синий RAL5005{whitespace}", "Новости Московского подразделения Россвик")
                elif call.data == "/Меню":
                    self.delete_photo_from_chat()
                    self.selected_base = False
                    self.selected_amount = ""
                    self.list_currency = []
                    self.show_button(call.message, ["Новости", "Курсы валют", "Каталог"], 2,
                                     f"Выберете, что Вас интересует: ")
                elif call.data == "/Курсы валют":
                    self.selected_base = False
                    self.selected_amount = ""
                    self.list_currency = []
                    list_currency = []
                    for value in self.data.arr_currency.values():
                        list_currency.append(value)
                        self.list_currency.append("/" + value)
                    self.show_button(call.message, list_currency, 2,
                                     f"Выберете валюту, курс которой хотите узнать:{whitespace}", return_menu="Меню")
                elif call.data in self.list_currency:
                    list_currency = []
                    for value in self.data.arr_currency.values():
                        list_currency.append(value)
                    if self.selected_base:
                        self.data.set_quote = call.data
                        self.show_button(call.message, self.list_amount.keys(), 3,
                                         f"Выберете количество валюты:{whitespace}",
                                         return_menu="Меню")
                    else:
                        self.data.set_base = call.data
                        self.selected_base = True
                        self.show_button(call.message, list_currency, 2,
                                         f"Выберете валюту, в которой показать курс:{whitespace}",
                                         return_menu="Меню")
                elif call.data in self.list_amount.values():
                    if self.selected_amount is None:
                        self.selected_amount = "".join(call.data.split("/"))
                        self.show_button(call.message, self.list_amount.keys(), 3,
                                         f"{self.data.base} к {self.data.quote} х {self.selected_amount}",
                                         return_menu="=")
                    else:
                        self.selected_amount = str(self.selected_amount) + "".join(call.data.split("/"))
                        self.show_button(call.message, self.list_amount.keys(), 3,
                                         f"{self.data.base} к {self.data.quote} х {self.selected_amount}",
                                         return_menu="=")
                    self.data.set_amount = self.selected_amount
                elif call.data == "/=":
                    self.selected_base = False
                    self.show_button(call.message, ["Новости", "Курсы валют", "Каталог"], 2,
                                     f"{self.data.base} к {self.data.quote} х {self.selected_amount} = "
                                     f"{self.data.answer}", return_menu="Меню")
                else:
                    pass

    def run(self):
        try:
            self.infinity_polling(timeout=10, long_polling_timeout=5)
        except (ConnectionError, ReadTimeout) as e:
            sys.stdout.flush()
            os.execv(sys.argv[0], sys.argv)
        else:
            self.infinity_polling(timeout=10, long_polling_timeout=5)
        self.polling(none_stop=True)

    def delete_photo_from_chat(self):
        if self.message_with_photo:
            list_message_delete = []
            for message_delete in self.message_with_photo:
                list_message_delete.append(message_delete.id)
            self.delete_messages(self.message_with_photo[0].chat.id, list_message_delete)
            self.delete_message(self.message_with_description.chat.id, self.message_with_description.id)
        self.message_with_photo = None
        self.message_with_description = None
        self.keyboard = None

    def show_image(self, message, arr_url, arr_button, column, content_message, name_photo, return_menu=None):
        self.delete_photo_from_chat()
        media_group = []
        button_list = []
        for button in arr_button:
            button_list.append(types.InlineKeyboardButton(text=f"{button}", callback_data=f"/{button}"))
        if return_menu:
            footer = types.InlineKeyboardButton(text=f"{return_menu}", callback_data=f"/{return_menu}")
            self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column, footer_buttons=footer))
        else:
            self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column))
        for number, url in enumerate(arr_url.split()):
            if number == 0:
                media_group.append(types.InputMediaPhoto(media=url, caption=f"{name_photo}"))
            else:
                media_group.append(types.InputMediaPhoto(media=url))
        self.message_with_photo = self.send_media_group(chat_id=message.chat.id, reply_to_message_id=message.id,
                                                        media=media_group)
        self.message_with_description = self.send_message(chat_id=self.message_with_photo[0].chat.id,
                                                          reply_to_message_id=self.message_with_photo[0].id,
                                                          text=f"{content_message}", reply_markup=self.keyboard)

    @staticmethod
    def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            menu.append([footer_buttons])
        return menu

    def show_button(self, message, arr_button, column, contents_menu, return_menu=None):
        button_list = []
        for button in arr_button:
            button_list.append(types.InlineKeyboardButton(text=f"{button}", callback_data=f"/{button}"))
        if self.keyboard:
            if return_menu:
                footer = types.InlineKeyboardButton(text=f"{return_menu}", callback_data=f"/{return_menu}")
                self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column, footer_buttons=footer))
                self.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=f"{contents_menu}",
                                       reply_markup=self.keyboard)
            else:
                self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column))
                self.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=f"{contents_menu}",
                                       reply_markup=self.keyboard)
        else:
            if return_menu:
                footer = types.InlineKeyboardButton(text=f"{return_menu}", callback_data=f"/{return_menu}")
                self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column, footer_buttons=footer))
                self.reply_to(message=message, text=f"{contents_menu}", reply_markup=self.keyboard)
            else:
                self.keyboard = types.InlineKeyboardMarkup(self.build_menu(button_list, column))
                self.reply_to(message=message, text=f"{contents_menu}", reply_markup=self.keyboard)


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
