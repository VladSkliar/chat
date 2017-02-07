# Simple chat
### Installation

Just clone repo and change directory. Than open your virtual environment and install requirements package:
```sh
$ pip install -r requirements.txt
```
In models change credentials for you db(if you want):
```sh
db = PooledPostgresqlExtDatabase(database="dbname", user="db_username",
                                 password="db_pass", host="db_host", port=5432,
                                 register_hstore=False, autorollback=True)
```
Run application with gunicorn:
```sh
gunicorn app:app --worker-class eventlet -w 1
```

### In developing the site was used
http://bootsnipp.com/snippets/vrzGb - Free bootstrap template
https://flask-socketio.readthedocs.io/en/latest/ - socketio library for flask

### View deploy chat
https://skliar-chat.herokuapp.com/

P.S.
Enter ``` /help ```  to chat for call list of commands
