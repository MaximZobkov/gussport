import datetime
import os, json

from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, BooleanField, IntegerField, \
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
    residence_type = SelectField('Тип населённого пункта', validators=[DataRequired()],
                         choices=[('1', 'Город'), ('2', "Село"), ('3', "Деревня"),
                                  ('4', "Посёлок"), ('5', "Посёлок городского типа")])
    residence_name = StringField('Название населённого пункта', validators=[DataRequired()])
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
    age_range_start = IntegerField('Минимальный возраст', validators=[DataRequired()])
    age_range_end = IntegerField('Максимальный возраст', validators=[DataRequired()])
    players_count = IntegerField('Максимальное количество участников в группе',
                                 validators=[DataRequired()])
    group_time_start = TimeField('Время старта группы')
    payment = SelectField('Оплата участия', validators=[DataRequired()],
                          choices=[('1', 'Есть'), ('2', "Нет")])
    payments_value = IntegerField('Размер оплаты', validators=[DataRequired()])


class CreateNewsForm(FlaskForm):
    name = StringField("Заголовок новости", validators=[DataRequired()])
    content = StringField("Новость:", validators=[DataRequired()])
    submit = SubmitField("Завершить создание новости")


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
    print(4, form.validate_on_submit())
    if request.method == "POST":
        print(3)
        result = check_password(form.password.data)
        date_check = check_date(form.date_of_birth.data)
        if result != 'OK':
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form, email_error="OK", again_password_error="OK",
                                   date_error="OK",
                                   password_error=result)
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, email_error="OK", password_error="OK",
                                   date_error="OK",
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
        user.residence_type = request.form["typecode"]
        user.residence_name = request.form["city"]
        print(request.form["city"])
        print(request.form["typecode"])
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
    return render_template('register.html', form=form, email_error="OK", again_password_error="OK",
                                   date_error="OK", password_error="OK")


@app.route('/create_competition', methods=['GET', 'POST'])
@login_required
def create_competition():
    if current_user.role != "admin":
        return redirect("/")
    sessions = db_session.create_session()
    form = CreateCompetitionForm()
    if request.method == "POST":
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
        print('/groups_description/' + str(competition.id) + "/" + str(form.groups_count.data))
        return redirect(
            '/groups_description/' + str(competition.id) + "/" + str(
                form.groups_count.data) + "/0")
    return render_template('create_competition.html', title="Создание соревнования", form=form,
                           date_error='OK', time_error='OK')


@app.route("/groups_description/<int:id>/<int:count>/<int:number>", methods=['GET', 'POST'])
@login_required
def groups_description(id, count, number):
    if current_user.role != "admin":
        return redirect("/")
    sessions = db_session.create_session()
    form = CreateGroupsForm()
    if request.method == "POST":
        competition = sessions.query(competitions.Competitions).filter(
            competitions.Competitions.id == id).first()
        competition.groups_description += "%%" + "$$".join([str(form.age_range_start.data),
                                                            str(form.age_range_end.data),
                                                            str(form.players_count.data),
                                                            str(form.group_time_start.data),
                                                            str(form.payments_value.data)])
        sessions.merge(competition)
        sessions.commit()
        number += 1
        if number == count:
            return redirect('/')
        else:
            return redirect(
                '/groups_description/' + str(competition.id) + "/" + str(count) + "/" + str(
                number))
    return render_template("groups_description.html", form=form, count=count, number=number)


@app.route("/user_management", methods=['GET', 'POST'])
@login_required
def user_management():
    if current_user.role != "admin":
        return redirect("/")
    sessions = db_session.create_session()
    table = []
    users_list = sessions.query(users.User)
    for user in users_list:
        row = [user.id, user.name, user.surname, user.middle_name, user.email, user.date_of_birth,
               user.gender, user.role]
        table += [row]
    return render_template("user_management.html", table=table)


@app.route("/redefine_role/<string:role>/<int:id>")
@login_required
def redefine_role(role, id):
    if current_user.role != "admin":
        return redirect("/")
    sessions = db_session.create_session()
    user = sessions.query(users.User).filter(users.User.id == id).first()
    user.role = role
    sessions.merge(user)
    sessions.commit()
    return redirect("/user_management")


@app.route("/create_news", methods=['GET', 'POST'])
def create_news():
    if current_user.role != "admin":
        return redirect("/")
    form = CreateNewsForm()
    sessions = db_session.create_session()
    if request.method == "POST":
        new = news.News()
        new.name = form.name.data
        new.content = form.content.data
        if str(request.files["file"]) != "<FileStorage: '' ('application/octet-stream')>":
            file = request.files["file"]
            name = "static/images/avatar_image/avatar_" + \
                   str(1 + len(os.listdir("static/images/avatar_image"))) + ".jpg"
            file.save(name)
            new.image = "/" + name
        sessions.add(new)
        sessions.commit()
        return redirect('/')
    return render_template("create_news.html", form=form)


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
    sessions = db_session.create_session()
    all_news = sessions.query(news.News)
    news_list = []
    for new in all_news:
        news_list += [new]
    return render_template("index.html", news_list=news_list)


@app.errorhandler(404)  # функция ошибки
def not_found(error):
    return render_template("not_found.html")


@app.errorhandler(401)  # функция ошибки
def not_found(error):
    return render_template("not_authorized.html")


def main():
    global count_items
    sessions = db_session.create_session()
    sessions.close()
    app.run()


if __name__ == '__main__':
    main()
