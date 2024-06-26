from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, PasswordField, SubmitField, BooleanField, DateField, RadioField, SelectField, TelField, IntegerField
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
    departure_city = StringField('Откуда', validators=[DataRequired()])
    arrival_city = StringField('Куда', validators=[DataRequired()])
    departure_date = DateField(
        'Дата вылета', format='%Y-%m-%d', validators=[DataRequired()])
    return_date = DateField(
        'Дата возвращения', format='%Y-%m-%d', validators=[DataRequired()])
    passengers = IntegerField('Количество пассажиров',
                              validators=[DataRequired()])
    flight_class = SelectField('Класс обслуживания', choices=[
                               ('economy', 'Эконом'), ('business', 'Бизнес')])
    submit = SubmitField('Поиск')


class UserForm(FlaskForm):
    gender = RadioField('Пол', choices=[('мужской', 'мужской'), (
        'женский', 'женский')], default='мужской', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', format='%Y-%m-%d',
                           validators=[DataRequired()])  # Используем формат YYYY-MM-DD
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    phone_code = StringField('Код', default='+7', validators=[DataRequired()])
    phone_number = TelField('Телефон', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class PassengerForm(FlaskForm):
    namee = StringField('Фио', validators=[DataRequired()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    passport_series = StringField(
        'Серия паспорта', validators=[DataRequired()])
    passport_number = StringField(
        'Ноемер пасапорта', validators=[DataRequired()])


class AirBookingForm(FlaskForm):
    passengers = FieldList(FormField(PassengerForm), min_entries=1)
    submit = SubmitField('Забронировать')
