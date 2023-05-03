from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from view.auth import login_required
from app import db
from heapq import nlargest
from models import User, Book
from sqlalchemy import text, not_
import heapq, csv

bp = Blueprint('blog', __name__)



@bp.route('/')
@login_required
def index():
    recs = {}
    if g.user is not None:
        user = User.query.where(User.id == g.user.id).first()
        if user is not None:
            print(str(user))
            user_genres = user.genre.split(",")
            
            #get recomendations
            books = Book.query.all()
            for book in books:
                book_genres = book.genre.split(",")
                count = 0
                for genre in book_genres:
                    for u_genre in user_genres:
                        if genre == u_genre:
                            count = count + 1;
                recs[book] = count
            final = nlargest(5, recs, key = recs.get)
            genres = []
            for b in final:
                genres.append( b.genre.split(",") )
            return render_template('blog/index.html', books=final, genres=genres)
        return render_template('blog/index.html', books=[], genres=[])
    else:
        books = Book.query.all()
        genres = []
        for book in books:
            genres.append( book.genre.split(",") )
        return render_template('blog/index.html', books=books, genres=genres)
@bp.route('/search')
def search():
    isbn = request.args.get('query')
    print("Looking up book with isbn " + str(isbn))

    book = Book.query.where(Book.isbn == isbn).first()

    error = None
    if book is None:
        error = 'No posting found!'
    if error is None:
        user = User.query.where(User.username == book.uploader).first()
        bgenre = book.genre.split(",")

        #get recomendations

        genres = []
        for b in books:
            genres.append( b.genre.split(",") )

        return render_template('blog/view.html', book=book, user=user, genre=bgenre,books=books,genres=genres)
    
    flash(error)
    books = Book.query.all()
    genres = []
    for book in books:
        genres.append( book.genre.split(",") )
    return render_template('blog/index.html', books=books, genres=genres)
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        isbn = request.form['isbn']
        error = None

        if not isbn:
            error = 'ISBN is required.'

        if error is not None:
            flash(error)
        else:

            book = Book.query.where(Book.isbn == isbn).first()

            book.available = "True"
            
            user = User.query.where(User.id == g.user.id).first()
            book.uploader = user.username

            ## commit the changes to the database
            db.session.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')
