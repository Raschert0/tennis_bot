BOT_TOKEN = 'x'

PROJECT_NAME = 'tennis_bot'

WEBHOOK_HOST = 'x' # your ip adress
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (BOT_TOKEN)
WORKERS = 1

STATES_HISTORY_LEN = 15

try:
    import os, time
    os.environ['TZ'] = 'Europe/Kiev'
    time.tzset()
except AttributeError:
    pass
