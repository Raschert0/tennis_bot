from config import WEBHOOK_URL_BASE, WEBHOOK_URL_PATH, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, WEBHOOK_PORT, WORKERS
import os


forked = 0


def pre_fork(server, worker):
    global forked
    forked += 1


def post_fork(server, worker):
    if forked == workers:
        from time import sleep
        from telebot import TeleBot
        from config import BOT_TOKEN
        from time import sleep

        bot = TeleBot(BOT_TOKEN, threaded=False)
        bot.remove_webhook()
        sleep(1)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                        certificate=open(WEBHOOK_SSL_CERT, 'r'))


accesslog = os.getcwd() + '/access-logs.log'
disable_redirect_access_to_syslog = True
keyfile = WEBHOOK_SSL_PRIV
certfile = WEBHOOK_SSL_CERT
bind = '0.0.0.0:'+str(WEBHOOK_PORT)
workers = WORKERS
worker_class = 'eventlet'
