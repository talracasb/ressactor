from flask import *
import os

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

@app.route('/')
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return 'You are not logged in'

