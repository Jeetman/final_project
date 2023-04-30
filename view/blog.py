from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from azure.cognitiveservices.personalizer import PersonalizerClient
from azure.cognitiveservices.personalizer.models import RankableAction, RewardRequest, RankRequest
from msrest.authentication import CognitiveServicesCredentials
from view.auth import login_required
from app import db
from models import User, Book
from sqlalchemy import text, not_
import heapq, csv
key = "d2029f0050c34f1dac4cbd1f97da6bd6"
endpoint = "https://book-recommender-3.cognitiveservices.azure.com/"
client = PersonalizerClient(endpoint, CognitiveServicesCredentials(key))
# Open the CSV file
actions_and_features = {}
book_attr = []
# Instantiate a Personalizer client
genre_list = ["Fiction","Adventure","Romance","Modernist","Coming-of-Age","Psychological","Existentialism"]
# Open the CSV file
unique_genre_set = set()
with open('books.csv') as csv_file:
    # Read the data from the CSV file as a dictionary
    csv_reader = csv.DictReader(csv_file)
    # Initialize an empty dictionary to store the book information
    books = {}
    # Loop through each row of the CSV file
    for row in csv_reader:
        # Create a dictionary to store the book information
        book_info = {
            "title": row['Book Title'],
           # "year": row['Year'],
            "Author": row['Author']
        }
        genre = {}
        # genre_list = []
        for genre_ in genre_list:
          genre[genre_] = False

        if row['Genre 1'] is not None and row['Genre 1'] != '':
            genre[row['Genre 1']] = True
            genre_list.append(row['Genre 1'])
            unique_genre_set.add(row['Genre 1'])
        if row['Genre 2'] is not None and row['Genre 2'] != '':
            genre[row['Genre 2']] = True
            genre_list.append(row['Genre 2'])
            unique_genre_set.add(row['Genre 2'])
        if row['Genre 3'] is not None and row['Genre 3'] != '':
            genre[row['Genre 3']] = True
            genre_list.append(row['Genre 3'])
            unique_genre_set.add(row['Genre 3'])
        if row['Genre 4'] is not None and row['Genre 4'] != '':
            genre[row['Genre 4']] = True
            genre_list.append(row['Genre 4'])
            unique_genre_set.add(row['Genre 4'])

        book_data = {
            "book_info": book_info,
            "genre": genre
            # "genre": set(genre_list)
            # "attributes": attributes
        }
        book_attr.append(row['Book Title'])
        book_attr.append(row['Author'])
        #book_attr.append(row['ISBN'])
        books[row['ISBN']] = book_data
    actions_and_features = books
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
    print("arrived at index")
    print(actions_and_features)
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
        profile = [{'genre_preferences':set(bgenre[:3])}]
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
