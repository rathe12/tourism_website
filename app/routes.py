# Подразумевается, что модели импортированы из вашего модуля
from . import app, db
import json
from flask import render_template, flash, redirect, url_for, request, session
from app.forms import RegistrationForm, LoginForm, ResidenceForm, BookingHotelForm, AirplaneTicketsForm
from app.models import User, City, Hotel, HotelPhoto, Room, RoomAvailability, RoomImage, BookingStatus, Booking, AirCity, Aircraft, FlightClass, Seat, Flight, AirBooking
# from config import dbx
from flask_login import login_user, current_user, login_required
from datetime import datetime, date, timedelta
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


@app.route('/air_tickets', methods=['GET', 'POST'])
def air_tickets():
    form = AirplaneTicketsForm()
    if form.validate_on_submit():
        departure_city = form.departure_city.data
        arrival_city = form.arrival_city.data
        departure_date = form.departure_date.data
        return_date = form.return_date.data
        passengers = form.passengers.data
        flight_class = form.flight_class.data

        session['passengers'] = passengers
        session['flight_class'] = flight_class

        return redirect(url_for('search_flights', departure_city=departure_city, arrival_city=arrival_city, departure_date=departure_date, return_date=return_date, passengers=passengers, flight_class=flight_class))
    return render_template('air_tickets.html', form=form, menu=menu, title='Авиабилеты')


# @app.route('/search_flights', methods=['GET', 'POST'])
# def search_flights():
#     form = AirplaneTicketsForm()
#     if form.validate_on_submit():
#         departure_city = form.departure_city.data
#         arrival_city = form.arrival_city.data
#         departure_date = form.departure_date.data
#         return_date = form.return_date.data
#         passengers = form.passengers.data
#         flight_class = form.flight_class.data
#         # Передача данных для дальнейшей обработки
#         return redirect(url_for('search_flights', departure_city=departure_city, arrival_city=arrival_city, departure_date=departure_date, return_date=return_date, passengers=passengers, flight_class=flight_class))

#     departure_city = request.args.get('departure_city')
#     arrival_city = request.args.get('arrival_city')
#     departure_date = request.args.get('departure_date')
#     return_date = request.args.get('departure_date')
#     passengers = int(request.args.get('passengers'))
#     flight_class = FlightClass.query.filter_by(
#         name=request.args.get('flight_class')).first().id
#     session['departure_date'] = request.args.get('departure_date')
#     departure_city_id = AirCity.query.filter_by(
#         name=departure_city).first().id
#     arrival_city_id = AirCity.query.filter_by(name=arrival_city).first().id

#     def calculate_flight_duration(departure_time, arrival_time):
#         return arrival_time - departure_time

#     def search_direct_flights(departure_city, arrival_city, departure_date, passengers, flight_class):
#         departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
#         flights = Flight.query.filter(
#             Flight.origin_city_id == departure_city,
#             Flight.destination_city_id == arrival_city,
#             db.func.date(Flight.departure_time) == departure_date
#         ).all()

#         suitable_flights = []
#         for flight in flights:
#             available_seats = Seat.query.filter_by(
#                 aircraft_id=flight.aircraft_id,
#                 flight_class_id=flight_class
#             ).count()
#             if available_seats >= passengers:
#                 flight_duration = calculate_flight_duration(
#                     flight.departure_time, flight.arrival_time)
#                 suitable_flights.append((flight, flight_duration))
#         return suitable_flights

#     def search_flights_with_transfers(departure_city, arrival_city, departure_date, passengers, flight_class):
#         departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
#         first_leg_flights = Flight.query.filter(
#             Flight.origin_city_id == departure_city,
#             db.func.date(Flight.departure_time) == departure_date
#         ).all()

#         suitable_flights_with_transfers = []

#         for first_flight in first_leg_flights:
#             transfer_city_id = first_flight.destination_city_id

#             # Ищем рейсы, которые вылетают в тот же день после прибытия первого рейса или на следующий день
#             second_leg_flights = Flight.query.filter(
#                 Flight.origin_city_id == transfer_city_id,
#                 Flight.destination_city_id == arrival_city,
#                 db.or_(
#                     db.and_(
#                         db.func.date(
#                             Flight.departure_time) == first_flight.arrival_time.date(),
#                         Flight.departure_time > first_flight.arrival_time
#                     ),
#                     db.func.date(
#                         Flight.departure_time) == first_flight.arrival_time.date() + timedelta(days=1)
#                 )
#             ).all()

#             for second_flight in second_leg_flights:
#                 first_leg_seats = Seat.query.filter_by(
#                     aircraft_id=first_flight.aircraft_id,
#                     flight_class_id=flight_class
#                 ).count()
#                 second_leg_seats = Seat.query.filter_by(
#                     aircraft_id=second_flight.aircraft_id,
#                     flight_class_id=flight_class
#                 ).count()

#                 if first_leg_seats >= passengers and second_leg_seats >= passengers:
#                     transfer_duration = second_flight.departure_time - first_flight.arrival_time
#                     total_travel_duration = calculate_flight_duration(first_flight.departure_time, first_flight.arrival_time) + \
#                         calculate_flight_duration(second_flight.departure_time, second_flight.arrival_time) + \
#                         transfer_duration
#                     suitable_flights_with_transfers.append(
#                         (first_flight, second_flight, transfer_duration, total_travel_duration))

#         return suitable_flights_with_transfers

#     def search_all_flights(departure_city, arrival_city, departure_date, passengers, flight_class):
#         direct_flights = search_direct_flights(
#             departure_city, arrival_city, departure_date, passengers, flight_class)
#         connecting_flights = search_flights_with_transfers(
#             departure_city, arrival_city, departure_date, passengers, flight_class)
#         return direct_flights, connecting_flights

#     direct_flights, connecting_flights = search_all_flights(departure_city_id, arrival_city_id,
#                                                             departure_date, passengers, flight_class)

#     return render_template('search_flights.html', direct_flights=direct_flights, connecting_flights=connecting_flights, form=form, menu=menu, title='Авиабилеты')


@app.route('/search_flights', methods=['GET', 'POST'])
def search_flights():

    def calculate_final_price(base_price, departure_date, agency_fee_percentage, booking_date=date.today()):

        def apply_time_based_markup(base_price, days_to_departure):
            if days_to_departure > 30:
                markup = 1.0  # без надбавки
            elif 14 < days_to_departure <= 30:
                markup = 1.1  # +10% к базовой цене
            elif 7 < days_to_departure <= 14:
                markup = 1.2  # +20% к базовой цене
            else:
                markup = 1.5  # +50% к базовой цене
            return base_price * markup

        def apply_seasonal_markup(price, booking_date):
            # Предположим, что высокий сезон - лето (июнь, июль, август)
            high_season_months = [6, 7, 8]
            if booking_date.month in high_season_months:
                season_markup = 1.2  # +20% к цене
            else:
                season_markup = 1.0  # без надбавки
            return price * season_markup

        def apply_weekday_markup(price, booking_date):
            # Предположим, что цены выше на выходные (пятница, суббота, воскресенье)
            # 4 - пятница, 5 - суббота, 6 - воскресенье
            if booking_date.weekday() in [4, 5, 6]:
                weekday_markup = 1.1  # +10% к цене
            else:
                weekday_markup = 1.0  # без надбавки
            return price * weekday_markup

        def apply_agency_fee(price, agency_fee_percentage):
            return price * (1 + agency_fee_percentage / 100)

        days_to_departure = (departure_date - booking_date).days
        price_with_time_markup = apply_time_based_markup(
            base_price, days_to_departure)

        price_with_season_markup = apply_seasonal_markup(
            price_with_time_markup, booking_date)
        price_with_weekday_markup = apply_weekday_markup(
            price_with_season_markup, booking_date)

        final_price = apply_agency_fee(
            price_with_weekday_markup, agency_fee_percentage)

        return final_price

    def format_timedelta(td):
        return f"{td.seconds // 3600}ч {td.seconds % 3600 // 60}мин"

    form = AirplaneTicketsForm()

    if form.validate_on_submit():
        departure_city = form.departure_city.data
        arrival_city = form.arrival_city.data
        departure_date = form.departure_date.data
        return_date = form.return_date.data
        passengers = form.passengers.data
        flight_class = form.flight_class.data

        session['passengers'] = passengers
        session['flight_class'] = flight_class

        return redirect(url_for('search_flights', departure_city=departure_city, arrival_city=arrival_city, departure_date=departure_date, return_date=return_date, passengers=passengers, flight_class=flight_class))

    departure_city = request.args.get('departure_city')
    arrival_city = request.args.get('arrival_city')
    departure_date = request.args.get('departure_date')
    return_date = request.args.get('return_date')
    passengers = request.args.get('passengers')
    flight_class_name = request.args.get('flight_class')

    if not all([departure_city, arrival_city, departure_date, passengers, flight_class_name]):
        # Обработка ошибок если параметры отсутствуют
        return render_template('error.html', message="Missing parameters"), 400

    passengers = int(passengers)
    flight_class = FlightClass.query.filter_by(name=flight_class_name).first()

    if not flight_class:
        return render_template('error.html', message="Invalid flight class"), 400

    departure_city_id = AirCity.query.filter_by(name=departure_city).first().id
    arrival_city_id = AirCity.query.filter_by(name=arrival_city).first().id

    def calculate_flight_duration(departure_time, arrival_time):
        return arrival_time - departure_time

    def search_direct_flights(departure_city, arrival_city, departure_date, passengers, flight_class):
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
        flights = Flight.query.filter(
            Flight.origin_city_id == departure_city,
            Flight.destination_city_id == arrival_city,
            db.func.date(Flight.departure_time) == departure_date
        ).all()

        suitable_flights = []
        for flight in flights:
            available_seats = Seat.query.filter_by(
                aircraft_id=flight.aircraft_id,
                flight_class_id=flight_class
            ).count()
            if available_seats >= passengers:
                flight_duration = calculate_flight_duration(
                    flight.departure_time, flight.arrival_time)
                suitable_flights.append((flight, flight_duration))
        return suitable_flights

    def search_flights_with_transfers(departure_city, arrival_city, departure_date, passengers, flight_class):
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
        first_leg_flights = Flight.query.filter(
            Flight.origin_city_id == departure_city,
            db.func.date(Flight.departure_time) == departure_date
        ).all()

        suitable_flights_with_transfers = []

        for first_flight in first_leg_flights:
            transfer_city_id = first_flight.destination_city_id

            second_leg_flights = Flight.query.filter(
                Flight.origin_city_id == transfer_city_id,
                Flight.destination_city_id == arrival_city,
                db.or_(
                    db.and_(
                        db.func.date(
                            Flight.departure_time) == first_flight.arrival_time.date(),
                        Flight.departure_time > first_flight.arrival_time
                    ),
                    db.func.date(
                        Flight.departure_time) == first_flight.arrival_time.date() + timedelta(days=1)
                )
            ).all()

            for second_flight in second_leg_flights:
                first_leg_seats = Seat.query.filter_by(
                    aircraft_id=first_flight.aircraft_id,
                    flight_class_id=flight_class
                ).count()
                second_leg_seats = Seat.query.filter_by(
                    aircraft_id=second_flight.aircraft_id,
                    flight_class_id=flight_class
                ).count()

                if first_leg_seats >= passengers and second_leg_seats >= passengers:
                    transfer_duration = second_flight.departure_time - first_flight.arrival_time
                    first_flight_duration = calculate_flight_duration(
                        first_flight.departure_time, first_flight.arrival_time)
                    second_flight_duration = calculate_flight_duration(
                        second_flight.departure_time, second_flight.arrival_time)
                    total_travel_duration = calculate_flight_duration(first_flight.departure_time, first_flight.arrival_time) + \
                        calculate_flight_duration(second_flight.departure_time, second_flight.arrival_time) + \
                        transfer_duration
                    suitable_flights_with_transfers.append(
                        (first_flight, second_flight,
                         transfer_duration, total_travel_duration, first_flight_duration, second_flight_duration)
                    )

        return suitable_flights_with_transfers

    def search_all_flights(departure_city, arrival_city, departure_date, passengers, flight_class):
        direct_flights = search_direct_flights(
            departure_city, arrival_city, departure_date, passengers, flight_class)
        connecting_flights = search_flights_with_transfers(
            departure_city, arrival_city, departure_date, passengers, flight_class)
        return direct_flights, connecting_flights

    def search_return_flights(departure_city, arrival_city, return_date, passengers, flight_class):
        if return_date:
            return search_all_flights(arrival_city, departure_city, return_date, passengers, flight_class)
        return [], []

    direct_flights, connecting_flights = search_all_flights(
        departure_city_id, arrival_city_id, departure_date, passengers, flight_class.id)
    return_direct_flights, return_connecting_flights = search_return_flights(
        departure_city_id, arrival_city_id, return_date, passengers, flight_class.id)

    return render_template('search_flights.html', direct_flights=direct_flights, connecting_flights=connecting_flights, return_direct_flights=return_direct_flights, return_connecting_flights=return_connecting_flights, calculate_flight_duration=calculate_flight_duration, form=form, menu=menu, calculate_final_price=calculate_final_price, flight_class_name=flight_class_name, format_timedelta=format_timedelta, title='Авиабилеты')


@app.route('/book_seats', methods=['GET', 'POST'])
@login_required
def book_seats():

    user_id = current_user.id

    # Получение рейсов из запроса
    flights = eval(request.args.get('flights'))
    total_price = request.args.get('total_price')
    number_of_seats = session.get('passengers')
    flight_class = session.get('flight_class')
    flight_class_id = FlightClass.query.filter_by(name=flight_class).first().id
    name = 'name'
    phone_number = 'phone_number'
    passport_number = 'passport_number'
    passport_series = 'passport_series'

    # Проверка наличия минимально необходимых сегментов
    first_flight_id = flights.get('first_flight')
    second_flight_id = flights.get('second_flight')
    first_return_flight_id = flights.get('first_return_flight')
    second_return_flight_id = flights.get('second_return_flight')

    if not first_flight_id or not first_return_flight_id:
        return {'error': 'You must specify at least one flight for both directions.'}

    # Проверка доступности мест для каждого указанного рейса
    flight_ids = {
        'first_flight': first_flight_id,
        'second_flight': second_flight_id,
        'first_return_flight': first_return_flight_id,
        'second_return_flight': second_return_flight_id
    }

    available_seats_per_flight = {}
    for flight_key, flight_id in flight_ids.items():
        if flight_id:  # Проверяем только если flight_id не None
            available_seats = Seat.query.filter(
                Seat.aircraft_id == Flight.query.filter_by(
                    id=flight_id).first().aircraft_id,
                Seat.flight_class_id == flight_class_id,
                ~Seat.id.in_(db.session.query(AirBooking.first_seat_id).filter_by(first_flight_id=flight_id)) &
                ~Seat.id.in_(db.session.query(AirBooking.second_seat_id).filter_by(second_flight_id=flight_id)) &
                ~Seat.id.in_(db.session.query(AirBooking.first_return_seat_id).filter_by(first_return_flight_id=flight_id)) &
                ~Seat.id.in_(db.session.query(AirBooking.second_return_seat_id).filter_by(
                    second_return_flight_id=flight_id))
            ).limit(number_of_seats).all()

            if len(available_seats) < number_of_seats:
                return {'error': f'Not enough available seats for flight {flight_id}.'}

            available_seats_per_flight[flight_key] = available_seats

    # Создаем бронирования для каждого рейса и каждого места
    new_bookings = []
    for i in range(number_of_seats):
        new_booking = AirBooking(
            user_id=user_id,
            first_flight_id=first_flight_id,
            second_flight_id=second_flight_id,
            first_return_flight_id=first_return_flight_id,
            second_return_flight_id=second_return_flight_id,
            first_seat_id=available_seats_per_flight['first_flight'][
                i].id if 'first_flight' in available_seats_per_flight else None,
            second_seat_id=available_seats_per_flight['second_flight'][
                i].id if 'second_flight' in available_seats_per_flight else None,
            first_return_seat_id=available_seats_per_flight['first_return_flight'][
                i].id if 'first_return_flight' in available_seats_per_flight else None,
            second_return_seat_id=available_seats_per_flight['second_return_flight'][
                i].id if 'second_return_flight' in available_seats_per_flight else None,
            class_id=flight_class_id,
            total_price=total_price,
            name=name,
            phone_number=phone_number,
            passport_number=passport_number,
            passport_series=passport_series
        )
        new_bookings.append(new_booking)
        db.session.add(new_booking)

    db.session.commit()

    return render_template('book_seats.html', title='Авиабилеты', menu=menu)


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
