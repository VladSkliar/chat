from functools import wraps
from flask import Flask, render_template, session, request, redirect, url_for
from flask import jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import User, Room
from translate import translate
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
    session.pop('room', None)
    return redirect(url_for('login'))


@app.route('/find_room', methods=['POST'])
def find_room():
    roomname = request.form['roomname']
    roomname = '%' + roomname + '%'
    rooms = Room.select().where(Room.name**roomname)
    return jsonify([room.to_dict() for room in rooms])


@app.route('/create_room', methods=['POST'])
def create_room():
    roomname = request.form['roomname']
    if roomname:
        rooms = Room.select().where(Room.name == roomname)
        if not rooms:
            Room.create(name=roomname.replace('<script>', '').replace('</script>','').replace('script', ''))
            return jsonify({'message': 'Your room is created'})
        else:
            return jsonify({'message': 'Room with that name is currently created'})
    else:
        return jsonify({'message': 'Room must have name. Please enter add roomname to post data'})


@socketio.on('change_room', namespace='/test')
def change_room(data):
    time = datetime.datetime.now()
    room = session.get('room', 'general')
    emit('response',
         {
          'data': session.get('username') + ' has left the room.',
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
          'roomname': room
          },
         room=room
         )
    leave_room(room)
    room = session['room'] = data['roomname']
    join_room(room)
    emit('response',
         {
          'data': 'Connected',
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
          'roomname': room
          },
         room=room
         )


@socketio.on('connect', namespace='/test')
def test_connect():
    time = datetime.datetime.now()
    room = session.get('room', 'general')
    join_room(room)
    emit('response',
         {
          'data': 'Connected',
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
          'roomname': room
          },
         room=room
         )


@socketio.on('leave', namespace='/test')
def leave():
    time = datetime.datetime.now()
    room = session.get('room', 'general')
    if room != 'general':
        leave_room(room)
        emit('response',
             {
              'data': session.get('username') + ' has left the room.',
              'username': session.get('username'),
              'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
              'roomname': room
              },
             room=room
             )
        session.pop('room', None)
    room = 'general'
    join_room(room)
    emit('response',
         {
          'data': 'Connected',
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
          'roomname': room
          },
         room=room
         )


@socketio.on('message', namespace='/test')
def test_message(message):
    time = datetime.datetime.now()
    room = session.get('room', 'general')
    msg = message['data']
    msg_list = message['data'].split(' ')
    cmd = msg_list[0]
    if cmd == '/translate':
        language = msg_list[1]
        text = ' '.join(msg_list[2:])
        msg = translate(text, language)+ ' '+ language+' ' + text
    emit('response',
         {
          'data': msg,
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
          'roomname': room
          },
         room=room
         )


if __name__ == '__main__':
    #socketio.init_app(app)
    socketio.run(app)
    # app.run()
