from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO
from models import User
from functools import wraps

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'my_secret_key'
socketio = SocketIO(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session.keys():
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
        return render_template('register.html', context=responce_context)
    except UserDoesNotExist:
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
        if user.password == password:
            session['username'] = username
            return redirect(url_for('index'))
        response_context['message'] = 'Your user credentials is wrong'
        return render_template('login.html', context=responce_context)
    except UserDoesNotExist:
        response_context['message'] = 'Your user credentials is wrong'
        return render_template('login.html', context=responce_context)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    socketio.run(app)
