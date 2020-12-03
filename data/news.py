import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.VARCHAR, default="/static/images")
    created_date = sqlalchemy.Column(sqlalchemy.DATE)


