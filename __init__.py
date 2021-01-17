import datetime
import os
import json

from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, BooleanField, IntegerField, \
    SelectField, TimeField, TextAreaField, FileField
from wtforms.validators import DataRequired

from data import db_session, users, competitions, news

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GusStory.ru'
db_session.global_init("db/blogs.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)


# Кто читает этот код извините меня, вместо failed должно быть upcoming, не бейте палками


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
    residence_name = StringField('Название населённого пункта', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class CreateCompetitionForm(FlaskForm):
    name = StringField('Название соревнования', validators=[DataRequired()])
    short_description = StringField('Краткое описание соревнования', validators=[DataRequired()])
    event_date_start = DateField('Дата проведения соревнования')
    event_time_start = TimeField('Время начала соревнования')
    registration_start = DateField('Дата начала регистрации')
    registration_end = DateField('Дата окончания регистрации')
    type = SelectField('Тип соревнования', validators=[DataRequired()],
                       choices=[('Триатлон', 'Триатлон'), ('Дуатлон', "Дуатлон"),
                                ('Лыжный Масс-старт', "Лыжный Масс-старт"),
                                ('Лыжная гонка', 'Лыжная гонка'),
                                ('Велокросс', 'Велокросс'), ('Велобиатлон', 'Велобиатлон'),
                                ('Веломарафон', "Веломарафон"), ('Забег', 'Забег'),
                                ('Марафон', 'Марафон'),
                                ('Полумарафон', 'Полумарафон'), ('Плавание', 'Плавание')])
    groups_count = IntegerField('Количество групп', validators=[DataRequired()])
    submit = SubmitField('Перейти к созданию групп')


class CreateGroupsForm(FlaskForm):
    gender = SelectField('Пол', validators=[DataRequired()],
                         choices=[('1', 'Мужчины'), ('2', "Женщины")])
    age_range_start = IntegerField('Минимальный возраст', validators=[DataRequired()])
    age_range_end = IntegerField('Максимальный возраст', validators=[DataRequired()])
    players_count = IntegerField('Максимальное количество участников в группе',
                                 validators=[DataRequired()])
    distance = IntegerField('Длина дистанции', validators=[DataRequired()])
    group_time_start = TimeField('Время старта группы')
    payment = SelectField('Оплата участия', validators=[DataRequired()],
                          choices=[('1', 'Есть'), ('2', "Нет")])
    payments_value = IntegerField('Размер оплаты', validators=[DataRequired()])


class CreateNewsForm(FlaskForm):
    name = StringField("Заголовок новости", validators=[DataRequired()])
    content = TextAreaField("Новость:", validators=[DataRequired()])
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
        sessions = db_session.create_session()
        with open("static/json/competition.json") as file:
            data = json.load(file)
        upcoming = data["failed_competitions"]
        keys_list = upcoming.keys()
        users_competition = []
        for competition_name in keys_list:
            competition = upcoming[competition_name]
            if current_user.id in competition["all_users"]:
                keys = competition.keys()
                for key in keys:
                    if key != "all_users" and current_user.id in competition[key]:
                        full_competition = sessions.query(competitions.Competitions).filter(
                            competitions.Competitions.url == competition_name).first()
                        users_competition += [[full_competition, key]]
                        break
        flag = 1
        if len(users_competition) == 0:
            flag = 0
        return render_template("profile.html", users_competition=users_competition, flag=flag)
    return redirect('/')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST":
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
        user.set_password(form.password.data)
        if form.gender.data == '1':
            user.gender = 'Мужской'
        else:
            user.gender = 'Женский'
        sessions.add(user)
        sessions.commit()
        if str(request.files["file"]) != "<FileStorage: '' ('application/octet-stream')>":
            file = request.files["file"]
            name = "static/images/avatar_image/avatar_" + str(user.id) + ".jpg"
            file.save(name)
            user.image = "/" + name
        sessions.merge(user)
        sessions.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, email_error="OK",
                           password_error="OK", again_password_error="OK", date_error='OK')


def reformat(string_date):
    s = string_date.split('-')
    month = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
             'августа', 'сентября', 'октября', 'ноября', 'декабря']
    string = ''
    k = 0
    for x in s[::-1]:
        print(string)
        if k == 0:
            string += x + ' '
        elif k == 1:
            string += month[int(x) - 1] + ' '
        else:
            string += x
        k += 1
    return string


@app.route('/competition/<int:id>')
def single_competition(id):
    session = db_session.create_session()
    competition = session.query(competitions.Competitions).filter(
        competitions.Competitions.id == id).first()
    array_group = competition.groups_description[2:].split('%%')
    array = []
    for i in range(competition.groups_count):
        array_elements = array_group[i].split('$$')
        string_year = f'{array_elements[0]}-{array_elements[1]} лет.'
        string_count_people = f'{array_elements[2]}'
        string_distance = f'{array_elements[3]} км.'
        string_time = f'{array_elements[4][:-3]}.'
        string_money = f'{array_elements[5]}'
        array.append(
            [string_year, string_count_people, string_distance, string_time, string_money])
    return render_template('single_competition.html', competition=competition, groups_array=array)


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
        competition.short_description = form.short_description.data
        competition.type = form.type.data
        competition.event_time_start = str(form.event_time_start.data)[:-3]
        competition.event_date_start = reformat(str(form.event_date_start.data))
        competition.registration_start = reformat(str(form.registration_start.data))
        competition.registration_end = reformat(str(form.registration_end.data))
        competition.groups_count = form.groups_count.data
        sessions.add(competition)
        sessions.commit()
        if str(request.files["file"]) != "<FileStorage: '' ('application/octet-stream')>":
            file = request.files["file"]
            name = "static/images/competition_image/competition_" + str(competition.id) + ".jpg"
            file.save(name)
            competition.image = "/" + name
        with open("static/json/competition.json") as file:
            data = json.load(file)
        data["failed_competitions"].update(
            [("competition" + str(competition.id), {"all_users": []})])
        with open("static/json/competition.json", "w") as file:
            json.dump(data, file)
        competition.url = "competition" + str(competition.id)
        sessions.merge(competition)
        sessions.commit()
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
        competition.groups_description = "%%".join([competition.groups_description,
                                                    "$$".join([str(form.age_range_start.data),
                                                               str(form.age_range_end.data),
                                                               str(form.players_count.data),
                                                               str(form.distance.data),
                                                               str(form.group_time_start.data),
                                                               str(form.payments_value.data),
                                                               str(form.gender.data)])])
        with open("static/json/competition.json") as file:
            data = json.load(file)
        group_name_to_dict = str(form.age_range_start.data) + ":" + str(
            form.age_range_end.data) + ":" + str(
            form.players_count.data) + ":" + str(form.distance.data) + ":" + str(form.gender.data)
        data["failed_competitions"][competition.url].update([(group_name_to_dict, [])])
        with open("static/json/competition.json", "w") as file:
            json.dump(data, file)
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


@app.route("/register_to_competition/<string:name>/<int:id>/<int:number>")
@login_required
def register_to_competition(name, id, number):
    session = db_session.create_session()
    with open("static/json/competition.json") as file:
        data = json.load(file)
    user = session.query(users.User).filter(users.User.id == id).first()
    age = get_age(user.date_of_birth)
    keys = data["failed_competitions"][name].keys()
    group_list = []
    small_dict = {"Мужской": 1, "Женский": 2}
    stack_overflow = 0
    competition_id = int(name.split("competition")[1])
    if id in data["failed_competitions"][name]["all_users"]:
        stack_overflow = 1
    if stack_overflow == 1:
        return render_template("end_registration_to_competition.html", message="stack overflow",
                               competition_id=competition_id)
    for key in keys:
        if key == "all_users":
            continue
        key_s = key.split(':')
        if (int(key_s[0]) <= age <= int(key_s[1]) and
                int(key_s[4]) == small_dict[user.gender]):
            lenght = max(int(key_s[2]) - len(data["failed_competitions"][name][key]), 0)
            group_list += [[key_s, lenght]]
    if len(group_list) == 0:
        # пользователь не может зарегистрироваться на это соревнование, т.к. нет подходящей возрастной категории
        return render_template("end_registration_to_competition.html", message="no age category",
                               competition_id=competition_id)
    print(group_list, number)
    if number != 0:
        data["failed_competitions"][name][":".join(group_list[number - 1][0])] += [id]
        data["failed_competitions"][name]["all_users"] += [id]
        with open("static/json/competition.json", "w") as file:
            json.dump(data, file)
        # регистрация успешно завершена
        return render_template("end_registration_to_competition.html", message="success",
                               competition_id=competition_id)
    return render_template('register_to_competition.html', group_list=group_list, name=name, id=id,
                           competition_id=competition_id)


@app.route("/unregister/<string:name>/<int:id>/<string:group>")
@login_required
def unregister(name, id, group):
    print(group)
    with open("static/json/competition.json") as file:
        data = json.load(file)
    mas = data["failed_competitions"][name]
    if id in mas[group]:
        mas[group].remove(id)
    if id in mas["all_users"]:
        mas["all_users"].remove(id)
    data["failed_competitions"][name] = mas
    with open("static/json/competition.json", "w") as file:
        json.dump(data, file)
    return redirect("/profile")


@app.route('/competitions')
def all_competitions():
    session = db_session.create_session()
    competitions_list = session.query(competitions.Competitions)
    return render_template('competitions.html', competitions_list=competitions_list)


@app.route("/delete_competition/<int:id>")
def delete_competitions(id):
    session = db_session.create_session()
    competition = session.query(competitions.Competitions).filter(
        competitions.Competitions.id == id).first()
    with open("static/json/competition.json") as file:
        data = json.load(file)
    data["failed_competitions"].pop("competition" + str(id), None)
    with open("static/json/competition.json", "w") as file:
        json.dump(data, file)
    session.delete(competition)
    session.commit()
    try:
        os.remove(f"static/images/competition_image/competition_{id}.jpg")
    except Exception:
        pass
    return redirect("/competitions")


def get_age(data):
    date = data.split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    print(day, month, year)
    today_year = datetime.datetime.now().year
    today_month = datetime.datetime.now().month
    today_day = datetime.datetime.now().day
    if (today_month < month) or (today_month == month and today_day < day):
        return today_year - year - 1
    else:
        return today_year - year


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
    if request.method == "POST":
        sessions = db_session.create_session()
        new = news.News()
        new.name = form.name.data
        new.content = form.content.data
        photo = request.files['file1']
        file = request.files['file']
        print(str(file)[-6:-3])
        if file:
            file_extension = str(file)[-6:-3]
            file.save("static/files/file_" + \
                      str(1 + len(os.listdir("static/files"))) + "." + file_extension)
            new.files = "static/files/file_" + \
                        str(len(os.listdir("static/files"))) + "." + file_extension
        photo.save("static/images/news_image/news_" + \
                   str(1 + len(os.listdir("static/images/news_image"))) + ".jpg")
        new.image = "static/images/news_image/news_" + \
                    str(len(os.listdir("static/images/news_image"))) + ".jpg"
        sessions.add(new)
        sessions.commit()
        return redirect('/')
    return render_template("create_news.html", form=form)


@app.route("/delete_new/<int:id>")
def delete_news(id):
    session = db_session.create_session()
    new = session.query(news.News).filter(news.News.id == id).first()
    session.delete(new)
    session.commit()
    try:
        os.remove(f"static/images/news_image/news_{id}.jpg")
    except Exception:
        pass
    try:
        print(f"{new.files}")
        os.remove(f"{new.files}")
    except Exception:
        pass
    return redirect("/")


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
    return render_template("index.html", news_list=all_news)


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
