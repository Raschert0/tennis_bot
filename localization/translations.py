from models import Localization

#universal_lang = 'ww'

LANGUAGES_DICTIONARY = {
    'uk': {
        'welcome_msg': 'Вітаю, {}!',
        'menu_msg': 'Меню',
        'use_keyboard_msg': 'Використовуйте, будь ласка, віртуальну клавіатуру!',
        'message_type_not_supported_msg': 'Цей тип повідомлень не підтримується',

        'authentication_msg': 'Вітаємо в боті.\n'
                              'Вам необхідно пройти процедуру аутентифікації. Просто оберіть себе із списку нижче.\n'
                              'Якщо не можете себе знайти, зв’яжіться, будь ласка, із адміністрацією.',
        'authentication_cannot_find_competitors_msg': 'Не вдалося знайти жодного неавторизованого учасника.\n'
                                                      'Для вирішення цієї проблеми зв’яжіться, будь ласка, з адміністрацією.',
        'authentication_specified_competitor_not_found': 'Такого учасника не знайдено',

        'competitor_record_vanished_msg': 'Не вдалося знайти інформацію про гравця. Необхідно знову пройти процедуру аутентифікації',

        'menu_info_btn': 'Моя інформація',
        'menu_create_challenge_btn': 'Створити челендж',
        'menu_submit_challenge_results_btn': 'Зафіксувати результат челенджа',
        'menu_cancel_challenge_btn': 'Скасувати челендж',
        'menu_cancel_challenge_request_btn': 'Скасувати запит на челендж',
        'menu_reply_to_challenge_request_btn': 'Відповісти на челендж',
        'menu_go_to_vacation_btn': 'Піти у відпустку',
        'menu_got_to_injuiry_btn': 'Взяти лікарняний',
        'menu_end_vacation_btn': 'Закінчити відпустку',
        'menu_end_injuiry_status_btn': 'Вийти з лікарняного',

        'info_status_str': 'Статус',
        'info_level_str': 'Рівень',
        'info_matches_str': 'Матчів',
        'info_wins_str': 'Перемог',
        'info_losses_str': 'Поразок',
        'info_performance_str': 'Performance',
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
