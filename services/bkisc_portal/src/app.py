from flask import Flask,request, Response, render_template_string, g, session
import sqlite3
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(1)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('./database.db')
        db.isolation_level = None
        db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    with app.app_context():
        cur = get_db().execute(query, args)
        rv = [dict((cur.description[idx][0], str(value))
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv
    
def init_db():
    with open('./schema.sql', mode='r') as f:
        sql = f.read()
        get_db().cursor().executescript(sql)


@ app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@ app.route('/', methods=['GET'])
def index():
    return Response(render_template_string("""<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>Are you the member of {{ title }}</h1>
    <form action="/login" method="post">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <br><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>""", title="BKISC Portal"), mimetype='text/html')

@ app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username", "nobody")
    password = request.form.get("password", "nobody")
    token = request.form.get("token", "0")
    if session.get('user', 'nobody') == 'nobody':
        try:
                sql = "SELECT * FROM users WHERE (usrname='%s' AND passwd='%s') OR token=%s;" % (username, password, token)
                result = query_db(sql, one=True)
                print(result)
                session['user'] = result['usrname']
        except:
            return Response(render_template_string("Invalid Credential"), mimetype='text/plain')    
    if session['user'] == 'bkisc_admin':
        secret = open("/flag1.txt", "r").read()
        return render_template_string("Hello admin, your secret is {{flag}}", flag=secret)
    else:
        return render_template_string("Hello %s, how are you today?" % result['usrname'])
app.before_request_funcs = {None: [init_db]}    