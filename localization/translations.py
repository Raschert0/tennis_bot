LANGUAGES_DICTIONARY = {
    'uk': {
        'welcome_msg': 'Вітаю, {}!',

        'use_keyboard_msg': 'Використовуйте, будь ласка, віртуальну клавіатуру!',
        'message_type_not_supported_msg': 'Цей тип повідомлень не підтримується',

        'authentication_msg': 'Це офіційний бот Shuliavka Pyramid Open \n'
                              'Для участі в турнірі потрібно авторизуватись - просто оберіть себе зі списку гравців.\n'
                              'Якщо не можете знайти себе, зв’яжіться, будь ласка, з адміністрацією - @abezkorovainyi',
        'authentication_cannot_find_competitors_msg': 'Наразі немає неавторизованих учасників.\n'
                                                      'Зв’яжіться, будь ласка, із адміністрацією - @abezkorovainyi',
        'authentication_specified_competitor_not_found_clb': 'Такого учасника не знайдено',

        'competitor_record_vanished_msg': 'Не вдалося знайти інформацію про гравця. Необхідно знову пройти процедуру аутентифікації',

        'menu_info_btn': 'ℹ️ Профіль',
        'menu_create_challenge_btn': '🎾 Челендж',
        'menu_submit_challenge_results_btn': '💾 Повідомити результат матчу',
        'menu_cancel_challenge_btn': '❌ Скасувати челендж',
        'menu_cancel_challenge_request_btn': '❌ Скасувати челендж',
        'menu_reply_to_challenge_request_btn': '⚔️ Відповісти на челендж',
        'menu_go_on_vacation_btn': '🌴 Відпустка',
        'menu_go_on_sick_leave_btn': '🚑 Травма',
        'menu_end_vacation_btn': '🚀 Закінчити відпустку',
        'menu_end_sick_leave_btn': '💪 Повернутись до гри',

        'menu_msg': '👇',
        'menu_on_sick_leave_start_msg': 'Ви пішли на лікарняний. Бажаємо швидкого одужання 💊',
        'menu_on_sick_leave_end_msg': 'Лікарняний завершено! Вітаємо у грі 🎾',
        'menu_on_vacation_start_msg': 'Гарної відпустки ☀️',
        'menu_on_vacation_end_manual_msg': 'Відпустку завершено. Вітаємо у грі 🎾',
        'menu_on_vacation_end_msg': 'Ваша відпустка закінчилася. Ви у грі 🎾',
        'menu_vacation_no_days_left_msg': 'У вас не лишилося днів для відпустки в цьому місяці 👻',

        'challenge_send_msg': 'Оберіть зі списку гравця, якому ви хочете зробити челендж ⬆️',
        'challenge_send_confirm_msg': 'Надсилаємо челендж гравцю {}?',
        'challenge_sent_msg': 'Челендж надіслано! Чекайте на реакцію <a href="tg://user?id={}">{}</a>.',
        'challenge_no_applicable_competitors_msg': 'Наразі ніхто з доступних вам гравців не може отримати челендж. Дочекайтесь завершення наближчих матчів, а також поверення гравців з відпустки чи лікарняного 🙃',
        'challenge_specified_competitor_not_found_clb': 'Такого учасника не знайдено 🔎',
        'challenge_opponent_no_longer_available_msg': 'Обраний гравець наразі недоступний для челенджа. Спробуйте іншого, будь ласка 🙏',
        'challenge_cannot_send_message_to_opponent_msg': 'Неможливо надіслати челендж гравцю, оскільки він відсутній у Telegram 🙈',
        'challenge_you_are_challenged_msg': '<a href="tg://user?id={}">{}</a> (рівень: {}) зробив вам челендж. У вас є {} дні для відповіді',
        'challenge_you_are_challenged_passive_msg': '<a href="tg://user?id={}">{}</a> (рівень: {}) зробив вам челендж. У вас є {}\n для відповіді'
                                                    'Якщо ви не приймете цей челендж, вам буде зараховано технічну поразку в матчі!',
        'challenge_cancel_msg': 'Ви впевнені, що хочете скасувати челендж? Для підтвердження натисніть на кнопку ще раз ✍️',
        'challenge_cancel_request_sent_msg': 'Запит на скасування челенджа надіслано вашому опоненту 👀',
        'challenge_cancel_request_opponent_msg': 'Ваш опонент {} хоче скасувати челендж. Якщо ви згодні, натисніть відповідну кнопку ✍️',
        'challenge_canceled_msg': 'Ваш челендж з {} скасовано ❌',
        'challenge_cancellation_denied_opponent_msg': 'Ваш опонент {} не готовий скасувати челендж. Зв’яжіться, будь ласка ☎️',
        'challenge_cancellation_denied_msg': 'Ви відмовились від пропоцизії {} стосовно скасування челенджа. Зв’яжіться, будь ласка ☎️',
        'challenge_cancellation_in_progress_msg': 'Ваш опонент {} вже розглядає пропозицію скасування челенджа. Дочекайтесь реакції, будь ласка ☕️',
        'challenge_cancellation_opponent_is_verifying_results_msg': 'Ваш опонент {} має підтвердити результат матча. Зараз скасування челенджу неможливе 🕘',

        'challenge_cancel_request_opponent_confirm_btn': '✅ Так, скасувати челендж',
        'challenge_cancel_request_opponent_dismiss_btn': '❌ Ні, не скасовувати челендж',

        'challenge_send_confirm_yes_btn': '✅ Так',
        'challenge_send_confirm_no_btn': '❌ Ні',

        'info_status_str': '🕹 Поточний статус',
        'info_level_str': '🔺 Рівень',
        'info_matches_str': '🎾 Зіграно матчів',
        'info_wins_str': '😁 Перемог',
        'info_losses_str': '😐 Поразок',
        'info_performance_str': '🔥 Рейтинг сили',
        'vacation_days_used_str': '🌴 Днів у відпустці',

        'back_btn': '🔙 Назад',
        'to_menu_btn': 'В меню',

        'not_found_str': 'не знайдено',

        'error_occurred_contact_administrator_msg': 'Під час обробки вашого запиту сталася помилка. Зв’яжіться, будь ласка, з адміністрацією - @abezkorovainyi',

        'challenge_received_accept_btn': '✅ Прийняти челендж',
        'challenge_received_dismiss_btn': '❌ Відхилити челендж',
        'challenge_received_dismiss_confirm_msg': 'Ви впевнені, що хочете відмовитися від челенджа?\n'
                                                  'Натисніть кнопку ще раз, щоб підтвердити ваш вибір ',
        'challenge_received_not_found': 'Челендж не знайдено. Повернення до головного меню',
        'challenge_received_status': 'Наразі ви в челенджі з',
        'challenge_received_warning': 'Якщо Ви відхиляєте цей челендж, то автоматично отримаєте технічну поразку в матчі!',
        'challenge_confirm_technical_defeat': 'Відмова від цього челенджу призведе до технічної поразки!\n'
                                              'Натисніть на кнопку ще раз, щоб підтверджити ваш вибір',
        'challenge_confirm_opponent_wins': 'Вам зараховано технічну перемогу. Ваш новий рівень:',
        'challenge_confirm_competitor_losses': 'Вам зараховано технічну поразку. Ваш новий рівень:',
        'challenge_confirmation_dismissed_opponent_msg': 'Ваш опонент відмовився від челенджа',
        'challenge_confirmation_dismissed_competitor_msg': 'Ви відмовилися від челенджа',
        'challenge_confirm_challenge_accepted_opponent_msg': 'Ваш опонент {} прийняв челендж 🎾. Кількість днів, щоб зіграти матч: {}',
        'challenge_confirm_challenge_accepted_competitor_msg': 'Челендж прийнято 🎾. Ваш опонент - {}. Кількість днів, щоб зіграти матч: {}',
        'challenge_confirm_cannot_find_opponent_msg': 'Неможливо провести матч - не вдається отримати інформацію про суперника',
        'challenge_confirm_cannot_fin_opponents_user_msg': 'Неможливо провести матч - суперник більше не присутній у Telegram, нам не вдалось надіслати йому інформацію про челендж',
        'challenge_confirm_challenge_canceled_by_bot_msg': 'Челендж буде скасовано автоматично. Для вирішення цієї проблеми зв’яжіться з адміністрацією - @abezkorovainyi',

        'challenge_request_cancel_confirm_msg': 'Підтвердіть скасування запиту на челендж - настиніть ще раз на кнопку.',
        'challenge_request_canceled_to_competitor_msg': 'Ви скасували запит на челендж',
        'challenge_request_canceled_to_opponent_msg': 'Гравець {} скасував челендж до вас',

        'results_clear_btn': 'Очистити ❌',
        'results_confirm_btn': 'Підтвердити ✅',
        'results_scores_confirm_btn': 'Зафіксувати результат ✍️',

        'results_enter_results_msg': 'Введіть результат матчу ✍️',
        'result_current_str': 'Результат',
        'result_match_result_str': 'Результат матчу',
        'result_challenge_canceled_str': 'челендж скасовано',
        'results_maximum_scores_entered_msg': 'Ви вже ввели результати для 5-и сетів. Щоб очистити попередні результати скористайтеся кнопкою "🔙 Назад" або "❌ Очистити"',
        'results_incorrect_score_msg': 'Введено некоректний результат 🚨',
        'result_scores_count_must_be_odd_msg': 'Для збереження введіть результат повністю',
        'result_competitor_win_btn': 'Я переміг 😁',
        'result_opponent_win_btn': 'Я програв 😐',
        'result_to_change_winner_press_again_str': 'Для зміни переможця натисніть відповідну кнопку',
        'result_select_winner_str': 'Вкажіть, хто переміг у матчі',
        'result_wins_str': 'перемагає',
        'result_winner_must_be_specified_msg': 'Необхідно вказати переможця матчу',
        'results_sent_to_opponent_msg': 'Результат матчу надіслано вашому опоненту. Він має його підтвердити ✍️',
        'results_already_sent_msg': 'Результат вже надіслано. Чекайте, будь ласка, на відповідь опонента ☕️',

        'result_confirmation_confirm_btn': 'Підтвердити ✅',
        'result_confirmation_dismiss_btn': 'Скасувати ❌',

        'result_confirmation_msg': 'Ваш суперник надіслав результати матчу. Підтвердіть чи відхиліть їх.',
        'result_confirmation_confirm_msg': 'Для підтвердження натисніть кнопку ще раз',
        'result_confirmation_confirmed_msg': 'Результати матчу підтверджені ✅',
        'result_confirmation_confirmed_opponent_msg': 'Ваш опонент підтвердив результат матчу ✅',
        'result_confirmation_dismissed_msg': 'Результати матчу відхилені 🚨',
        'result_confirmation_dismissed_opponent_msg': 'Ваш опонент відхилив результати матчу 🚨',

        'your_level_changed_str': 'Ваш рівень змінився: {}->{}',

        'menu_accept_challenge_results_btn': 'Переглянути результати матчу 🎾',

        'remainder_challenge_accept_msg': 'Нагадуємо, що вам надіслали челендж в Піраміді 🎾. Для реагування залишилося днів: {}',
        'remainder_challenge_play_msg': 'Нагадуємо, що у ви в челенджі в Піраміді. У вас залишилося днів для матчу: {}',

        'challenge_was_ignored_msg': 'Ви проігнорували челендж 😿 На жаль, вам зараховано технічну поразку. В цьому сезоні ви проігнорували челенджів: {} (максимально допустимо за сезон: {})',
        'user_was_moved_to_inactive': 'Ви проігнорували надто багато челенджів. Вас переведено в стан Inactive. Для повернення до турніру зв’яжіться з адміністрацією - @abezkorovainy',
        'challenge_was_ignored_opponent_msg': 'Ваш опонент проігнорував челендж. Вам зараховано технічну перемогу в матчі.',

        'gsheet_technical_win_ignored_str': 'челендж проігноровано',
        'gsheet_technical_win_dismissed_str': 'повторна відмова',

        'gsheet_log_challenge_canceled': 'Челендж від {} до {} скасовано з технічних причин',
        'gsheet_log_challenge_canceled_no_opponent': 'Челендж від {} скасовано з технічних причин',
        'gsheet_log_player_created_challenge_for_player': '{} надіслав челендж {}',
        'gsheet_log_player_canceled_challenge_for_player': '{} скасував свій челендж',
        'gsheet_log_player_accepted_challenge_from_player': '{} прийняв челендж від {}',
        'gsheet_log_player_dismissed_challenge_from_player': '{} відхилив челендж від {}',
        'gsheet_log_player_ignored_challenge_from_player': '{} проігнорував челендж від {}',
        'gsheet_log_game_finished': 'Гру між {} та {} завершено. Переможець - {}, {}',
        'gsheet_log_game_canceled': 'Гру між {} та {} скасовано',
        'gsheet_log_player_moved_to_inactive': '{} проігнорував надто багато челенджів і був переведений до стану Inactive',
        'gsheet_log_player_started_vacation': '{} пішов у відпустку',
        'gsheet_log_player_finished_vacation': '{} вийшов з відпустки',
        'gsheet_log_on_injuiry_started': '{} травмувався',
        'gsheet_log_on_injuiry_ended': '{} позбувся травми',

        'group_chat_technical_win_report_msg': '{} отримує технічну перемогу над {}',
        'group_chat_match_result_msg': '{} виграє у {} з рахунком: {}',
        'group_chat_players_level_changed': 'Зміна рівнів гравців: {}',

        'admin_notification_competitor_changed_status': '{} змінив свій статус з {} на {}',
        'admin_notification_tg_user_vanished': 'Не вдається більше знайти користувача, який аутентифікувався як {}',
        'admin_notification_tg_user_blocked': 'Не вдалося надіслати повідомлення користувачу {}, оскільки він заблокував бота.\n'
                                              'Гравця {} переведено у стан Inactive',
        'admin_notification_tg_user_blocked_and_competitor_vanished': 'Не вдалося надіслати повідомлення користувачу {}, оскільки він заблокував бота.\n' \
                                                                      'При цьому користувач не пов\'язаний з жодним з гравців',

        'error_bot_blocked_by_opponent_challenge_canceled_msg': 'Ваш опонент заблокував бота, тому неможливо надіслати йому повідомлення.\nЧелендж скасовано',
    }
}


def get_translation_for(token):
    v = LANGUAGES_DICTIONARY['uk'].get(token, None)
    if v is not None:
        return v
    raise ValueError('Could not find translation for {}'.format(token))
