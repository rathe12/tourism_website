from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from app.profile import create_blueprint
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf.csrf import CSRFProtect
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

    from .models import User, City, Hotel, HotelPhoto, Room, RoomAvailability, RoomImage, Booking, BookingStatus, AirCity, Aircraft, FlightClass, Seat, Flight, AirBooking

    class HotelView(ModelView):
        form_ajax_refs = {
            'city': {
                'fields': (City.name,)
            }
        }
    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

    # Регистрация моделей для административного интерфейса
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(City, db.session))
    admin.add_view(HotelView(Hotel, db.session))
    admin.add_view(ModelView(HotelPhoto, db.session))
    admin.add_view(ModelView(Room, db.session))
    admin.add_view(ModelView(RoomAvailability, db.session))
    admin.add_view(ModelView(RoomImage, db.session))
    admin.add_view(ModelView(Booking, db.session))
    admin.add_view(ModelView(BookingStatus, db.session))
    admin.add_view(ModelView(AirCity, db.session))
    admin.add_view(ModelView(Aircraft, db.session))
    admin.add_view(ModelView(FlightClass, db.session))
    admin.add_view(ModelView(Seat, db.session))
    admin.add_view(ModelView(Flight, db.session))
    admin.add_view(ModelView(AirBooking, db.session))

    return app
