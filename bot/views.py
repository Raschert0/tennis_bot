from flask import Blueprint, request, abort
from telebot import types
from bot.handler import BotHandlers
from config import *
from logger_settings import logger

bot_blueprint = Blueprint('bot', __name__)
bot_handler = BotHandlers(BOT_TOKEN)

@bot_blueprint.route(WEBHOOK_URL_PATH, methods=['POST'])
def web_hook():
    logger.debug('Received new reqeuest')
    if request.headers.get('content-type') == 'application/json':
        logger.debug('Received json')
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot_handler.bot.process_new_updates([update])
        return ''
    else:
        abort(403)
