from . import app, db
from flask import render_template, flash, redirect, url_for, request, session
from app.forms import RegistrationForm, LoginForm, ResidenceForm
from app.models import User, Hotel, City, Room, RoomAvailability
from flask_login import login_user, current_user
from datetime import datetime

menu = [{"name": "Акции", "url": "/"},
        {"name": "Туры", "url": "/tours"},
        {"name": "Проживание", "url": "/accommodation"},
        {"name": "Авиабилеты", "url": "/air_tickets"},
        {"name": "Профиль", "url": "/profile/myaccount"}]


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


@app.route('/hotels')
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

    # Здесь вы можете выполнить необходимые операции с этими данными, например, передать их в шаблон
    # Или выполнить запрос к базе данных для получения данных о гостиницах
    city = City.query.filter_by(name=destination).first()
    if city:
        hotels = Hotel.query.filter_by(city_id=city.id).all()
    return render_template('hotels.html', form=form, hotels=hotels, destination=destination, start_date=start_date, end_date=end_date, menu=menu)


@app.route('/hotel/<int:hotel_id>')
def show_hotel(hotel_id):
    hotel = Hotel.query.get(hotel_id)
    start_date = datetime.strptime(session.get(
        'start_hotel_date'), '%Y-%m-%d').date()
    print(start_date)
    end_date = datetime.strptime(session.get(
        'end_hotel_date'), '%Y-%m-%d').date()
    print(end_date)
    availability_room_type = []
    for room in hotel.rooms:
        # print(room)
        availability = RoomAvailability.query.filter_by(room_id=room.id).all()
        # print(availability)
        for room_info in availability:
            # print(room_info)
            if room_info.check_in_date == None and room_info.check_out_date == None:
                if room_info.room not in availability_room_type:
                    availability_room_type.append(room_info.room)
            else:
                if start_date > room_info.check_out_date or end_date < room_info.check_in_date:
                    print(room_info)
                    if room_info.room not in availability_room_type:
                        availability_room_type.append(room_info.room)

    print(availability_room_type)
    return render_template('hotel.html', hotel=hotel, menu=menu, rooms=availability_room_type)


@app.route('/air_tickets')
def air_tickets():
    return render_template('air_tickets.html', menu=menu, title='Авиабилеты')


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
        return redirect(url_for('profile.myaccount'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неврный логин или пароль', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        return redirect(url_for('profile.myaccount', username=current_user.username))
    return render_template('login.html', title='Войти', form=form, menu=menu)
