from models import Config


def get_config_document() -> Config:
    return Config.objects(config_id='main_config').first() or Config(config_id='main_config').save()
