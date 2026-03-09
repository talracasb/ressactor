from .db import *
from flask import *
from argon2 import PasswordHasher

bp = Blueprint('auth', __name__, url_prefix='/auth')
ph = PasswordHasher()

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form["password"]
        hash = ph.hash(password)
        user = User(
            username = request.form["username"],
            password = hash
        )
        
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template("register.html")

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user: User = db.session.scalar(
                db.select(User).where(User.username == request.form["username"])
            )
            ph.verify(user.password, request.form["password"])
        except:
            abort(401)

        session['username'] = user.username
        session['id'] = user.id

        return redirect(url_for('index'))
    return render_template("login.html")

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))