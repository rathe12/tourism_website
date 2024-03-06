
from flask import Blueprint


profile_bp = Blueprint('profile', __name__,
                       template_folder='templates', static_folder='static')


def create_blueprint():
    from . import routes
    return profile_bp
