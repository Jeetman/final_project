import os
from datetime import datetime
import csv, json
from flask import Flask, redirect, render_template, request, send_from_directory, url_for, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, static_folder='static')

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Book, User
from view import auth
app.register_blueprint(auth.bp)

from view import blog
app.register_blueprint(blog.bp)
app.add_url_rule('/', endpoint='index')

# a simple page that says hello
@app.route('/upload', methods=['GET'])
def upload_books():
    # Open the CSV file
    with open('books.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            book_title = row['Book Title']
            isbn = row['ISBN']
            author = row['Author']
            genre = row['Genre 1']
            genre2 = row['Genre 2']
            genre3 = row['Genre 3']
            genre4 = row['Genre 4']
            genreAll = genre + "," + genre2 + "," + genre3 + "," + genre4
            ## create a new Post object
            new_book = Book(isbn=isbn,title=book_title, author=author, genre=genreAll, available="False")

            ## add the new post to the session
            db.session.add(new_book)

            ## commit the changes to the database
            db.session.commit()
    return str(Book.query.all())
# a simple page that says hello
@app.route('/books', methods=['GET'])
def books():
    books = Book.query.all()
    book_list = []
    for book in books:
        book_dict = {
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'genre': book.genre
        }
        book_list.append(book_dict)
    return jsonify(book_list)

# a simple page that says hello
@app.route('/users', methods=['GET'])
def users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_dict = {
            'id': user.id,
            'username': user.username,
            'genre': user.genre
        }
        user_list.append(user_dict)
    return jsonify(user_list)

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

if __name__ == '__main__':
    app.run()
