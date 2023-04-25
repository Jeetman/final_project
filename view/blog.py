from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from view.auth import login_required
from app import db
from models import User, Post, Book

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    posts = db.session.query(Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username) \
                      .join(User, Post.author_id == User.id) \
                      .order_by(Post.created.desc()) \
                      .all()
    return render_template('blog/index.html', posts=posts)
@bp.route('/search')
def search():
    isbn = request.args.get('query')
    print("Looking up book with isbn " + str(isbn))

    book = Book.query.where(Book.isbn == isbn).first()

    error = None
    if book is None:
        error = 'No posting found!'
    if error is None:
        user = User.query.where(User.id == book.uploader).first()
        return render_template('blog/view.html', book=book, user=user)
    
    flash(error)
    posts = db.session.query(Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username) \
                      .join(User, Post.author_id == User.id) \
                      .order_by(Post.created.desc()) \
                      .all()
    return render_template('blog/index.html', posts=posts)
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            # create a new Post object
            new_post = Post(title=title, body=body, author_id=g.user.id)

            # add the new post to the session
            db.session.add(new_post)

            # commit the changes to the database
            db.session.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):

    post = Post.query \
        .join(User) \
        .filter(Post.id == id) \
        .with_entities(Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username) \
        .first()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = Post.query.filter_by(id=id).first()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog.index'))