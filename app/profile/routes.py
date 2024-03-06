from flask import render_template, redirect, url_for
from app.routes import menu
from . import profile_bp
from flask_login import logout_user, login_required, current_user


@profile_bp.route('/myaccount')
def myaccount():
    if current_user.is_authenticated:
        return render_template('profile.html', menu=menu, title='Профиль')
    else:
        return redirect(url_for('login'))


@profile_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
