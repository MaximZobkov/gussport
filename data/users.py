import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date_of_birth = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    gender = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.String, default="user")
    image = sqlalchemy.Column(sqlalchemy.String, default="/static/images/avatar_image/unknown.jpg")
    middle_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    residence_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    residence_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    notifications = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    club = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f'{self.id}, {self.name}, {self.email}'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
