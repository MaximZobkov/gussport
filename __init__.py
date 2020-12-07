import datetime
import os

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, BooleanField, IntegerField,\
    SelectField, TimeField
from wtforms.validators import DataRequired

from data import db_session, users, competitions, news

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GusStory.ru'
db_session.global_init("db/blogs.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    sessions = db_session.create_session()
    return sessions.query(users.User).get(user_id)


class LoginForm(FlaskForm):
    email = StringField("Логин", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    email = StringField("Электронная почта", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения')
    gender = SelectField('Пол', validators=[DataRequired()],
                         choices=[('1', 'Мужской'), ('2', "Женский")])
    submit = SubmitField('Зарегистрироваться')


class CreateCompetitionForm(FlaskForm):
    name = StringField('Название соревнования', validators=[DataRequired()])
    event_date_start = DateField('Дата проведения соревнования')
    event_time_start = TimeField('Время начала соревнования')
    registration_start = DateField('Дата начала регистрации')
    registration_end = DateField('Дата окончания регистрации')
    type = SelectField('Тип соревнования', validators=[DataRequired()],
                         choices=[('1', 'Триатлон'), ('2', "Дуатлон"), ('3', "Лыжный Масс-старт"),
                                  ('4', "Веломарафон")])
    groups_count = IntegerField('Количество групп', validators=[DataRequired()])
    submit = SubmitField('Перейти к созданию групп')


class CreateGroupsForm(FlaskForm):
    age_range_start = IntegerField('Минмальный возраст', validators=[DataRequired()])
    age_range_end = IntegerField('Максимальный возраст', validators=[DataRequired()])
    players_count = IntegerField('Максимальное количество участников в группе', validators=[DataRequired()])
    group_time_start = TimeField('Время старта группы')
    payment = SelectField('Оплата участия', validators=[DataRequired()],
                          choices=[('1', 'Есть'), ('2', "Нет")])
    payments_value = IntegerField('Размер оплаты', validators=[DataRequired()])


class LengthError(Exception):
    error = 'Пароль должен от 8 до 15 символов!'


class LetterError(Exception):
    error = 'В пароле должна быть хотя бы одна буква!'


class DigitError(Exception):
    error = 'В пароле должна быть хотя бы одна цифра!'


@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template("profile.html")
    return redirect('/')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        result = check_password(form.password.data)
        date_check = check_date(form.date_of_birth.data)
        if result != 'OK':
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form, email_error="OK", again_password_error="OK", date_error="OK",
                                   password_error=result)
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, email_error="OK", password_error="OK", date_error="OK",
                                   again_password_error="Пароли не совпадают")
        sessions = db_session.create_session()
        if sessions.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   password_error="OK", again_password_error="OK", date_error="OK",
                                   email_error="Такой пользователь уже есть")
        if date_check != 'OK':
            return render_template('register.html', title='Регистрация',
                                   form=form, email_error="OK", password_error="OK",
                                   again_password_error="OK", date_error=date_check)
        user = users.User()
        user.email = form.email.data.lower()
        user.name = form.name.data
        user.surname = form.surname.data
        user.middle_name = form.middle_name.data
        user.date_of_birth = form.date_of_birth.data
        user.set_password(form.password.data)
        if str(request.files["file"]) != "<FileStorage: '' ('application/octet-stream')>":
            file = request.files["file"]
            name = "static/images/avatar_image/avatar_" + \
                   str(1 + len(os.listdir("static/images/avatar_image"))) + ".jpg"
            file.save(name)
            user.image = "/" + name
        sessions.add(user)
        if form.gender.data == '1':
            user.gender = 'Мужской'
        else:
            user.gender = 'Женский'
        sessions.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, email_error="OK",
                           password_error="OK", again_password_error="OK", date_error='OK')


@app.route('/create_competition', methods=['GET', 'POST'])
def create_competition():
    sessions = db_session.create_session()
    form = CreateCompetitionForm()
    if form.validate_on_submit():
        competition = competitions.Competitions()
        competition.name = form.name.data
        competition.type = form.type.data
        competition.event_time_start = form.event_time_start.data
        competition.event_date_start = form.event_date_start.data
        competition.registration_start = form.registration_start.data
        competition.registration_end = form.registration_end.data
        competition.groups_count = form.groups_count.data
        sessions.add(competition)
        sessions.commit()
        print(1)
        print('/groups_description/' + str(competition.id) + "/" + str(form.groups_count.data))
        return redirect('/groups_description/' + str(competition.id) + "/" + str(form.groups_count.data))
    return render_template('create_competition.html', title="Создание соревнования", form=form,
                           date_error='OK', time_error='OK')


@app.route("/groups_description/<int:id>/<int:count>", methods=['GET', 'POST'])
def groups_description(id, count):
    mas = [CreateGroupsForm() for i in range(count)]

    return render_template("groups_description.html", mas=mas, kol=1)


def check_password(password):
    flags = [0, 0]
    for element in password:
        if element.isdigit():
            flags[0] = 1
        elif element.isalpha():
            flags[1] = 1
    try:
        if flags[1] == 0:
            raise LetterError
        if flags[0] == 0:
            raise DigitError
        if len(password) < 8 or len(password) > 15:
            raise LengthError
        return 'OK'
    except (LengthError, LetterError, DigitError) as ex:
        return ex.error


def check_date(date):
    if int(str(date).split('-')[0]) > 2015:
        return 'Введенная дата неккоректна'
    return "OK"


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        sessions = db_session.create_session()
        user = sessions.query(users.User).filter(users.User.email ==
                                                 form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
def index():
    return render_template("index.html")


def main():
    global count_items
    sessions = db_session.create_session()
    sessions.close()
    app.run()


if __name__ == '__main__':
    main()
