from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from app.profile import create_blueprint

# Создание экземпляра объекта SQLAlchemy
db = SQLAlchemy()

app = Flask(__name__)

# Настройка конфигурации приложения
app.config.from_object(Config)
# Инициализация расширений Flask
db.init_app(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'


def create_app():

    from app import routes, models
    app.register_blueprint(create_blueprint(), url_prefix='/profile')
    return app
