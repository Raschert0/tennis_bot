import csv
from datetime import datetime
from time import sleep

import telebot
from telebot import types

import config
from models import User

bot = telebot.TeleBot(config.BOT_TOKEN, threaded=False)

def get_date_from_str(date_string):
    return datetime.strptime(date_string, '%d.%m.%Y')


def send_messages(message, param):
    if param == 'all':
        users = User.objects()
    elif param == 'paid':
        users = User.objects(paid_service=True)
    else:
        users = User.objects(paid_service=False)

    amount = users.count()

    if message.url and message.url_text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton(text=message.url_text, url=message.url))
    else:
        keyboard = None

    photo = message.image.read()

    for user in users[:1000]:
        try:
            if photo:
                if keyboard is not None:
                    last_message = bot.send_photo(user.user_id,
                                                  photo,
                                                  caption=message.text,
                                                  reply_markup=keyboard)
                else:
                    last_message = bot.send_photo(user.user_id,
                                                  photo,
                                                  caption=message.text)
                photo = last_message.photo[-1].file_id
            elif keyboard is not None:
                last_message = bot.send_message(user.user_id,
                                                message.text,
                                                reply_markup=keyboard)
            else:
                last_message = bot.send_message(user.user_id,
                                                message.text)

        except:
            print(f'{user} blocked this bot')

    if amount > 1000:
        for thousand in range(1, amount // 1000 + 1):
            sleep(60)
            for user in users[thousand * 1000:(thousand + 1) * 1000]:
                try:
                    if photo:
                        if keyboard is not None:
                            bot.send_photo(user.user_id, photo, caption=message.text, reply_markup=keyboard)
                        else:
                            bot.send_photo(user.user_id, photo, caption=message.text)
                    else:
                        if keyboard is not None:
                            bot.send_message(user.user_id, message.text, reply_markup=keyboard)
                        else:
                            bot.send_message(user.user_id, message.text)
                except:
                    print(f'{user} blocked this bot')


def download_user_table():
    with open('users.csv', mode='w') as csv_file:
        fieldnames = ['user_id', 'username', 'first_name', 'authorised', 'deleted', 'birth_date',
                      'town', 'area', 'areas', 'area_details', 'position', 'find_text', 'abilities',
                      'info', 'link', 'company_name', 'phone_number', 'marks']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for user in User.objects():
            user_dict = {key: value for key, value in user.to_mongo().items() if key in fieldnames}
            writer.writerow(user_dict)


def get_str_from_date(date):
    return date.strftime('%d.%m.%Y')
