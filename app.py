from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def render_main():
    return render_template('index.html')


@app.route('/goals/<goal>')
def render_goals():
    return render_template('goal.html')


@app.route('/profiles/<id>')
def render_profiles():
    return render_template('profile.html')


@app.route('/request')
def render_request():
    return render_template('request.html')


@app.route('/request_done')
def render_request_done():
    return render_template('request_done.html')


@app.route('/booking/<id>')
def render_booking():
    return render_template('booking.html')


@app.route('/booking_done')
def render_booking_done():
    return render_template('booking_done.html')


if __name__ == '__main__':
    app.run(debug=True)
