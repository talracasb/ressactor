from collections import defaultdict

from flask import *
import os
import feedparser

from . import auth
from .db import *

# Contains all the config for our flask app.
# We put it here just to clean things up.
def create_app():
    # Make the app, and set the database URL (basically, where the database is.)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    )

    # Make the "instance directory".
    # This basically refers to the directory flask uses for resources which are,
    # in some sense, temporary or specific to a given instance of the app.
    os.makedirs(app.instance_path, exist_ok=True)

    # Register the auth blueprint. This basically lets us create routes and other stuff
    # in a separate file, cleaning things up a bit.
    app.register_blueprint(auth.bp)

    # Initialize the database.
    db.init_app(app)
    with app.app_context():
        # Create all of our database models within the database.
        db.create_all()

    return app

app = create_app()

# Parse the RSS feed at app start.
feed = feedparser.parse(f"{app.instance_path}/feed.xml")

# Route for adding comments.
# To be specific, this is called by the javascript in the index.html
# file when a user wants to make a comment. This allows us to make the app
# more dynamic.
@app.route('/comment/<path:rss_id>', methods=["POST"])
def comment(rss_id):
    if not 'username' in session:
        return abort(401, "Not logged in")

    body = request.data.decode()
    if len(body) == 0:
        return abort(400)
    
    # If there isn't a "Post" object in the database associated with the post we
    # are trying to comment on, then create it.
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
    
    if len(feed.entries) == 0:
        return abort(500, "No RSS entries found!")
    
    # Sort the comments based on the id of the post they belong to.
    comments = defaultdict(list)
    for comment in db.session.query(Comment).all():
        comments[comment.post.rss_id].append(comment)
    
    # Trim some excess from the feed entries' id.
    for x in feed.entries:
        x.id = x.id.split("#", 1)[0]
    
    return render_template("index.html",
        feed=feed,                   
        comments = comments
    )
