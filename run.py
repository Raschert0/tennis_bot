from time import sleep
from bot.views import bot_blueprint, bot_handler
from admin.views import admin_blueprint, admin, login
from flask import Flask
from config import *
from models import db
from localization.translations import create_translation
import secrets
import telebot


app = Flask(PROJECT_NAME)
app.config['MONGODB_DB'] = PROJECT_NAME
app.config['SECRET_KEY'] = b'\x10X\xe6\x1c\xb0\xea\x9a\xbf\xa3\x16\x83\xe8\x0c\x84a\x87'
db.init_app(app)
admin.init_app(app)
login.init_app(app)
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
app.register_blueprint(bot_blueprint)
app.register_blueprint(admin_blueprint)
create_translation()

from google_integration.sheets.users import UsersSheet
UsersSheet.update_model()

if __name__ == "__main__":
    # bot_handler.bot.polling(none_stop=True)
    app.run(debug=True, threaded=True)
    # bot_handler.bot.remove_webhook()
    # sleep(1)
    # bot_handler.bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
    #                             certificate=open(WEBHOOK_SSL_CERT, 'r'))
    # app.run(host=WEBHOOK_LISTEN,
    #         port=WEBHOOK_PORT,
    #         ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
    #         threaded=True
    #         )
