import config
import telebot

bot = telebot.TeleBot(config.BOT_TOKEN, threaded=False)
#print(bot.get_me())
