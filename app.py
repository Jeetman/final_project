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
from models import Book
from view import auth
app.register_blueprint(auth.bp)

from view import blog
app.register_blueprint(blog.bp)
app.add_url_rule('/', endpoint='index')

# a simple page that says hello
@app.route('/books', methods=['GET'])
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

if __name__ == '__main__':
    app.run()
