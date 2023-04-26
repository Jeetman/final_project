from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import validates, relationship
from sqlalchemy.sql.expression import func

from app import db


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    genre = Column(String,nullable=False)
    def __repr__(self):
            return f"<User(id='{self.id}', name='{self.username}', genre='{self.genre}')>"
class Book(db.Model):
    __tablename__ = 'books'
    isbn = Column(String, primary_key=True)
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    uploader = Column(String,nullable=True)
    available = Column(String,nullable=False)
    genre = Column(String,nullable=False)

    def __repr__(self):
        return f"<Book(isbn='{self.isbn}', title='{self.title}', author='{self.author}')>"