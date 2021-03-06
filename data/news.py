import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.TEXT)
    files = sqlalchemy.Column(sqlalchemy.String)
    count_file = sqlalchemy.Column(sqlalchemy.Integer)
    file_name = sqlalchemy.Column(sqlalchemy.String)