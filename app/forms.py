from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    username = StringField("Username: ", validators=[Length(
        min=4, max=20, message="Имя должно быть от 4 до 20 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    password = PasswordField('Пароль:', validators=[DataRequired(), Length(
        min=4, max=50, message="Пароль должен быть от 4 до 50 символов")])
    password2 = PasswordField(
        'Повтор пароля:', validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')])
    submit = SubmitField("Регистрация")


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    password = PasswordField("Пароль: ", validators=[DataRequired(),
                                                     Length(min=4, max=50, message="Пароль должен быть от 4 до 50 символов")])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField("Войти")


class ChangePassword(FlaskForm):
    old_password = PasswordField("Старый пароль: ", validators=[DataRequired(),
                                                                Length(min=4, max=50, message="Пароль должен быть от 4 до 50 символов")])
    new_password = PasswordField("Новый пароль: ", validators=[DataRequired(),
                                                               Length(min=4, max=50, message="Пароль должен быть от 4 до 50 символов")])
    new_password2 = PasswordField(
        'Повтор пароля:', validators=[DataRequired(), EqualTo('new_password', message='Пароли не совпадают')])
    submit = SubmitField("Поменять")


class ResidenceForm(FlaskForm):
    destination = StringField('Куда', validators=[DataRequired()])
    start_date = DateField(
        'Начальная дата', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Конечная дата', format='%Y-%m-%d',
                         validators=[DataRequired()])
    submit = SubmitField("Поиск")


class BookingHotelForm(FlaskForm):
    name = StringField('Фио', validators=[DataRequired()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    passport_number = StringField(
        'Номер паспорта', validators=[DataRequired()])
    passport_series = StringField(
        'Серия паспорта', validators=[DataRequired()])
    submit = SubmitField('Забронировать')


class AirplaneTicketsForm(FlaskForm):
    departure = StringField('Место вылета', validators=[DataRequired()])
    destination = StringField('Место назначения', validators=[DataRequired()])
    date = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
    flight_class = SelectField('Класс', choices=[('Economy', 'Economy'), (
        'Business', 'Business'), ('First', 'First')], default='Economy', validators=[DataRequired()])
    submit = SubmitField('Submit')
