from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField, RadioField


class BookingForm(FlaskForm):
    client_weekday = HiddenField()
    client_time = HiddenField()
    client_teacher_id = HiddenField()

    client_name = StringField('Вас зовут')
    client_phone = StringField('Ваш телефон')
    submit = SubmitField('Записаться на пробный урок')


class RequestForm(FlaskForm):
    request_goal = RadioField('Какая цель занятий?',
                      choices=[('travel', 'Для путешествий'), ('learn', 'Для школы'), ('work', 'Для работы'),
                               ('move', 'Для переезда'), ('programming', 'Для программирования')])
    request_time = RadioField('Сколько времени есть?',
                      choices=[('1-2', '1-2 часа в неделю'), ('3-5', '3-5 часов  неделю'),
                               ('5-7', '5-7 часов в неделю'), ('7-10', '7-10 часов в неделю')])
    request_name = StringField('Вас зовут')
    request_phone = StringField('Ваш телефон')

    submit = SubmitField('Найдите мне преподавателя')
