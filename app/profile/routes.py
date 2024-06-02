from flask import render_template, redirect, url_for, flash, request
from app.routes import menu
from . import profile_bp
from flask_login import logout_user, login_required, current_user
from app.forms import ChangePassword, UserForm
from app.models import AirBooking, Flight, Seat, User, Booking, Hotel, Room
from werkzeug.security import generate_password_hash
from app import db
from datetime import datetime


@profile_bp.route('/<username>', methods=['GET', 'POST'])
@login_required
def myaccount(username):
    user = User.query.get_or_404(current_user.id)

    # Установка значений по умолчанию для формы
    form = UserForm(
        gender=user.gender,
        first_name=user.first_name,
        last_name=user.last_name,
        birth_date=user.birth_date.strftime(
            '%Y-%m-%d') if user.birth_date else '',
        email=user.email,
        phone_code=user.phone_code,
        phone_number=user.phone_number
    )

    if request.method == 'POST':
        print("Request form data:", request.form)  # Логирование данных запроса
        if form.validate_on_submit():
            user.gender = form.gender.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data

            # Конвертация даты в формат базы данных
            user.birth_date = form.birth_date.data

            user.email = form.email.data
            user.phone_code = form.phone_code.data
            user.phone_number = form.phone_number.data

            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('profile.myaccount', username=current_user.username))

        # Вывод ошибок валидации
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(
                        f"Ошибка в поле {getattr(form, field).label.text}: {error}", 'danger')

    return render_template('myaccount.html', username=username, form=form, user=user, menu=menu, title='Профиль')


@profile_bp.route('/myorders')
@login_required
def myorders():
    orders = Booking.query.filter_by(user_id=current_user.id).all()
    air_orders = AirBooking.query.filter_by(user_id=current_user.id).all()

    combined_orders = []

    for order in orders:
        hotel = Hotel.query.filter_by(id=order.hotel_id).first()
        room = Room.query.filter_by(id=order.room_id).first()
        check_in_date = order.check_in_date if isinstance(
            order.check_in_date, datetime) else datetime.combine(order.check_in_date, datetime.min.time())
        combined_orders.append({
            'type': 'hotel',
            'order': order,
            'hotel': hotel,
            'room': room,
            'date': check_in_date
        })

    for air_order in air_orders:
        first_flight = Flight.query.filter_by(
            id=air_order.first_flight_id).first()
        second_flight = Flight.query.filter_by(
            id=air_order.second_flight_id).first()
        first_return_flight = Flight.query.filter_by(
            id=air_order.first_return_flight_id).first()
        second_return_flight = Flight.query.filter_by(
            id=air_order.second_return_flight_id).first()
        first_seat = Seat.query.filter_by(id=air_order.first_seat_id).first()
        second_seat = Seat.query.filter_by(id=air_order.second_seat_id).first()
        first_return_seat = Seat.query.filter_by(
            id=air_order.first_return_seat_id).first()
        second_return_seat = Seat.query.filter_by(
            id=air_order.second_return_seat_id).first()

        departure_time = first_flight.departure_time if isinstance(
            first_flight.departure_time, datetime) else datetime.combine(first_flight.departure_time, datetime.min.time())
        combined_orders.append({
            'type': 'air',
            'order': air_order,
            'first_flight': first_flight,
            'second_flight': second_flight,
            'first_return_flight': first_return_flight,
            'second_return_flight': second_return_flight,
            'first_seat': first_seat,
            'second_seat': second_seat,
            'first_return_seat': first_return_seat,
            'second_return_seat': second_return_seat,
            'date': departure_time
        })

    combined_orders.sort(key=lambda x: x['date'], reverse=True)

    return render_template('myorders.html', combined_orders=combined_orders, menu=menu, title='Заказы')


@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = ChangePassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if user.check_password(form.old_password.data):
            user.set_password(form.new_password2.data)
            db.session.commit()
            flash('Вы успешно сменили пароль', 'success')
        else:
            flash('Неверный пароль', 'error')
    return render_template('settings.html', form=form, menu=menu, title='Настройки')


@profile_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
