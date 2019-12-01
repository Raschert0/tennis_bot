from models import Localization

#universal_lang = 'ww'

LANGUAGES_DICTIONARY = {
    'uk': {
        'welcome_msg': 'Вітаю, {}!',

        'use_keyboard_msg': 'Використовуйте, будь ласка, віртуальну клавіатуру!',
        'message_type_not_supported_msg': 'Цей тип повідомлень не підтримується',

        'authentication_msg': 'Вітаємо в боті.\n'
                              'Вам необхідно пройти процедуру аутентифікації. Просто оберіть себе із списку нижче.\n'
                              'Якщо не можете себе знайти, зв’яжіться, будь ласка, із адміністрацією.',
        'authentication_cannot_find_competitors_msg': 'Не вдалося знайти жодного неавторизованого учасника.\n'
                                                      'Для вирішення цієї проблеми зв’яжіться, будь ласка, з адміністрацією.',
        'authentication_specified_competitor_not_found_clb': 'Такого учасника не знайдено',

        'competitor_record_vanished_msg': 'Не вдалося знайти інформацію про гравця. Необхідно знову пройти процедуру аутентифікації',

        'menu_info_btn': 'Моя інформація',
        'menu_create_challenge_btn': 'Створити челендж',
        'menu_submit_challenge_results_btn': 'Зафіксувати результат челенджа',
        'menu_cancel_challenge_btn': 'Скасувати челендж',
        'menu_cancel_challenge_request_btn': 'Скасувати запит на челендж',
        'menu_reply_to_challenge_request_btn': 'Відповісти на челендж',
        'menu_go_on_vacation_btn': 'Піти у відпустку',
        'menu_go_on_sick_leave_btn': 'Взяти лікарняний',
        'menu_end_vacation_btn': 'Закінчити відпустку',
        'menu_end_sick_leave_btn': 'Вийти з лікарняного',

        'menu_msg': 'Меню',
        'menu_on_sick_leave_start_msg': 'Ви пішли на лікарняний',
        'menu_on_sick_leave_end_msg': 'Ви вийшли з лікарняного',
        'menu_on_vacation_start_msg': 'Ви пішли у відпустку',
        'menu_on_vacation_end_manual_msg': 'Ви вийшли з відпустки',
        'menu_on_vacation_end_msg': 'Ваша відпустка закінчилася',
        'menu_vacation_no_days_left_msg': 'У вас не лишилося днів відпустки в цьому місяці',

        'challenge_send_msg': 'Оберіть зі списку гравця, якому ви хочете надіслати челендж',
        'challenge_send_confirm_msg': 'Підтвердити надсилання челенджа грацю {}?',
        'challenge_no_applicable_competitors_msg': 'Наразі ніхто з доступних Вам гравців не може взяти участь у челенджі',
        'challenge_specified_competitor_not_found_clb': 'Такого учасника не знайдено',
        'challenge_opponent_no_longer_available_msg': 'Обраний гравець наразі недоступний для челенджа',
        'challenge_cannot_send_message_to_opponent_msg': 'Неможливо надіслати челендж гравцю, оскільки він відсутній у Telegram',
        'challenge_you_are_challenged_msg': 'Вам надіслано челендж від <a href="tg://user?id={}">{}</a> (рівень: {}). Кількість днів для того, щоб дати відповідь: {}',
        'challenge_you_are_challenged_passive_msg': 'Вам надіслано челендж від <a href="tg://user?id={}">{}</a> (рівень: {}). Кількість днів для того, щоб дати відповідь: {}\n'
                                                    'Якщо Ви не приймете цей челендж, Вам буде зараховано технічну поразку!',
        'challenge_cancel_msg': 'Ви впевнені, що хочете скасувати цей челендж? Для підтвердження натисніть на кнопку ще раз',
        'challenge_cancel_request_sent_msg': 'Запит на скасування челенджа надіслано вашому опоненту',
        'challenge_cancel_request_opponent_msg': 'Ваш опонент {} хоче скасувати челендж. Для підтвердження цього натисніть відповідну кнопку у меню',
        'challenge_canceled_msg': 'Ваш челендж з {} скасовано',
        'challenge_cancellation_denied_opponent_msg': 'Ваш опонент {} відхилив скасування челенджа',
        'challenge_cancellation_denied_msg': 'Ви відхилили пропозицію {} стосовно скасування челенджа',
        'challenge_cancellation_in_progress_msg': 'Ваш опонент {} вже розглядає пропозицію скасування челенджа',
        'challenge_cancellation_opponent_is_verifying_results_msg': 'Ваш опонент {} наразі розглядає результати челенджу. Зараз скасування челенджу неможливе',

        'challenge_cancel_request_opponent_confirm_btn': 'Підтвердити скасування челенджа',
        'challenge_cancel_request_opponent_dismiss_btn': 'Відхилити скасування челенджа',

        'challenge_send_confirm_yes_btn': 'Так',
        'challenge_send_confirm_no_btn': 'Ні',

        'info_status_str': 'Статус',
        'info_level_str': 'Рівень',
        'info_matches_str': 'Матчів',
        'info_wins_str': 'Перемог',
        'info_losses_str': 'Поразок',
        'info_performance_str': 'Performance',
        'vacation_days_used_str': 'Використано днів відпустки',

        'back_btn': 'Назад',
        'to_menu_btn': 'У меню',

        'not_found_str': 'не знайдено',

        'error_occurred_contact_administrator_msg': 'Під час обробки вашого запиту сталася помилка. Зв’яжіться, будь ласка, з адміністрацією',

        'challenge_received_accept_btn': 'Прийняти челендж',
        'challenge_received_dismiss_btn': 'Відхилити челендж',
        'challenge_received_dismiss_confirm_msg': 'Ви впевнені, що хочете відмовитися від челенджа?\n'
                                                  'Натисніть кнопку ще раз, щоб підтвердити Ваш вибір',
        'challenge_received_not_found': 'Челендж не знайдено. Повернення до головного меню',
        'challenge_received_status': 'Наразі ви в челенджі з',
        'challenge_received_warning': 'Якщо Ви відхилете цей челендж, то автоматично отримаєте технічну поразку!',
        'challenge_confirm_technical_defeat': 'Відмова від цього челенджу призведе до технічної поразки!\n'
                                              'Натисніть на кнопку ще раз, щоб підтверджити Ваш вибір',
        'challenge_confirm_opponent_wins': 'Вам зараховано технічну перемогу. Ваш новий рівень:',
        'challenge_confirm_competitor_losses': 'Вам зараховано технічну поразку. Ваш новий рейтинг:',
        'challenge_confirm_challenge_accepted_opponent_msg': 'Ваш опонент {} прийняв челендж. Кількість днів, щоб зіграти челендж: {}',
        'challenge_confirm_challenge_accepted_competitor_msg': 'Челендж прийнято. Ваш опонент - {}. Кількість днів, щоб зіграти челендж: {}',
        'challenge_confirm_cannot_find_opponent_msg': 'Неможливо провести челендж - не вдається отримати інформацію про суперника',
        'challenge_confirm_cannot_fin_opponents_user_msg': 'Неможливо провести челендж - суперник більше не присутній у Telegram, тож неможливо надіслати йому інформацію про челендж',
        'challenge_confirm_challenge_canceled_by_bot_msg': 'Челендж буде скасовано автоматично. Для вирішення цієї проблеми зв’яжіться з адміністрацією.',

        'challenge_request_cancel_confirm_msg': 'Підтвердіть скасування запиту на челендж. Для цього настиніть ще раз на кнопку.',
        'challenge_request_canceled_to_competitor_msg': 'Ви скасували свій запит на челендж',
        'challenge_request_canceled_to_opponent_msg': 'Гравець {} скасував свій запит в челенджу до вас',

        'results_clear_btn': 'Очистити результат',
        'results_confirm_btn': 'Підтвердити результат',
        'results_scores_confirm_btn': 'Зафіксувати очки',

        'results_enter_results_msg': 'Уведіть результати челенджу',
        'result_current_str': 'Поточний результат',
        'result_match_result_str': 'Результат матчу',
        'result_challenge_canceled_str': 'челендж скасовано',
        'results_maximum_scores_entered_msg': 'Ви вже ввели результати 5-и сетів. Щоб очистити попередні результати скористайтеся кнопкою "Назад" або "Очистити"',
        'results_incorrect_score_msg': 'Введено некоректний результат',
        'result_scores_count_must_be_odd_msg': 'Для збереження необхідно ввести парну кількість результатів',
        'result_competitor_win_btn': 'Переміг я',
        'result_opponent_win_btn': 'Переміг мій опонент',
        'result_to_change_winner_press_again_str': 'Щоб змінити переможця натисніть відповідну кнопку',
        'result_select_winner_str': 'Вкажіть, хто переміг у матчі, натиснувши відповідну кнопку',
        'result_wins_str': 'перемагає',
        'result_winner_must_be_specified_msg': 'Необхідно вказати переможця матчу',
        'results_sent_to_opponent_msg': 'Результат матчу надіслано вашому опоненту. Тепер він має його підтвердити',
        'results_already_sent_msg': 'Результат вже надіслано. Чекайте, будь ласка, на відповідь опонента',

        'result_confirmation_confirm_btn': 'Результат підтверджую',
        'result_confirmation_dismiss_btn': 'Результат не підтверджую',

        'result_confirmation_msg': 'Ваш суперник надіслав результати матчу. Підтвердіть чи відхиліть їх.',
        'result_confirmation_confirm_msg': 'Для підтвердження вибору натисніть кнопку ще раз',
        'result_confirmation_confirmed_msg': '',
        'result_confirmation_confirmed_opponent_msg': '',
        'result_confirmation_dismissed_msg': '',
        'result_confirmation_dismissed_opponent_msg': '',

        'your_level_changed_str': 'Ваш рівень змінився: {}->{}',
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
