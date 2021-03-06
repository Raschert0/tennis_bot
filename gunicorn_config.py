from config import WEBHOOK_URL_BASE, WEBHOOK_URL_PATH, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, WEBHOOK_PORT, WORKERS
import os


forked = 0


def pre_request(worker, req):
    from logger_settings import logger

    logger.debug('Gunicorn request arrived')


def pre_fork(server, worker):
    global forked
    forked += 1


def post_fork(server, worker):
    if forked == workers:
        from time import sleep
        from telebot import TeleBot
        from config import BOT_TOKEN
        from time import sleep
        from scheduler_controller import schedule_controller
        from logger_settings import hr_logger

        hr_logger.info('Сервіс запущено')
        bot = TeleBot(BOT_TOKEN, threaded=False)
        bot.remove_webhook()
        sleep(1)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                        certificate=open(WEBHOOK_SSL_CERT, 'r'))
        schedule_controller()


accesslog = os.getcwd() + '/access-logs.log'
disable_redirect_access_to_syslog = True
keyfile = WEBHOOK_SSL_PRIV
certfile = WEBHOOK_SSL_CERT
bind = '0.0.0.0:'+str(WEBHOOK_PORT)
workers = WORKERS
worker_class = 'gthread'
