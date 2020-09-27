from flask import Flask
from flask import render_template
from flask import request
from functools import reduce
import json
from random import randint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody'


class Tutor(db.Model):
    __tablename__ = "tutors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    about = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(256))
    price = db.Column(db.Integer, nullable=False)
    goals = db.Column(db.String(200), nullable=False)  # в виде строки будет json, который преобразуется в список
    free = db.Column(db.String(), nullable=False)  # в виде строки будет json, который преобразуется в словарь
    bookings = db.relationship("Booking")  # у репетитора может быть несколько бронирований

    def get_dict(self):
        return {
            'name': self.name,
            'about': self.about,
            'rating': self.rating,
            'picture': self.picture,
            'price': self.price,
            'goals': self.goals,
            'free': self.free,
            'bookings': self.bookings,
        }


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("tutors.id"))  # связь с репетитором
    teacher = db.relationship("Tutor")
    day_of_week = db.Column(db.String(3), nullable=False)  # mon,...
    time = db.Column(db.String(2), nullable=False)  # 16
    name = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(12), nullable=False)


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(4), nullable=False)  # 7-10
    name = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(12), nullable=False)


@app.route('/')
def render_main():
    data_base = get_data_from_db()
    tutors = db.session.query(Tutor).all()  # Использование БД
    print(type(tutors))
    goals = data_base['goals']

    all_numbers = [i for i in range(len(tutors))]
    random_numbers = []
    for i in range(6):
        random_numbers.append(all_numbers.pop(randint(0, len(all_numbers) - 1)))

    random_profiles = []
    for random_number in random_numbers:
        random_profiles.append(tutors[random_number])

    return render_template('index.html', profiles=random_profiles, goals=goals)


@app.route('/all_tutors')
def render_all_tutors():
    tutors = db.session.query(Tutor).all()  # Использование БД

    data_base = get_data_from_db()
    goals = data_base['goals']
    return render_template('all_tutors.html', profiles=tutors, goals=goals)


@app.route('/profiles/<int:teacher_id>')
def render_profile(teacher_id):
    data_base = get_data_from_db()
    teachers = data_base['teachers']
    goals = data_base['goals']

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
    data_base = get_data_from_db()
    teacher = data_base['teachers'][teacher_id]
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

    data_base = get_data_from_db()
    data_base['bookings'].append(booking)
    save_data_to_db(data_base)

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

    data_base = get_data_from_db()
    data_base['requests'].append(client_request)
    save_data_to_db(data_base)

    return render_template('request_done.html', request_goal=request_goal,
                           request_time=request_time,
                           request_name=request_name,
                           request_phone=request_phone)


@app.route('/goals/<string:goal>')
def render_goal(goal):
    data_base = get_data_from_db()
    teachers = data_base['teachers']
    filtered_teachers = list(filter(lambda x: goal in x['goals'], teachers))
    goals = data_base['goals']
    return render_template('goal.html', goal=goals[goal], teachers=filtered_teachers)


if __name__ == '__main__':
    app.run(debug=True)
