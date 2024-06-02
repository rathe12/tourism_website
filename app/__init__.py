from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from app.profile import create_blueprint
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user
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
    from app.routes import book_seats
    app.register_blueprint(create_blueprint(), url_prefix='/profile')

    from .models import User, City, Hotel, HotelPhoto, Room, RoomAvailability, RoomImage, Booking, BookingStatus, AirCity, Aircraft, FlightClass, Seat, Flight, AirStatus, AirBooking

    class HotelView(ModelView):
        def is_accessible(self):
            # Проверяем, является ли текущий пользователь администратором
            return current_user.is_authenticated and current_user.is_admin
        form_ajax_refs = {
            'city': {
                'fields': (City.name,)
            }
        }
    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

    class MyModelView(ModelView):
        def is_accessible(self):
            # Проверяем, является ли текущий пользователь администратором
            return current_user.is_authenticated and current_user.is_admin

    admin.add_view(MyModelView(User, db.session))
    # Регистрация моделей для административного интерфейса
    admin.add_view(MyModelView(City, db.session))
    admin.add_view(HotelView(Hotel, db.session))
    admin.add_view(MyModelView(HotelPhoto, db.session))
    admin.add_view(MyModelView(Room, db.session))
    admin.add_view(MyModelView(RoomAvailability, db.session))
    admin.add_view(MyModelView(RoomImage, db.session))
    admin.add_view(MyModelView(Booking, db.session))
    admin.add_view(MyModelView(BookingStatus, db.session))
    admin.add_view(MyModelView(AirCity, db.session))
    admin.add_view(MyModelView(Aircraft, db.session))
    admin.add_view(MyModelView(FlightClass, db.session))
    admin.add_view(MyModelView(Seat, db.session))
    admin.add_view(MyModelView(Flight, db.session))
    admin.add_view(MyModelView(AirStatus, db.session))
    admin.add_view(MyModelView(AirBooking, db.session))

    return app
