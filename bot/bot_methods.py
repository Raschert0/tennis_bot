from models import User, Texts
from bot import bot
import bot.keyboards as keyboards
from datetime import datetime, date, timedelta
import os
from telebot import types
import config
import random
from time import sleep
# from threading import Timer

def get_str_from_date(date):
    return date.strftime('%d.%m.%Y')


def get_date_from_str(date_string):
    return datetime.strptime(date_string, '%d.%m.%Y')

