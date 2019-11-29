from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField


def build_localization_form(localization_data, localization_key, **kwargs):

    class LocalizationForm(FlaskForm):
        pass

    for field, value in localization_data.items():
        setattr(LocalizationForm, field, StringField(field, default=value))

    setattr(LocalizationForm, 'key', HiddenField('key', default=localization_key))

    return LocalizationForm()
