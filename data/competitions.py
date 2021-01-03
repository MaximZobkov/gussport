import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Competitions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'competitions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.TEXT)
    type = sqlalchemy.Column(sqlalchemy.TEXT)
    event_date_start = sqlalchemy.Column(sqlalchemy.DATE)
    event_time_start = sqlalchemy.Column(sqlalchemy.TIME)
    registration_start = sqlalchemy.Column(sqlalchemy.DATE)
    registration_end = sqlalchemy.Column(sqlalchemy.DATE)
    groups_count = sqlalchemy.Column(sqlalchemy.Integer)
    groups_description = sqlalchemy.Column(sqlalchemy.TEXT, default="")
    url = sqlalchemy.Column(sqlalchemy.TEXT)

