import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Competitions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'competitions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.TEXT)
    type = sqlalchemy.Column(sqlalchemy.TEXT)
    short_description = sqlalchemy.Column(sqlalchemy.TEXT)
    image = sqlalchemy.Column(sqlalchemy.TEXT)
    event_date_start = sqlalchemy.Column(sqlalchemy.String)
    event_time_start = sqlalchemy.Column(sqlalchemy.String)
    registration_start = sqlalchemy.Column(sqlalchemy.String)
    registration_end = sqlalchemy.Column(sqlalchemy.String)
    groups_count = sqlalchemy.Column(sqlalchemy.Integer)
    groups_description = sqlalchemy.Column(sqlalchemy.TEXT, default="")
    url = sqlalchemy.Column(sqlalchemy.TEXT)
    # endspiel: 0-незавершено, 1-завершено
    endspiel = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    registration = sqlalchemy.Column(sqlalchemy.Integer, default=0)
