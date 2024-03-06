from . import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import RegistrationForm, LoginForm
from app.models import User
from flask_login import login_user, current_user

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


@app.route('/accommodation')
def accommodation():
    return render_template('accommodation.html', menu=menu, title='Проживание')


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
        flash('Congratulations, you are now a registered user!')
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
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        return redirect(url_for('profile.myaccount'))
    return render_template('login.html', title='Войти', form=form, menu=menu)
