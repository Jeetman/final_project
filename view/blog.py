from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from view.auth import login_required
from app import db
from models import User, Book

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
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
        genre = book.genre.split(",")
        books = Book.query.all()
        genres = []
        for b in books:
            genres.append( b.genre.split(",") )
        return render_template('blog/view.html', book=book, user=user, genre=genre,books=books,genres=genres)
    
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
