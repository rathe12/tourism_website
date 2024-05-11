from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Модель для таблицы "User"
class User(UserMixin, db.Model):
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


# Модель для таблицы "City"
class City(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True, unique=True)

    def __repr__(self):
        return f"City('{self.name}')"


# Модель для таблицы "Hotels"
class Hotel(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey(
        'city.id'), nullable=False, index=True)
    image_url = db.Column(db.String(1000))
    description = db.Column(db.Text)
    rating = db.Column(db.Float)

    city = db.relationship('City', backref='hotels')

    def get_lowest_room_price(self):
        if self.rooms:
            return min(room.price_per_night for room in self.rooms)
        return None

    def __repr__(self):
        return f"Hotel('{self.name}', '{self.city.name}')"


# Модель для таблицы "HotelPhotos"
class HotelPhoto(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey(
        'hotel.id'), nullable=False, index=True)
    photo_url = db.Column(db.String(1000))

    hotel = db.relationship('Hotel', backref='photos')

    def __repr__(self):
        return f"HotelPhoto('{self.photo_url}')"


class Room(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey(
        'hotel.id'), nullable=False, index=True)
    type = db.Column(db.String(100))
    price_per_night = db.Column(db.Float)
    description = db.Column(db.Text)

    hotel = db.relationship('Hotel', backref='rooms')

    def get_total_price(self, check_in_date, check_out_date):
        num_days = (check_out_date - check_in_date).days
        return num_days * self.price_per_night

    def __repr__(self):
        return f"Room('{self.type}', '{self.hotel.name}')"


# Модель для таблицы "RoomAvailability"
class RoomAvailability(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey(
        'room.id'), nullable=False, index=True)
    room_number = db.Column(db.Integer, nullable=False)
    # Дата заезда может быть не указана
    check_in_date = db.Column(db.Date, nullable=True)
    # Дата выезда может быть не указана
    check_out_date = db.Column(db.Date, nullable=True)

    room = db.relationship('Room', backref='availabilities')

    def __repr__(self):
        return f"RoomAvailability('{self.room.type}','{self.room_number}', '{self.check_in_date}', '{self.check_out_date}')"

# Модель для таблицы "RoomImages"


class RoomImage(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey(
        'room.id'), nullable=False, index=True)
    image_url = db.Column(db.String(1000))

    room = db.relationship('Room', backref='images')

    def __repr__(self):
        return f"RoomImage('{self.image_url}')"


# Модель для таблицы "BookingStatus"
class BookingStatus(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, index=True, unique=True)

    def __repr__(self):
        return f"BookingStatus('{self.name}')"


class Booking(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    hotel_id = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)
    total_price = db.Column(db.Float)
    status_id = db.Column(db.Integer, db.ForeignKey(
        'booking_status.id'), nullable=False)

    status = db.relationship('BookingStatus')

    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(50))
    passport_number = db.Column(db.String(50))
    passport_series = db.Column(db.String(50))

    def __repr__(self):
        return f"Booking('{self.id}', '{self.user_id}', '{self.hotel_id}')"


# Таблица для самолетов
class Aircraft(db.Model):
    # Уникальный идентификатор самолета
    id = db.Column(db.Integer, primary_key=True)
    aircraft_number = db.Column(
        db.String(20), unique=True, nullable=False)  # Номер самолета
    model = db.Column(db.String(100), nullable=False)  # Модель самолета

# Таблица для классов обслуживания


class Class(db.Model):
    # Уникальный идентификатор класса
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Название класса

# Таблица для мест в самолетах


class Seat(db.Model):
    # Уникальный идентификатор места
    id = db.Column(db.Integer, primary_key=True)
    aircraft_id = db.Column(db.Integer, db.ForeignKey(
        'aircraft.id'), nullable=False)  # Идентификатор самолета
    class_id = db.Column(db.Integer, db.ForeignKey(
        'class.id'), nullable=False)  # Идентификатор класса
    seat_number = db.Column(db.String(10), nullable=False)  # Номер места

# Модель для таблицы рейсов


class Flight(db.Model):
    # Уникальный идентификатор рейса
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(
        db.String(20), unique=True, nullable=False)  # Номер рейса
    origin_city_id = db.Column(db.Integer, db.ForeignKey(
        'city.id'), nullable=False)  # Идентификатор города отправления
    destination_city_id = db.Column(db.Integer, db.ForeignKey(
        'city.id'), nullable=False)  # Идентификатор города назначения
    departure_time = db.Column(
        db.DateTime, nullable=False)  # Время отправления
    arrival_time = db.Column(db.DateTime, nullable=False)  # Время прибытия
    aircraft_id = db.Column(db.Integer, db.ForeignKey(
        'aircraft.id'), nullable=False)  # Идентификатор самолета
    # Связь с таблицей бронирований
    bookings = db.relationship('AirBooking', backref='flight', lazy=True)

# Модель для таблицы бронирования


class AirBooking(db.Model):
    # Уникальный идентификатор бронирования
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)  # Идентификатор пользователя
    flight_id = db.Column(db.Integer, db.ForeignKey(
        'flight.id'), nullable=False)  # Идентификатор рейса
    seat_id = db.Column(db.Integer, db.ForeignKey(
        'seat.id'), nullable=False)  # Идентификатор места
    class_id = db.Column(db.Integer, db.ForeignKey(
        'class.id'), nullable=False)  # Идентификатор класса
    total_price = db.Column(db.Float, nullable=False)  # Обща
