import config
import logging


formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

logger = setup_logger(
    config.PROJECT_NAME,
    f'logfile_{config.PROJECT_NAME}.log',
    level=logging.WARNING
)

hr_logger = setup_logger(
    'human_readable',
    f'logfile_human_readable.log',
    level=logging.INFO
)
