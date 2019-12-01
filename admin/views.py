from flask import Blueprint, redirect, url_for, request, render_template, flash, send_file, Markup
from flask_admin.contrib.mongoengine import ModelView
from flask_admin import Admin, BaseView, expose
from flask_admin.form import rules
from flask_login import LoginManager, current_user, login_user, logout_user
from models import User, Administrator, Competitor, RESULT, Result, HighLevelLogs
from admin.forms import LoginForm
import admin.methods as methods
from threading import Thread
from localization.views import LocalizationView

admin_blueprint = Blueprint('admin_bp', __name__)
login = LoginManager()

@login.user_loader
def load_user(user_id):
    return Administrator.objects(id=user_id).first()


@admin_blueprint.route('/')
def index():
    return redirect(url_for('admin.index'))


# @admin_blueprint.route('/send', methods=['POST'])
# def handle_sending():
#     form = request.form
#     message = Mailing.objects(id=form['id']).first()
#     Thread(target=methods.send_messages, args=(message,)).start()
#     flash('Отправлено', category='success')
#     return redirect('/admin/mailing')


# @admin_blueprint.route('/send_message', methods=['POST'])
# def handle_user_sending():
#     form = request.form
#     user = User.objects(user_id=form['user_id']).first()
#     bot_handler.bot.send_message(user.user_id, form['message'])
#     flash('Отправлено', category='success')
#
#     if 'msg' in request.form:
#         return redirect('/admin/feedback')
#     else:
#         return redirect('/admin/user')


def validate_login(user, form):
    if user is None:
        return False

    if user.password == form.password.data:
        return True
    else:
        return False


@admin_blueprint.route('/login', methods=['GET', 'POST'])
def handle_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Administrator.objects(username=form.username.data).first()

        if validate_login(user, form):
            login_user(user)
            flash('Logged in', category='success')
            return redirect(url_for('admin.index'))
        else:
            flash('Wrong username or password', category='danger')

    return render_template('login.html', form=form)


@admin_blueprint.route('/logout')
def handle_logout():
    logout_user()
    return redirect(url_for('admin.index'))


class MyUserView(ModelView):
    # list_template = 'user_list.html'

    column_searchable_list = ['username', 'first_name', 'last_name']

    # can_delete = False

    can_set_page_size = True

    column_filters = ['username', 'first_name', 'last_name']

    def is_accessible(self):
        return current_user.is_authenticated


class CompetitorView(ModelView):

    column_searchable_list = ['name', ]
    can_set_page_size = True
    column_filters = ['name', ]

    column_formatters = {
        'status': lambda v, c, m, p: Competitor.status_code_to_str_dict[m.status],
        'previous_status': lambda v, c, m, p: Competitor.status_code_to_str_dict[m.previous_status],
        'in_challenge_with': lambda v, c, m, p: m.check_opponent().name if m.check_opponent() else None
    }
    create_modal = True
    edit_modal = True
    column_exclude_list = ['legacy_number', 'previous_challenge_status']
    form_excluded_columns = ['previous_status', 'legacy_number', 'previous_challenge_status', 'in_challenge_with', 'latest_challenge_sent_to', ]

    def is_accessible(self):
        return current_user.is_authenticated


class ResultView(ModelView):

    create_modal = True
    can_set_page_size = True
    edit_modal = True
    column_exclude_list = ['player_a', 'player_b']
    form_excluded_columns = ['player_a', 'player_b']

    column_formatters = {
        'result': lambda v, c, m, p: Result.result_to_str_dict[m.result]
    }

    def is_accessible(self):
        return current_user.is_authenticated


class LogsView(ModelView):

    column_searchable_list = ['log', ]
    can_set_page_size = True
    column_filters = ['severity', ]

    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class ConfigView(ModelView):
    create_modal = True
    edit_modal = True

    form_excluded_columns = ['config_id', 'last_daily_check']
    can_delete = False
    can_create = False

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(template_mode='bootstrap3')
admin.add_view(MyUserView(User, name='Користувачі (TG)'))
admin.add_view(CompetitorView(Competitor, name='Учасники турніру'))
admin.add_view(ResultView(Result, name='Результати'))
admin.add_view(LogsView(HighLevelLogs, name='Логи', category='Налаштування'))
admin.add_view(MyAdminView(Administrator, name='Адміни', category='Налаштування'))
admin.add_view(LocalizationView(name="Переклад", category='Налаштування', endpoint="localization"))
