from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import validates, relationship
from sqlalchemy.sql.expression import func

from app import db


class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))

    def __str__(self):
        return self.name

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey('restaurant.id', ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)

    @validates('rating')
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    
    posts = relationship("Post", back_populates="author")

class Post(db.Model):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    created = Column(TIMESTAMP, default=func.now())
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    
    author = relationship("User", back_populates="posts")

class Book(db.Model):
    __tablename__ = 'books'
    isbn = Column(Integer, primary_key=True)
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    uploader = Column(String,nullable=True)
    available = Column(String,nullable=False)
    genre = Column(String,nullable=False)

    def __repr__(self):
        return f"<Book(isbn='{self.isbn}', title='{self.title}', author='{self.author}')>"