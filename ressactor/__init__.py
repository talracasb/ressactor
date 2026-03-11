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

@app.route('/')
def index():
    if not 'username' in session:
        return redirect(url_for('auth.login'))
    return render_template("index.html", feed = feed)

