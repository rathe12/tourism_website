from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Hotels(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(128))
    # Предполагается, что здесь будет храниться ссылка на фото
    photo = db.Column(db.String(256))
    name = db.Column(db.String(128), unique=True)

    def __repr__(self):
        return '<Hotel {}>'.format(self.name)