from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import json

map_to_day_of_week = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг',
                      'fri': 'Пятница', 'sat': 'Суббота', 'sun': 'Воскресение'}


def get_data_from_db():
    with open('db.json', 'r') as f:
        return json.load(f)


app = Flask(__name__)


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

    return render_template('profile.html', profile=profile, profile_goals=profile_goals,
                           map_to_day_of_week=map_to_day_of_week)


@app.route('/request')
def render_request():
    return render_template('request.html')


@app.route('/request_done')
def render_request_done():
    return render_template('request_done.html')


@app.route('/booking/<int:teacher_id>/<string:day_of_week>/<int:time>')
def render_booking(teacher_id, day_of_week, time):
    db = get_data_from_db()
    teacher = db['teachers'][teacher_id]

    return render_template('booking.html', teacher=teacher, day_of_week=day_of_week,
                           map_to_day_of_week=map_to_day_of_week, time=time)


@app.route('/booking_done/', methods=['POST'])
def render_booking_done():
    client_weekday = map_to_day_of_week[request.form.get('client_weekday')]
    client_time = request.form.get('client_time')
    client_name = request.form.get('client_name')
    client_phone = request.form.get('client_phone')
    return render_template('booking_done.html', client_weekday=client_weekday, client_time=client_time,
                           client_name=client_name, client_phone=client_phone)


if __name__ == '__main__':
    app.run(debug=True)
