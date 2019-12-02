import argparse

args = None
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tennis bot'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-W',
        '--web-server',
        action='store_true',
        help='run the web-server'
    )
    group.add_argument(
        '-B',
        '--bot',
        action='store_true',
        help='run bot in pooling mode'
    )
    group.add_argument(
        '-H',
        '--web-server-with-hooks',
        action='store_true',
        help='run web-server, scheduler and telegram bot'
    )
    group.add_argument(
        '-S',
        '--scheduler',
        action='store_true',
        help='run scheduler only'
    )
    args = parser.parse_args()

    if args.bot or args.web_server_with_hooks:
        from scheduler_controller import schedule_controller
        schedule_controller()


from time import sleep
from bot.views import bot_blueprint, bot_handler
from admin.views import admin_blueprint, admin, login
from flask import Flask
from config import *
from models import db


app = Flask(PROJECT_NAME)
app.config['MONGODB_DB'] = PROJECT_NAME
app.config['SECRET_KEY'] = b'\x10X\xe6\x1c\xb0\xea\x9a\xbf\xa3\x16\x83\xe8\x0c\x84a\x87'
db.init_app(app)
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
app.register_blueprint(bot_blueprint)
app.register_blueprint(admin_blueprint)
admin.init_app(app)
login.init_app(app)
#create_translation()


if __name__ == "__main__":
    from google_integration.sheets.users import UsersSheet
    from scheduler_controller import schedule_controller

    if not args:
        raise ValueError("Args not found")

    UsersSheet.update_model()
    if args.bot:
        bot_handler.bot.remove_webhook()
        bot_handler.bot.polling(none_stop=True)
    elif args.web_server:
        app.run(debug=True)
    elif args.scheduler:
        schedule_controller()
    elif args.web_server_with_hooks:
        bot_handler.bot.remove_webhook()
        sleep(1)
        bot_handler.bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

        app.run(host=WEBHOOK_LISTEN,
                port=WEBHOOK_PORT,
                ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
                threaded=True
                )
