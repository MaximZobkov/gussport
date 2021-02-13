import datetime
import os
import json
import shutil
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from random import randint
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, BooleanField, IntegerField, \
    SelectField, TimeField, TextAreaField
from wtforms.validators import DataRequired

from data import db_session, users, competitions, news

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GusStory.ru'
db_session.global_init("db/blogs.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)
code = 0
i = 0
flag = 0
name = 0
mail_to = ''


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
    date_of_birth = DateField('Дата рождения', validators=[DataRequired()])
    gender = SelectField('Пол', validators=[DataRequired()],
                         choices=[('1', 'Мужской'), ('2', "Женский")])
    club = StringField('Клуб')
    residence_name = StringField('Название населённого пункта', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class EditForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    email = StringField("Электронная почта", validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', validators=[DataRequired()])
    gender = SelectField('Пол', validators=[DataRequired()],
                         choices=[('Мужской', 'Мужской'), ('Женский', "Женский")])
    club = StringField('Клуб')
    residence_name = StringField('Название населённого пункта', validators=[DataRequired()])
    submit = SubmitField('Изменить данные')


class CreateCompetitionForm(FlaskForm):
    name = StringField('Название соревнования', validators=[DataRequired()])
    short_description = TextAreaField('Краткое описание соревнования', validators=[DataRequired()])
    event_date_start = DateField('Дата проведения соревнования')
    event_time_start = TimeField('Время начала соревнования')
    registration_start = DateField('Дата начала регистрации')
    registration_end = DateField('Дата окончания регистрации')
    team_competition = SelectField('Тип соревнования', validators=[DataRequired()],
                                   choices=[('Индивидуальное', "Индивидуальное"), ('Командное', 'Командное')])
    kol_vo_player = IntegerField('Количество участников в команде', validators=[DataRequired()], default=1)
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
                          choices=[('1', 'Нет'), ('2', "Есть")])
    payments_value = IntegerField('Размер оплаты', validators=[DataRequired()])


class CreateNewsForm(FlaskForm):
    name = StringField("Заголовок новости", validators=[DataRequired()])
    content = TextAreaField("Новость:", validators=[DataRequired()])
    submit = SubmitField("Завершить создание новости")


class RegisterGroupForm(FlaskForm):
    name = StringField("Название команды", validators=[DataRequired()])
    player1 = StringField("ФИО участника 1", validators=[DataRequired()])
    id_player1 = IntegerField("ID 1", validators=[DataRequired()])
    player2 = StringField("ФИО участника 2", validators=[DataRequired()])
    id_player2 = IntegerField("ID 2", validators=[DataRequired()])
    player3 = StringField("ФИО участника 3", validators=[DataRequired()])
    id_player3 = IntegerField("ID 3", validators=[DataRequired()])
    player4 = StringField("ФИО участника 4", validators=[DataRequired()])
    id_player4 = IntegerField("ID 4", validators=[DataRequired()])
    player5 = StringField("ФИО участника 5", validators=[DataRequired()])
    id_player5 = IntegerField("ID 5", validators=[DataRequired()])
    submit = SubmitField("Завершить регистрацию")


class LengthError(Exception):
    error = 'Пароль должен от 8 до 15 символов!'


class LetterError(Exception):
    error = 'В пароле должна быть хотя бы одна буква!'


class DigitError(Exception):
    error = 'В пароле должна быть хотя бы одна цифра!'


class RecoveryForm(FlaskForm):
    email = StringField("Введите почту", validators=[DataRequired()])
    code = StringField("Введите код", validators=[DataRequired()])
    new_password = PasswordField("Введите новый пароль", validators=[DataRequired()])
    repeat_new_password = PasswordField("Повторите новый пароль", validators=[DataRequired()])
    submit = SubmitField("Отправить")


@app.route('/recovery_password', methods=['GET', 'POST'])
def recovery_password():
    global mail_to, flag
    form = RecoveryForm()
    sessions = db_session.create_session()
    if request.method == 'POST':
        if not (form.repeat_new_password.data is None or form.repeat_new_password.data == ""):
            if form.repeat_new_password.data == form.new_password.data and flag == 2:
                user = sessions.query(users.User).filter(users.User.email == mail_to).first()
                user.set_password(form.new_password.data)
                sessions.merge(user)
                sessions.commit()
                flag = 0
                return redirect("/login")
            elif form.repeat_new_password.data != form.new_password.data and flag == 2:
                result = check_password(form.new_password.data)
                return render_template('password_recovery.html', form=form, type="password",
                                       message=result)
        elif sessions.query(users.User).filter(users.User.email ==
                                               form.email.data.lower()).first() and flag == 0:
            send_email(form.email.data.lower())
            mail_to = form.email.data.lower()
            flag = 1
            return render_template('password_recovery.html', form=form, type="code", message="OK")

        elif sessions.query(users.User).filter(users.User.email ==
                                               form.email.data.lower()).first() is None and flag == 0:
            return render_template('password_recovery.html', form=form, type="email",
                                   message="Пользователя с данной почтой не существует")
        elif form.code.data.strip() == str(code).strip() and flag == 1:
            flag = 2
            return render_template('password_recovery.html', form=form, type="password", message="OK")
        elif form.code.data.strip() != str(code).strip() and flag == 1:
            return render_template('password_recovery.html', form=form, type="code", message="Неверный код")
    return render_template('password_recovery.html', form=form, type="email", message='OK')


def send_email(user_mail):
    global code, flag
    flag = 0
    code = randint(100000, 1000000)
    subject_msg = 'Восстановление пароля GusSport'
    body = f'Ваш проверочный код: {code}'
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject_msg, 'utf-8')
    server = smtplib.SMTP('smtp.beget.com:2525')
    server.starttls()
    server.login('gussport@gusstory.ru', '12345678aA')
    server.sendmail('gussport@gusstory.ru', user_mail, msg.as_string())
    server.quit()


@app.route('/profile/<int:id>')
def profile(id):
    if not current_user.is_authenticated:
        return redirect('/')
    sessions = db_session.create_session()
    user = sessions.query(users.User).filter(users.User.id == id).first()
    with open("static/json/competition.json") as file:
        data = json.load(file)
    upcoming = data["failed_competitions"]
    keys_list = upcoming.keys()
    users_competition = []
    for competition_name in keys_list:
        competition = upcoming[competition_name]
        if user.id in competition["all_users"]:
            keys = competition.keys()
            for key in keys:
                if not key in ["all_users", "registration"] and user.id in competition[key]:
                    full_competition = sessions.query(competitions.Competitions).filter(
                        competitions.Competitions.url == competition_name).first()
                    users_competition += [[full_competition, key]]
                    break
    flag = 1
    if len(users_competition) == 0:
        flag = 0
    age = get_age(user.date_of_birth)
    if current_user.id == id:
        return render_template("profile.html", users_competition=users_competition, flag=flag, user=user, age=age,
                           profile=True)
    return render_template("profile.html", users_competition=users_competition, flag=flag, user=user, age=age,
                           profile=False)


@app.route('/edit_profile/<int:id>', methods=["GET", "POST"])
def editor_profile(id):
    form = EditForm()
    session = db_session.create_session()
    user = session.query(users.User).filter(users.User.id == id).first()
    if current_user.is_authenticated and current_user.id == id:
        if request.method == "GET":
            form.name.data = user.name
            form.surname.data = user.surname
            form.gender.data = user.gender
            form.middle_name.data = user.middle_name
            form.club.data = user.club
            form.email.data = user.email
        elif request.method == "POST":
            user.email = form.email.data.lower().strip()
            user.name = form.name.data
            user.surname = form.surname.data
            user.middle_name = form.middle_name.data
            user.gender  = form.gender.data
            date_check = check_date(form.date_of_birth.data)
            if date_check != 'OK':
                return render_template('register.html', title='Регистрация',
                                       form=form, email_error="OK", password_error="OK",
                                       again_password_error="OK", date_error=date_check)
            user.date_of_birth = form.date_of_birth.data
            user.residence_name = request.form["city"]
            user.club = form.club.data
            session.merge(user)
            session.commit()
            return redirect('/profile/' + str(id))
        return render_template('editor_profile.html', form=form, user=user, date_error="OK")
    if current_user.is_authenticated:
        return redirect(f'/profile/{current_user.id}')
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
        user.email = form.email.data.lower().strip()
        user.name = form.name.data
        user.surname = form.surname.data
        user.middle_name = form.middle_name.data
        user.date_of_birth = form.date_of_birth.data
        user.residence_type = request.form["typecode"]
        user.residence_name = request.form["city"]["typecode"]
        user.club = form.club.data
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
    check_all_competitions()
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
        competition.team_competition = form.team_competition.data
        competition.kol_vo_player = form.kol_vo_player.data
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
            [("competition" + str(competition.id), {"all_users": [], "registration": 0})])
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


@app.route("/register_to_competition/<string:name>/<int:id>/<int:number>/<int:kol_vo_player>")
@login_required
def register_to_competition(name, id, number, kol_vo_player):
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
        if key in ["all_users", "registration"]:
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
                           competition_id=competition_id, kol_vo_player=kol_vo_player)


@app.route("/register_command_to_competition/<string:name>/<int:id>/<int:number>/<int:kol_vo_player>", methods=['GET', 'POST'])
@login_required
def register_command_to_competition(name, id, number, kol_vo_player):
    session = db_session.create_session()
    with open("static/json/competition.json") as file:
        data = json.load(file)
    form = RegisterGroupForm()
    competition_id = int(name.split("competition")[1])
    our_user = session.query(users.User).filter(users.User.id == id).first()
    all_users = session.query(users.User)
    all_users_list = []
    #Как команда доолжна выглядеть в json:
    #{"all_users":[],
    # "Группа1": [["Тигры", 1, 2, 3], ["Львы", 4, 5, 6]]
    # }
    for user in all_users:
        if not user.id in data["failed_competitions"][name]["all_users"]:
            all_users_list += [user]
    if request.method == "POST":
        # уведомление: тип;;информация
        # тип 0 - заявка в ожидании
        # тип 1 - заявка одобрена
        # тип 2- заявка отвергнута
        notification = "0;;" + name + ";;" + form.name.data + ";;"
        first_player = session.query(users.User).filter(users.User.id == form.id_player1.data).first()
        notification = notification + str(form.id_player1.data) + ";;"
        if kol_vo_player >= 2:
            second_player = session.query(users.User).filter(users.User.id == form.id_player2.data).first()
            notification = notification + str(form.id_player2.data) + ";;"
        if kol_vo_player >= 3:
            third_player = session.query(users.User).filter(users.User.id == form.id_player3.data).first()
            notification = notification + str(form.id_player3.data) + ";;"
        if kol_vo_player >= 4:
            fourth_player = session.query(users.User).filter(users.User.id == form.id_player4.data).first()
            notification = notification + str(form.id_player4.data) + ";;"
        if kol_vo_player >= 5:
            fifth_player = session.query(users.User).filter(users.User.id == form.id_player5.data).first()
            notification = notification + str(form.id_player5.data) + ";;"
        notification = notification.rstrip(";;")
        if first_player.id != id:
            if first_player.notifications is None:
                first_player.notifications = notification
            else:
                first_player.notifications = first_player.notifications + "%%" + notification
            session.merge(first_player)
        if kol_vo_player >= 2 and second_player.id != id:
            if second_player.notifications is None:
                second_player.notifications = notification
            else:
                second_player.notifications = second_player.notifications + "%%" + notification
            session.merge(second_player)
        if kol_vo_player >= 3 and third_player.id != id:
            if third_player.notifications is None:
                third_player.notifications = notification
            else:
                third_player.notifications = third_player.notifications + "%%" + notification
            session.merge(third_player)
        if kol_vo_player >= 4 and fourth_player.id != id:
            if fourth_player.notifications is None:
                fourth_player.notifications = notification
            else:
                fourth_player.notifications = fourth_player.notifications + "%%" + notification
            session.merge(fourth_player)
        if kol_vo_player >= 5 and fifth_player.id != id:
            if fifth_player.notifications is None:
                fifth_player.notifications = notification
            else:
                fifth_player.notifications = fifth_player.notifications + "%%" + notification
            session.merge(fifth_player)
        session.commit()
        return redirect(f"/competition/{competition_id}")
    return render_template("register_command_to_competition.html", form=form, name=name, id=id,
                           number=number, kol_vo_player=kol_vo_player,
                           all_users_list=all_users_list, competition_id=competition_id)


@app.route("/notifications")
@login_required
def notifications():
    session = db_session.create_session()
    user = session.query(users.User).filter(users.User.id == current_user.id).first()
    notifications = user.notifications
    notifications_list = []
    for notification in notifications.split("%%"):
        type = int(notification.split(";;")[0])
        value = notification.split(";;")[1:]
        competition = session.query(competitions.Competitions).filter(competitions.Competitions.id == int(value[0].split("competition")[1])).first()
        command_name = value[1]
        players = []
        for player_id in value[2:]:
            players += [session.query(users.User).filter(users.User.id == int(player_id)).first()]
        notifications_list += [[type, competition, command_name, players]]
        print([type, competition, command_name, players])
    return render_template("notifications.html", notifications_list=notifications_list)



@app.route("/unregister/<string:name>/<int:id>/<string:group>")
@login_required
def unregister(name, id, group):
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
    return redirect(f"/profile/{id}")


@app.route('/table_of_registered_users/<string:name>')
def table_of_users(name):
    with open("static/json/competition.json") as file:
        data = json.load(file)
    mas = data["failed_competitions"][name]
    keys = mas.keys()
    array_users = []
    sessions = db_session.create_session()
    for key in keys:
        if "all_users" != key and key != "registration":
            if len(mas[key]) != 0:
                array_users += [
                    [get_category(key)] + [sessions.query(users.User).filter(users.User.id == id).first() for id in
                                           mas[key]]]
    print(array_users)
    return render_template("table_of_registered_users.html", array_users=array_users)


@app.route('/competitions/<string:type>')
def all_competitions(type):
    check_all_competitions()
    session = db_session.create_session()
    competitions_list = session.query(competitions.Competitions)
    normal_type = "Командное" if type == "team" else "Индивидуальное"
    failed_list = []
    past_list = []
    for competition in competitions_list:
        if competition.team_competition == normal_type:
            if competition.endspiel == 0:
                failed_list += [competition]
            else:
                past_list += [competition]
    return render_template('competitions.html', failed_list=failed_list, past_list=past_list)


@app.route('/competitions_type')
def competition_type():
    return render_template('type_competition.html')


def check_all_competitions():
    session = db_session.create_session()
    with open("static/json/competition.json") as file:
        data = json.load(file)
    data_copy = data
    upcoming_competitions = data["failed_competitions"]
    keys = upcoming_competitions.keys()
    go_to_past = []
    for key in keys:
        competition = session.query(competitions.Competitions).filter(competitions.Competitions.url == key).first()
        date_end = get_data(competition.registration_end)
        date_start = get_data(competition.registration_start)
        date_event = get_data(competition.event_date_start)
        today_year = datetime.datetime.now().year
        today_month = datetime.datetime.now().month
        today_day = datetime.datetime.now().day
        if (date_event[2] < today_year or (
                date_event[2] == today_year and date_event[1] < today_month) or (
                date_event[2] == today_year and date_event[1] == today_month and date_event[
            0] < today_day)):
            go_to_past += [key]
            competition.endspiel = 1
            competition.registration = "01"
            session.merge(competition)
            session.commit()
            continue
        if competition.registration == "00" and (date_start[2] < today_year or (
                date_start[2] == today_year and date_start[1] < today_month) or (
                                                         date_start[2] == today_year and date_start[
                                                     1] == today_month and date_start[0] <= today_day)):
            competition.registration = "11"
            data_copy["failed_competitions"][key]["registration"] = 1
        if competition.registration == "11" and (date_end[2] < today_year or (
                date_end[2] == today_year and date_end[1] < today_month) or (
                                                         date_end[2] == today_year and date_end[1] == today_month and
                                                         date_end[0] < today_day)):
            data_copy["failed_competitions"][key]["registration"] = 0
            competition.registration = "01"
        session.merge(competition)
        session.commit()
    for key in go_to_past:
        new_competition = data_copy["failed_competitions"].pop(key, None)
        data_copy["past_competitions"].update([(key, new_competition)])
    with open("static/json/competition.json", "w") as file:
        json.dump(data_copy, file)


def get_data(date):
    date = date.split()
    dikt = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7,
            'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}
    return [int(date[0]), dikt[date[1]], int(date[2])]


def get_category(key):
    category_start = key.split(':')
    category = ""
    if category_start[-1] == "1":
        category += "М"
    else:
        category += "Ж"
    category += category_start[0] + "-" + category_start[1]
    return category


@app.route("/delete_competition/<int:id>")
def delete_competitions(id):
    session = db_session.create_session()
    competition = session.query(competitions.Competitions).filter(
        competitions.Competitions.id == id).first()
    with open("static/json/competition.json") as file:
        data = json.load(file)
    data["failed_competitions"].pop("competition" + str(id), None)
    data["past_competitions"].pop("competition" + str(id), None)
    with open("static/json/competition.json", "w") as file:
        json.dump(data, file)
    session.delete(competition)
    session.commit()
    try:
        os.remove(f"static/images/competition_image/competition_{id}.jpg")
    except Exception:
        pass
    return redirect("/competitions_type")


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
        sessions.add(new)
        sessions.commit()
        files = request.files.getlist("file_new")
        photo.save("static/images/news_image/news_" + str(new.id) + ".jpg")
        new.image = "static/images/news_image/news_" + str(new.id) + ".jpg"
        if str(files) != "[<FileStorage: '' ('application/octet-stream')>]":
            count_file = 0
            file_str_name = ''
            os.mkdir('static/files/new' + str(new.id))
            for file in files:
                count_file += 1
                file_extension = str(file).split('application/')[1][:-3]
                file_name = str(file).split("FileStorage: '")[1][:-25].split('.')[0]
                file.save(f"static/files/new{new.id}/{file_name}." + file_extension)
                file_str_name += file_name + '%%'
            new.files = "static/files/new" + str(new.id)
            new.file_name = file_str_name[:-2]
            new.count_file = count_file
        sessions.merge(new)
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
        shutil.rmtree(f"{new.files}")
    except Exception:
        pass
    return redirect("/")


@app.route('/single_new/<int:id>')
def single_item_new(id):
    session = db_session.create_session()
    new = session.query(news.News).filter(news.News.id == id).first()
    return render_template("single_new.html", new=new)


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
                                                 form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
def index():
    sessions = db_session.create_session()
    all_news = sessions.query(news.News)
    competitions_list = sessions.query(competitions.Competitions).filter(competitions.Competitions.endspiel == 0)
    return render_template("index.html", news_list=all_news, competitions_list=competitions_list)


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


@app.route('/not_authorized')
def not_auth():
    return render_template("not_authorized.html")


if __name__ == '__main__':
    main()
