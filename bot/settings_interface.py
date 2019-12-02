from models import Config
from config import BotConfig


def get_config_document() -> Config:
    return Config.objects(config_id='main_config').first() or Config(config_id='main_config').save()


def get_config():
    return BotConfig
