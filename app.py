from flask import Flask
from flask import render_template
from flask import request
from functools import reduce
import json

from forms import BookingForm
from forms import RequestForm

map_to_day_of_week = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг',
                      'fri': 'Пятница', 'sat': 'Суббота', 'sun': 'Воскресение'}


def get_data_from_db():
    with open('db.json', 'r') as f:
        return json.load(f)


def save_data_to_db(new_db):
    with open('db.json', 'w') as f:
        return json.dump(new_db, f, indent=4)


app = Flask(__name__)
app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody'


@app.route('/')
def render_main():
    profiles = get_data_from_db()['teachers']
    return render_template('index.html', profiles=profiles)


@app.route('/goals/<goal>')
def render_goals():
    return render_template('goal.html')


@app.route('/profiles/<int:teacher_id>')
def render_profiles(teacher_id):
    db = get_data_from_db()
    teachers = db['teachers']
    goals = db['goals']

    profile = [teacher for teacher in teachers if teacher['id'] == teacher_id][0]
    profile_goals = [value for key, value in goals.items() if key in profile['goals']]

    day_dict = [(day, day_obj) if
                reduce(lambda x, y: x or y, day_obj.values(), False) else (day, None) for
                day, day_obj in profile['free'].items()]

    for (day, value) in day_dict:
        profile['free'][day] = value

    return render_template('profile.html', profile=profile, profile_goals=profile_goals,
                           map_to_day_of_week=map_to_day_of_week)


@app.route('/booking/<int:teacher_id>/<string:day_of_week>/<int:time>')
def render_booking(teacher_id, day_of_week, time):
    db = get_data_from_db()
    teacher = db['teachers'][teacher_id]
    form = BookingForm(client_weekday=day_of_week, client_time=time, client_teacher_id=teacher['id'])

    return render_template('booking.html', teacher=teacher, map_to_day_of_week=map_to_day_of_week,
                           day_of_week=day_of_week, time=time, form=form)


@app.route('/booking_done/', methods=['POST'])
def render_booking_done():
    client_weekday = request.form.get('client_weekday')
    client_time = request.form.get('client_time')
    client_name = request.form.get('client_name')
    client_phone = request.form.get('client_phone')
    client_teacher_id = request.form.get('client_teacher_id')
    booking = {
        'type': 'trial_lesson',
        'teacher_id': client_teacher_id,
        'day_of_week': client_weekday,
        'time': client_time,
        'name': client_name,
        'phone': client_phone
    }

    db = get_data_from_db()
    db['bookings'].append(booking)
    save_data_to_db(db)

    return render_template('booking_done.html', client_weekday=client_weekday, client_time=client_time,
                           client_name=client_name, client_phone=client_phone)


@app.route('/request')
def render_request():
    form = RequestForm()
    return render_template('request.html', form=form)


@app.route('/request_done', methods=['POST'])
def render_request_done():
    request_goal = request.form.get('request_goal')
    request_time = request.form.get('request_time')
    request_name = request.form.get('request_name')
    request_phone = request.form.get('request_phone')

    client_request = {
        'goal': request_goal,
        'time': request_time,
        'name': request_name,
        'phone': request_phone
    }

    db = get_data_from_db()
    db['requests'].append(client_request)
    save_data_to_db(db)

    return render_template('request_done.html', request_goal=request_goal,
                           request_time=request_time,
                           request_name=request_name,
                           request_phone=request_phone)


if __name__ == '__main__':
    app.run(debug=True)
