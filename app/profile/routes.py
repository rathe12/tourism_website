from flask import render_template, redirect, url_for, flash
from app.routes import menu
from . import profile_bp
from flask_login import logout_user, login_required, current_user
from app.forms import ChangePassword, UserForm
from app.models import User, Booking, Hotel, Room
from werkzeug.security import generate_password_hash
from app import db


@profile_bp.route('/<username>', methods=['GET', 'POST'])
@login_required
def myaccount(username):
    form = UserForm()
    form.gender.data = current_user.gender
    if form.validate_on_submit():
        # Получаем пользователя по id или возвращаем 404, если не найден
        user = User.query.get_or_404(current_user.id)
        print(user)
        # Обновляем поля пользователя с использованием данных из формы
        user.gender = form.gender.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.birth_date = form.birth_date .data
        user.phone_code = form.phone_code.data
        user.phone_number = form.phone_number.data

        # Сохраняем изменения в базе данных
        db.session.commit()

        flash('Данные успешно сохранены!')
        return render_template('myaccount.html', form=form, menu=menu, title='Профиль')
        # Обработка сохранения данных здесь
    return render_template('myaccount.html', form=form, menu=menu, title='Профиль')


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
