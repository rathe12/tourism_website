from . import app, db
from flask import render_template, flash, redirect, url_for, request, session
from app.forms import RegistrationForm, LoginForm, ResidenceForm, BookingHotelForm, AirplaneTicketsForm
from app.models import User, Hotel, City, Room, RoomAvailability, Booking, BookingStatus
# from config import dbx
from flask_login import login_user, current_user, login_required
from datetime import datetime, date
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

menu = [{"name": "Акции", "url": "/"},
        {"name": "Туры", "url": "/tours"},
        {"name": "Проживание", "url": "/accommodation"},
        {"name": "Авиабилеты", "url": "/air_tickets"},
        {"name": "Профиль", "url": "/profile"}]


@app.route('/')
def index():
    return render_template('index.html', menu=menu, title='Акции')


@app.route('/tours')
def tours():
    return render_template('tours.html', menu=menu, title='Туры')


@app.route('/accommodation', methods=['GET', 'POST'])
def accommodation():
    form = ResidenceForm()
    if form.validate_on_submit():
        destination = form.destination.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        return redirect(url_for('hotels', destination=destination, start_date=start_date, end_date=end_date))
    return render_template('accommodation.html', form=form, menu=menu, title='Проживание')


@app.route('/hotels', methods=['GET', 'POST'])
def hotels():
    form = ResidenceForm()
    if form.validate_on_submit():
        destination = form.destination.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        return redirect(url_for('hotels', destination=destination, start_date=start_date, end_date=end_date))
    # Получаем данные из параметров URL
    destination = request.args.get('destination')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    session['start_hotel_date'] = request.args.get('start_date')
    session['end_hotel_date'] = request.args.get('end_date')

    def generate_star_rating(rating):
        full_stars = int(rating)  # Целые звезды
        half_star = rating - full_stars >= 0.5  # Половинка звезды, если остаток >= 0.5
        html = ''

        # Добавляем целые звезды
        for _ in range(full_stars):
            html += f'<img src="{url_for("static", filename="images/star.png")}" alt="star" class="star-icon">'

        # Добавляем половинку звезды, если есть
        if half_star:
            html += f'<img src="{url_for("static", filename="images/half_star.png")}" alt="half-star" class="star-icon">'

        # Возвращаем сгенерированный HTML-код
        return html

    def get_distance(city, address):
        geolocator = Nominatim(user_agent="geo_distance_calculator")

        # Получаем координаты адреса и центра города
        address_location = geolocator.geocode(address)
        city_location = geolocator.geocode(city)

        if address_location is None or city_location is None:
            return "Не удалось найти одно из местоположений. Проверьте правильность введенных данных."

        # Вычисляем расстояние между двумя точками в километрах
        distance = geodesic((address_location.latitude, address_location.longitude),
                            (city_location.latitude, city_location.longitude)).kilometers

        return f"{distance:.2f} км до центра"
        # Здесь вы можете выполнить необходимые операции с этими данными, например, передать их в шаблон
    # Или выполнить запрос к базе данных для получения данных о гостиницах
    city = City.query.filter_by(name=destination).first()
    if city:
        hotels = Hotel.query.filter_by(city_id=city.id).all()
    return render_template('hotels.html', form=form, hotels=hotels, destination=destination, start_date=start_date, end_date=end_date, generate_star_rating=generate_star_rating, get_distance=get_distance, menu=menu)


@app.route('/hotel/<int:hotel_id>')
def show_hotel(hotel_id):
    hotel = Hotel.query.get(hotel_id)
    start_date = datetime.strptime(session.get(
        'start_hotel_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(session.get(
        'end_hotel_date'), '%Y-%m-%d').date()
    availability_room_type = []
    availability_room_info = []
    room_numbers = []
    all_room_numbers = []

    for room in hotel.rooms:
        availability = RoomAvailability.query.filter_by(room_id=room.id).all()
        for room_info in availability:
            if room_info.room_number not in room_numbers:
                all_room_numbers.append(room_info.room_number)
                if room_info.check_out_date > datetime.today().date():
                    room_numbers.append(room_info.room_number)

    multi_dict = {key: [] for key in room_numbers}

    for numbers in room_numbers:
        number_all_time = RoomAvailability.query.filter_by(
            room_number=numbers).all()
        for rm_number in number_all_time:
            if rm_number.check_out_date > datetime.today().date():
                print(rm_number)
                multi_dict[rm_number.room_number].append(
                    [rm_number.check_in_date, rm_number.check_out_date])

    def check_intersection(start_date, end_date, date_dict):
        # Преобразование строковых дат в объекты datetime.date
        intersecting_keys = []
        for key in date_dict:
            for date_range in date_dict[key]:
                if (start_date <= date_range[1]) and (end_date >= date_range[0]):
                    intersecting_keys.append(key)
                    break  # Выход из внутреннего цикла после первого совпадения
        return intersecting_keys

    intersecting_keys = check_intersection(start_date, end_date, multi_dict)

    if intersecting_keys:
        print(f"Пересечение с ключами {intersecting_keys} обнаружено!")
    else:
        print("Пересечение отсутствует.")

    for all_rm_nmbr in set(all_room_numbers):
        if all_rm_nmbr not in intersecting_keys:
            info = RoomAvailability.query.filter_by(
                room_number=all_rm_nmbr).first()
            availability_room_info.append(
                {'room_id': info.room_id, 'room_number': info.room_number})

            availability_room_type.append(info.room)

    session['availability_room_info'] = availability_room_info
    print(session.get('availability_room_info'))

    print(multi_dict)

    return render_template('hotel.html', hotel=hotel, menu=menu, rooms=availability_room_type)


@app.route('/booking/<int:hotel_id>/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_hotel(hotel_id, room_id):
    start_date = datetime.strptime(session.get(
        'start_hotel_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(session.get(
        'end_hotel_date'), '%Y-%m-%d').date()
    hotel = Hotel.query.get_or_404(hotel_id)
    room = Room.query.get_or_404(room_id)
    room_info = Room.query.get(room_id)
    total_price = room.get_total_price(start_date, end_date)
    rooms = session.get('availability_room_info')
    room_dict = {}
    for room in rooms:
        room_dict[room['room_id']] = room['room_number']
    room_number = room_dict.get(room_id)
    form = BookingHotelForm()
    if form.validate_on_submit():
        new_availability = RoomAvailability(
            room_id=room_id,
            room_number=room_number,
            check_in_date=start_date,
            check_out_date=end_date,
        )
        db.session.add(new_availability)
        print(total_price)
        booking = Booking(
            user_id=current_user.id,
            hotel_id=hotel_id,
            room_id=room_id,
            room_number=room_number,
            check_in_date=start_date,
            check_out_date=end_date,
            total_price=total_price,
            status_id=1,
            name=form.name.data,
            phone_number=form.phone_number.data,
            passport_number=form.passport_number.data,
            passport_series=form.passport_series.data
        )
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for('profile.myorders'))
    return render_template('booking_hotel.html', hotel=hotel, room=room_info, total_price=total_price, form=form, menu=menu)


@app.route('/air_tickets')
def air_tickets():
    form = AirplaneTicketsForm()
    if form.validate_on_submit():
        pass
    return render_template('air_tickets.html', form=form, menu=menu, title='Авиабилеты')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile.myaccount'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, вы успешно зарагестрировались!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистраця', form=form, menu=menu)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile.myaccount', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неврный логин или пароль', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        return redirect(url_for('profile.myaccount', username=current_user.username))
    return render_template('login.html', title='Войти', form=form, menu=menu)


@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    return redirect(url_for('login'))
