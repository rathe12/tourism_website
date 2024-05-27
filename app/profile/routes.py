from flask import render_template, redirect, url_for, flash, request
from app.routes import menu
from . import profile_bp
from flask_login import logout_user, login_required, current_user
from app.forms import ChangePassword, UserForm
from app.models import User, Booking, Hotel, Room
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
    print(orders)
    orders_list = []
    if not orders:
        orders = 'У вас нет заказов'
    else:
        for order in orders:
            hotel = Hotel.query.filter_by(id=order.hotel_id).first()
            room = Room.query.filter_by(id=order.room_id).first()
            orders_list.append([order, hotel, room])
    return render_template('myorders.html', orders_list=orders_list, menu=menu, title='Заказы')


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
