import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.TEXT, default="/static/images/news_image/default_news.jpg")


