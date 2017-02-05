from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO
from models import User
from functools import wraps
from flask_socketio import emit, join_room
import datetime

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
socketio = SocketIO(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username', '')
        if not username:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form['username']
    password = request.form['password']
    response_context = {}
    try:
        User.get(User.username == username)
        response_context['message'] = 'This username is register. Try another username'
        return render_template('login.html', context=response_context)
    except User.DoesNotExist:
        User.create(username=username, password=password)
        response_context['message'] = 'User is register. Try log in to website'
        return render_template('login.html', context=response_context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    response_context = {}
    try:
        user = User.get(User.username == username)
        if str(user.password) == str(password):
            session['username'] = username
            return redirect(url_for('index'))
        response_context['message'] = 'Your user credentials is wrong'
        return render_template('login.html', context=response_context)
    except User.DoesNotExist:
        response_context['message'] = 'Your user credentials is wrong'
        return render_template('login.html', context=response_context)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_response', {'data': 'PING-Pong'}, room='general')


@socketio.on('connect', namespace='/test')
def test_connect():
    time = datetime.datetime.now()
    join_room('general')
    emit('response',
         {
          'data': 'Connected',
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute)
          },
         room='general'
         )


@socketio.on('message', namespace='/test')
def test_message(message):
    time = datetime.datetime.now()
    emit('response',
         {
          'data': message['data'],
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute)
          },
         room='general'
         )


if __name__ == '__main__':
    #socketio.init_app(app)
    socketio.run(app)
    # app.run()
