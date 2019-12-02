from flask import url_for, request, redirect
from flask_admin import BaseView, expose
from localization.translations import LANGUAGES_DICTIONARY, update_translation_for, __get_translation_for as trans_for


class LocalizationView(BaseView):
    @expose('/')
    def index(self):
        unique_keys = set()
        langs = []

        for lang, dict in LANGUAGES_DICTIONARY.items():
            unique_keys.update(dict.keys())
            l_data = {'lang': lang}
            langs.append(l_data)

        unique_keys = list(unique_keys)
        unique_keys.sort()

        for l_data in langs:
            trans_data = {}
            lang = l_data['lang']
            for key in unique_keys:
                try:
                    tr = trans_for(lang, key)
                except ValueError:
                    tr = ''
                trans_data[key] = tr
            l_data['data'] = trans_data

        return self.render('localization.html', keys=unique_keys, translations=langs)

    @expose('/update', methods=['GET', 'POST'])
    def update(self):
        key = request.values.get('key')
        if key is None:
            return 'Key not found', 500

        if request.method == 'POST':
            try:
                for k, v in request.form.items():
                    update_translation_for(k, key, v)

            except Exception as e:
                #logger.exception('Exception occurred in user_edit()')
                return str(e), 500

            return redirect(url_for('localization.index'))

        langs = {}
        if request.method == 'GET':
            for lang in LANGUAGES_DICTIONARY.keys():
                try:
                    langs[lang] = trans_for(lang, key)
                except ValueError:
                    langs[lang] = ''

        return self.render('localization_edit.html', possible_translations=langs, key=key)
