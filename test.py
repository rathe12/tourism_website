Вот моя форма и маршрут для бронирования билетов а снизу еще и html код. У меня проблема в том что почему то когда я захлжу на страницу не отображается ни лейбл ни поле для ввода name. И так же мой print выводит {'passengers': [{'name': ['This field is required.']}]}

Формы:


class PassengerForm(FlaskForm):
    name = StringField('Фио', validators=[DataRequired()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    passport_number = StringField(
        'Ноемер пасапорта', validators=[DataRequired()])
    passport_series = StringField(
        'Серия паспорта', validators=[DataRequired()])


class AirBookingForm(FlaskForm):
    passengers = FieldList(FormField(PassengerForm), min_entries=1)
    submit = SubmitField('Забронировать')


Маршрут:


@app.route('/book_seats', methods=['GET', 'POST'])
@login_required
def book_seats():
    try:
        flights = eval(request.args.get('flights'))
        total_price = request.args.get('total_price')
        number_of_seats = session.get('passengers')
        flight_class = session.get('flight_class')
        session['flights'] = flights
        session['total_price'] = total_price
        session['number_of_seats'] = number_of_seats
        session['flight_class'] = flight_class
    except:
        flights = session.get('flights')
        total_price = session.get('total_price')
        number_of_seats = session.get('number_of_seats')
        flight_class = session.get('flight_class')
    flight_class_id = FlightClass.query.filter_by(name=flight_class).first().id

    form = AirBookingForm()
    while len(form.passengers.entries) < number_of_seats:
        form.passengers.append_entry()

    if request.method == 'POST':
        if form.validate():
            print("Форма прошла валидацию!")
            print(form.data)  # Debug: print form data
        else:
            print("Форма не прошла валидацию!")
            print(form.errors)  # Debug: print form errors

    if form.validate_on_submit():
        user_id = current_user.id

        first_flight_id = flights.get('first_flight')
        second_flight_id = flights.get('second_flight')
        first_return_flight_id = flights.get('first_return_flight')
        second_return_flight_id = flights.get('second_return_flight')

        if not first_flight_id or not first_return_flight_id:
            return {'error': 'You must specify at least one flight for both directions.'}

        flight_ids = {
            'first_flight': first_flight_id,
            'second_flight': second_flight_id,
            'first_return_flight': first_return_flight_id,
            'second_return_flight': second_return_flight_id
        }

        available_seats_per_flight = {}
        for flight_key, flight_id in flight_ids.items():
            if flight_id:
                available_seats = Seat.query.filter(
                    Seat.aircraft_id == Flight.query.filter_by(
                        id=flight_id).first().aircraft_id,
                    Seat.flight_class_id == flight_class_id,
                    ~Seat.id.in_(db.session.query(AirBooking.first_seat_id).filter_by(first_flight_id=flight_id)) &
                    ~Seat.id.in_(db.session.query(AirBooking.second_seat_id).filter_by(second_flight_id=flight_id)) &
                    ~Seat.id.in_(db.session.query(AirBooking.first_return_seat_id).filter_by(first_return_flight_id=flight_id)) &
                    ~Seat.id.in_(db.session.query(AirBooking.second_return_seat_id).filter_by(
                        second_return_flight_id=flight_id))
                ).limit(number_of_seats).all()

                if len(available_seats) < number_of_seats:
                    return {'error': f'Not enough available seats for flight {flight_id}.'}

                available_seats_per_flight[flight_key] = available_seats

        new_bookings = []
        for i in range(number_of_seats):
            passenger_data = form.passengers[i].data
            new_booking = AirBooking(
                user_id=user_id,
                first_flight_id=first_flight_id,
                second_flight_id=second_flight_id,
                first_return_flight_id=first_return_flight_id,
                second_return_flight_id=second_return_flight_id,
                first_seat_id=available_seats_per_flight['first_flight'][
                    i].id if 'first_flight' in available_seats_per_flight else None,
                second_seat_id=available_seats_per_flight['second_flight'][
                    i].id if 'second_flight' in available_seats_per_flight else None,
                first_return_seat_id=available_seats_per_flight['first_return_flight'][
                    i].id if 'first_return_flight' in available_seats_per_flight else None,
                second_return_seat_id=available_seats_per_flight['second_return_flight'][
                    i].id if 'second_return_flight' in available_seats_per_flight else None,
                class_id=flight_class_id,
                total_price=total_price,
                name=passenger_data['name'],
                phone_number=passenger_data['phone_number'],
                passport_number=passenger_data['passport_number'],
                passport_series=passenger_data['passport_series']
            )
            new_bookings.append(new_booking)
            db.session.add(new_booking)

        db.session.commit()

        return redirect(url_for('profile.myorders'))

    return render_template('book_seats.html', form=form, title='Авиабилеты', menu=menu)


Штмл код:

{ % extends 'base.html' % }
{ % block content % }

<form method = "post" action = "{{ url_for('book_seats') }}" >
    {{form.hidden_tag()}}

    { % for passenger_form in form.passengers % }
       <fieldset >
            {{passenger_form.hidden_tag()}}
            <legend > Пассажир {{loop.index}} < /legend >
            <div >
                {{passenger_form.name.label}} < br >
                {{passenger_form.name}} < br >
                { % if passenger_form.name.errors % }
                    <ul class = "errors" >
                        { % for error in passenger_form.name.errors % }
                            <li > {{error}} < /li >
                        { % endfor % }
                    </ul >
                { % endif % }
            </div >
            <div >
                {{passenger_form.phone_number.label}} < br >
                {{passenger_form.phone_number}} < br >
                { % if passenger_form.phone_number.errors % }
                    <ul class = "errors" >
                        { % for error in passenger_form.phone_number.errors % }
                            <li > {{error}} < /li >
                        { % endfor % }
                    </ul >
                { % endif % }
            </div >
            <div >
                {{passenger_form.passport_number.label}} < br >
                {{passenger_form.passport_number}} < br >
                { % if passenger_form.passport_number.errors % }
                    <ul class = "errors" >
                        { % for error in passenger_form.passport_number.errors % }
                            <li > {{error}} < /li >
                        { % endfor % }
                    </ul >
                { % endif % }
            </div >
            <div >
                {{passenger_form.passport_series.label}} < br >
                {{passenger_form.passport_series}} < br >
                { % if passenger_form.passport_series.errors % }
                    <ul class = "errors" >
                        { % for error in passenger_form.passport_series.errors % }
                            <li > {{error}} < /li >
                        { % endfor % }
                    </ul >
                { % endif % }
            </div >
        </fieldset >
    { % endfor % }

    <div >
        {{form.submit()}}
    </div >
</form >



{ % endblock % }