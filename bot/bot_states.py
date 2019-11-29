from bot.state_handler import StateHandler
from models import User, Texts
import bot.bot_methods as bot_methods
import bot.keyboards as keyboards


class BotStates(StateHandler):
    def __init__(self, bot):
        super(BotStates, self).__init__(bot)
        self._register_states([self.main_menu_state])

    def _start_state(self, message, entry=False):
        texts = Texts.objects().first()
        user = User.objects(user_id=message.chat.id).first()

        self._go_to_state(message, self.main_menu_state)

    def main_menu_state(self, message, entry=False):
        texts = Texts.objects().first()
        user = User.objects(user_id=message.chat.id).first()

        if entry:
            print('first entry')
            self._bot.send_message(message.chat.id,
                                   texts['greet_msg'].format(user.first_name),
                                   reply_markup=keyboards.set_main_keyboard())
        else:
            print('not first entry')
            if message.text == texts['cappers_btn']:
                bot_methods.send_cappers(self, message)
            elif message.text == texts['cappers_stats_btn']:
                bot_methods.send_cappers_stats(self._bot, message)
            elif message.text == texts['my_stats_btn']:
                bot_methods.send_my_stats(self, message)
            elif message.text == texts['refs_btn']:
                self._bot.send_message(message.chat.id,
                                       texts['refs_msg'],
                                       reply_markup=keyboards.set_referral_keyboard(user))
            elif message.text == texts['donate_btn']:
                self._go_to_state(message, self.donate_state)
            elif message.text == texts['news_btn']:
                self._bot.send_message(message.chat.id, texts['news_msg'])
            elif message.text == texts['faq_btn']:
                self._bot.send_message(message.chat.id, texts['faq_msg'])
            else:
                self._bot.send_message(message.chat.id,
                                       texts['use_keyboard_msg'],
                                       reply_markup=keyboards.set_main_keyboard())
