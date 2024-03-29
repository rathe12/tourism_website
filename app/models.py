from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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

    def __repr__(self):
        return f"Room('{self.type}', '{self.hotel.name}')"


# Модель для таблицы "RoomAvailability"
class RoomAvailability(db.Model):
    __bind_key__ = 'hotels_db'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey(
        'room.id'), nullable=False, index=True)
    # Дата заезда может быть не указана
    check_in_date = db.Column(db.Date, nullable=True)
    # Дата выезда может быть не указана
    check_out_date = db.Column(db.Date, nullable=True)

    room = db.relationship('Room', backref='availabilities')

    def __repr__(self):
        return f"RoomAvailability('{self.room.type}', '{self.check_in_date}', '{self.check_out_date}')"


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
    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)
    total_price = db.Column(db.Float)
    status_id = db.Column(db.Integer, db.ForeignKey(
        'booking_status.id'), nullable=False)

    status = db.relationship('BookingStatus')

    def __repr__(self):
        return f"Booking('{self.id}', '{self.user_id}', '{self.hotel_id}')"
