import config
import logging


logging.basicConfig(
    filename='logfile_' + config.PROJECT_NAME + '.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(config.PROJECT_NAME)
