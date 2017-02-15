from functools import wraps
from flask import Flask, render_template, session, request, redirect, url_for
from flask import jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
# from celery import Celery
# from celery.task import periodic_task
from models import User, Room, Message
from utils import translate, get_page_info, generate_roomname, get_news_links
import datetime
from datetime import timedelta
import re
import random

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
socketio = SocketIO(app)

CELERY_BROKER_URL ='redis://localhost:6379/0'
CELERY_RESULT_BACKEND ='redis://localhost:6379/0'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username', '')
        if not username:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Try use celery for post news to general chat


# def make_celery(app):
#     celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
#                     broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task

#     class ContextTask(TaskBase):
#         abstract = True

#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery


# app.config.update(
#     CELERY_BROKER_URL=CELERY_BROKER_URL,
#     CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND
# )
# celery = make_celery(app)


@app.route('/', methods=['GET'])
@login_required
def index():
    context = {}
    users = User.select()
    username = session['username']
    context['users'] = users
    context['username'] = username
    return render_template('index.html', context=context)


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
            session['room'] = 'general'
            session['roompage'] = 0
            return redirect(url_for('index'), 302)
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
    session.pop('roompage', None)
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
            if not re.findall(r'\d+', roomname):
                Room.create(name=roomname.replace('<script>', '').replace('</script>','').replace('script', ''))
                return jsonify({'message': 'Your room is created', 'roomname': roomname, 'success': True})
            else:
                return jsonify({'message': 'Numbers is not avalible in roomname', 'roomname': roomname, 'success': False})
        else:
            return jsonify({'message': 'Room with that name is currently created', 'success': False})
    else:
        return jsonify({'message': 'Room must have name. Please enter add roomname to post data', 'success': False})


@socketio.on('get_history', namespace='/chat')
def history():
    time = datetime.datetime.now()
    room = session.get('room', 'general')
    roompage = session.get('roompage', 0)
    roompage += 1
    session['roompage'] = roompage
    messages = Message.select().where(Message.roomname == room).order_by(Message.datetime.desc()).paginate(roompage, 10)
    emit('history_info',
         {
          'data': [message.to_dict() for message in messages],
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
          'roomname': room
          },
         room=room
         )


@socketio.on('change_room', namespace='/chat')
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
    room = data['roomname']
    session['room'] = room
    session['roompage'] = 0
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


@socketio.on('change_room_user', namespace='/chat')
def change_room_user(data):
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
    room = generate_roomname(session['username'], data['username'])
    session['room'] = room
    session['roompage'] = 0
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


@socketio.on('connect', namespace='/chat')
def test_connect():
    time = datetime.datetime.now()
    room = session.get('room', 'general')
    session['room'] = 'general'
    session['roompage'] = 0
    link = False
    image = False
    title = False
    join_room(room)
    emit('response',
         {
          'data': 'Connected',
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
          'roomname': room,
          'link': link,
          'image': image,
          'title': title
          },
         room=room
         )


@socketio.on('leave', namespace='/chat')
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
    session['room'] = 'general'
    session['roompage'] = 0
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


@socketio.on('message', namespace='/chat')
def test_message(message):
    time = datetime.datetime.now()
    room = session.get('room', 'general')
    msg = message['data']
    user = User.get(User.username == session['username'])
    Message.create(user=user, roomname=session.get('room', 'general'), message=str(msg))
    link = False
    image = False
    title = False
    if isinstance(msg, basestring):
        msg_list = message['data'].split(' ')
        cmd = msg_list[0]
        link = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', cmd)
        if cmd == '/translate' and len(msg_list) >= 3:
            language = msg_list[1]
            text = ' '.join(msg_list[2:])
            msg = translate(text, language)
        elif link:
            image, title = get_page_info(link[0])
    emit('response',
         {
          'data': msg,
          'username': session.get('username'),
          'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
          'roomname': room,
          'link': link,
          'image': image,
          'title': title
          },
         room=room
         )


# @periodic_task(run_every=timedelta(seconds=300))
# def post_news():
#     links = get_news_links()
#     link = random.choice(links)
#     image = False
#     title = False
#     if link:
#         time = datetime.datetime.now()
#         image, title = get_page_info(link)
#         """
#         Emit doesn`t work.I dont understand why.
#         All infromation is scrap but not send
#         """
#         socketio.emit('response',
#                       {
#                        'data': link,
#                        'username': 'ChatBot',
#                        'datetime': "Created at {:d}:{:02d}".format(time.hour, time.minute),
#                        'roomname': 'general',
#                        'link': link,
#                        'image': image,
#                        'title': title
#                       },
#                       room='general',
#                       broadcast=True)


if __name__ == '__main__':
    socketio.run(app)
