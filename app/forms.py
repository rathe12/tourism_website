from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    username = StringField("Имя: ", validators=[Length(
        min=4, max=20, message="Имя должно быть от 4 до 20 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    password2 = PasswordField(
        'Повтор пароля:', validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')])
    submit = SubmitField("Регистрация")


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    password = PasswordField("Пароль: ", validators=[DataRequired(),
                                                     Length(min=4, max=50, message="Пароль должен быть от 4 до 50 символов")])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField("Войти")
