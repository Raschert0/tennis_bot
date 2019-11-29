from models import Localization

#universal_lang = 'ww'

LANGUAGES_DICTIONARY = {
    'uk': {
        'welcome_msg': 'Вітаю, {}!',
        'menu_msg': 'Меню',
        'use_keyboard_msg': 'Використовуйте, будь ласка, віртуальну клавіатуру!',
        'message_type_not_supported_msg': 'Цей тип повідомлень не підтримується',

        'level_str': 'Рівень',
    }
    #,
    #universal_lang: {
    #    'select_your_lang_msg': 'Оберіть бажану мову інтерфейсу\nВыберите желаемый язык интерфейса',
    #    'lang_ukr_btn': 'Українська',
    #    'lang_ru_btn': 'Русский',
    #    'welcome_msg': 'Вітаю/добро пожаловать, {}'
    #}
}


def create_translation():
    print('===Loading localization===')
    for lang, dict in LANGUAGES_DICTIONARY.items():
        for k, v in dict.items():
            loc = Localization.objects(str_token=k, language=lang).first()
            if loc is None:
                print('Loaded {} key for {} language'.format(k, lang))
                Localization(
                    str_token=k,
                    language=lang,
                    translation=v
                ).save()
    print('===Localization loading finished===')


def get_translation_for(token):
    return __get_translation_for('uk', token)


def __get_translation_for(language, token):
    loc = Localization.objects(str_token=token, language=language).first()
    if loc is not None:
        return loc.translation.strip()
    raise ValueError('Could not find translation for {} ({})'.format(token, language))


def update_translation_for(language, token, new_value):
    loc = Localization.objects(str_token=token, language=language).first()
    if loc is None:
        Localization(
            str_token=token,
            language=language,
            translation=new_value.strip(),
        ).save()
    else:
        loc.translation = new_value.strip()
        loc.save()
