from flask import render_template, redirect, url_for, flash
from app.routes import menu
from . import profile_bp
from flask_login import logout_user, login_required, current_user
from app.forms import ChangePassword
from app.models import User
from werkzeug.security import generate_password_hash
from app import db


@profile_bp.route('/myaccount')
@login_required
def myaccount():
    return render_template('myaccount.html', menu=menu, title='Профиль')


@profile_bp.route('/myorders')
@login_required
def myorders():
    print()
    return render_template('myorders.html', menu=menu, title='Заказы')


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
