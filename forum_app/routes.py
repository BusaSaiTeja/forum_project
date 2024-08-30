from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, Thread, Post
from . import db
from flask_login import login_required, current_user

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('routes.home'))

@routes.route('/home')
@login_required
def home():
    threads = Thread.query.all()
    return render_template('home.html', user=current_user, threads=threads)

@routes.route('/create_thread', methods=['POST'])
@login_required
def create_thread():
    title = request.form['title']
    new_thread = Thread(title=title, author_id=current_user.id)
    db.session.add(new_thread)
    db.session.commit()
    return redirect(url_for('routes.home'))

@routes.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    posts = Post.query.filter_by(thread_id=thread_id).all()

    if request.method == 'POST':
        content = request.form.get('content')
        new_post = Post(content=content, author_id=current_user.id, thread_id=thread_id)
        db.session.add(new_post)
        db.session.commit()
        flash('Post added!', category='success')
        return redirect(url_for('routes.thread', thread_id=thread_id))

    is_author = (thread.author_id == current_user.id)
    return render_template('thread.html', thread=thread, posts=posts, is_author=is_author)

@routes.route('/delete_thread/<int:thread_id>', methods=['POST'])
@login_required
def delete_thread(thread_id):
    thread = Thread.query.get(thread_id)
    if thread and thread.author_id == current_user.id:
        db.session.delete(thread)
        db.session.commit()
        flash('Thread deleted successfully!', category='success')
    else:
        flash('You are not authorized to delete this thread.', category='error')
    return redirect(url_for('routes.home'))

@routes.route('/thread/<int:thread_id>/add_post', methods=['POST'])
@login_required
def add_post(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    content = request.form.get('content')
    if content:
        new_post = Post(content=content, author_id=current_user.id, thread_id=thread.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Post added successfully!', category='success')
    return redirect(url_for('routes.thread', thread_id=thread_id))


