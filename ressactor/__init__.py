from collections import defaultdict

from flask import *
import os
import feedparser

from . import auth
from .db import *

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    )

    os.makedirs(app.instance_path, exist_ok=True)
    app.register_blueprint(auth.bp)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app

app = create_app()
feed = feedparser.parse(f"{app.instance_path}/feed.xml")

@app.route('/comment/<path:rss_id>', methods=["POST"])
def comment(rss_id):
    if not 'username' in session:
        return "Not logged in", 401

    body = request.data.decode()
    
    post = db.session.query(Post).filter_by(rss_id=rss_id).first()
    if post is None:
        post = Post(rss_id=rss_id)
        db.session.add(post)
        db.session.flush()

    comment = Comment(
        content=body,
        user_id=session["id"],
        post_id=post.id
    )

    db.session.add(comment)
    db.session.commit()
    return "Added comment", 200

@app.route('/')
def index():
    if not 'username' in session:
        return redirect(url_for('auth.login'))
    
    comments = defaultdict(list)
    for comment in db.session.query(Comment).all():
        comments[comment.post.rss_id].append(comment)
    
    for x in feed.entries:
        x.id = x.id.split("#", 1)[0]
    
    return render_template("index.html",
        feed=feed,                   
        comments = comments
    )
