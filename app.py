import json
from functools import reduce

from flask import Flask
from flask import render_template
from flask import request

from forms import BookingForm
from forms import RequestForm

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

map_to_day_of_week = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг',
                      'fri': 'Пятница', 'sat': 'Суббота', 'sun': 'Воскресение'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody'

tutors_goals_association = db.Table(
    'users_chats',
    db.Column('tutor_id', db.Integer, db.ForeignKey('tutors.id', primary_key=True)),
    db.Column('goal_id', db.Integer, db.ForeignKey('goals.id', primary_key=True))
)


class Tutor(db.Model):
    __tablename__ = 'tutors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    about = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(256))
    price = db.Column(db.Integer, nullable=False)
    free = db.Column(db.String(), nullable=False)  # в виде строки будет json, который преобразуется в словарь
    bookings = db.relationship("Booking")  # у репетитора может быть несколько бронирований
    goals = db.relationship('Goal', secondary=tutors_goals_association, back_populates='tutors')

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


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    display_name = db.Column(db.String(30), nullable=False)
    tutors = db.relationship('Tutor', secondary=tutors_goals_association, back_populates='goals')


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    booking_type = db.Column(db.String(20), nullable=False)
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
    goals = db.session.query(Goal).all()
    random_profiles = Tutor.query.order_by(db.func.random()).limit(6)

    return render_template('index.html', profiles=random_profiles, goals=goals)


@app.route('/all_tutors')
def render_all_tutors():
    tutors = db.session.query(Tutor).all()
    goals = db.session.query(Goal).all()
    return render_template('all_tutors.html', profiles=tutors, goals=goals)


@app.route('/profiles/<int:teacher_id>')
def render_profile(teacher_id):
    profile = db.session.query(Tutor).get(teacher_id)
    if profile is None:
        return f'Преподавателья с id = {teacher_id} не существует', 404

    profile_goals = profile.goals

    list_of_tuples_day_and_dict_value = [(day, day_obj) if
                                         reduce(lambda x, y: x or y, day_obj.values(), False) else (day, None) for
                                         day, day_obj in json.loads(profile.free).items()]

    profile_free = {}
    for day, value in list_of_tuples_day_and_dict_value:
        profile_free[day] = value

    return render_template('profile.html', profile=profile, profile_free=profile_free, profile_goals=profile_goals,
                           map_to_day_of_week=map_to_day_of_week)


@app.route('/booking/<int:teacher_id>/<string:day_of_week>/<int:time>', methods=['GET', 'POST'])
def render_booking(teacher_id, day_of_week, time):
    if request.method == 'POST':
        client_weekday = request.form.get('client_weekday')
        client_time = request.form.get('client_time')
        client_name = request.form.get('client_name')
        client_phone = request.form.get('client_phone')
        client_teacher_id = request.form.get('client_teacher_id')

        booking_entity = Booking(
            booking_type='trial_lesson',
            teacher=db.session.query(Tutor).get(client_teacher_id),
            day_of_week=client_weekday,
            time=client_time,
            name=client_name,
            phone=client_phone)

        db.session.add(booking_entity)
        db.session.commit()

        return render_template('booking_done.html', client_weekday=client_weekday, client_time=client_time,
                               client_name=client_name, client_phone=client_phone)

    if request.method == 'GET':
        tutor = db.session.query(Tutor).get(teacher_id)
        form = BookingForm(client_weekday=day_of_week, client_time=time, client_teacher_id=tutor.id)

        return render_template('booking.html', teacher=tutor, map_to_day_of_week=map_to_day_of_week,
                               day_of_week=day_of_week, time=time, form=form)


@app.route('/request', methods=['GET', 'POST'])
def render_request():
    if request.method == 'GET':
        form = RequestForm()
        return render_template('request.html', form=form)
    elif request.method == 'POST':
        request_goal = request.form.get('request_goal')
        request_time = request.form.get('request_time')
        request_name = request.form.get('request_name')
        request_phone = request.form.get('request_phone')

        request_entity = Request(
            goal=request_goal,
            time=request_time,
            name=request_name,
            phone=request_phone)

        db.session.add(request_entity)
        db.session.commit()

        return render_template('request_done.html',
                               request_goal=request_goal,
                               request_time=request_time,
                               request_name=request_name,
                               request_phone=request_phone)


@app.route('/goals/<string:goal>')
def render_goal(goal):
    goal_entity = db.session.query(Goal).filter(Goal.name == goal).first()
    goal_display_name = goal_entity.display_name
    tutors = goal_entity.tutors
    return render_template('goal.html', goal_display_name=goal_display_name, teachers=tutors)


if __name__ == '__main__':
    app.run(debug=True)
