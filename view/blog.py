from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankableAction, RewardRequest, RankRequest
from msrest.authentication import CognitiveServicesCredentials
from view.auth import login_required
from app import db, actions_and_features
from models import User, Book
from sqlalchemy import text, not_
import heapq, csv
key = "9a506bda75c644d2ad1870de72c4e070"
endpoint = "https://book-recommender-2.cognitiveservices.azure.com/"
client = PersonalizerClient(endpoint, CognitiveServicesCredentials(key))

bp = Blueprint('blog', __name__)

def get_actions():
    res = []
    for action_id, feat in actions_and_features.items():
        action = RankableAction(id=action_id, features=[feat])
        res.append(action)
    return res

@bp.route('/')
@login_required
def index():
    if g.user is not None:
        user = User.query.where(User.id == g.user.id).first()
        if user is not None:
            print(str(user))
            user_genres = user.genre.split(",")
            profile = [{'genre_preferences':set(user_genres)}]
            actions = get_actions()
            rank_request = RankRequest(actions=actions, context_features=profile)
            response = client.rank(rank_request=rank_request)
            ranked_actions = [(action.id, action.probability) for action in response.ranking]
            top_actions = heapq.nlargest(5, ranked_actions, key=lambda x: x[1])
            print(top_actions)
            #get recomendations
            books = []
            for rec in top_actions:
                isbn = rec[0]
                data = Book.query.where(Book.isbn == isbn).first()
                books.append(data)
            genres = []
            for b in books:
                genres.append( b.genre.split(",") )
            return render_template('blog/index.html', books=books, genres=genres)
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
        search_term = bgenre[0]
        books = db.session.query(Book).filter(text("genre LIKE '%' || :search_term || '%'")).params(search_term=search_term).filter(not_(Book.isbn == isbn)).limit(5).all()
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
