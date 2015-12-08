#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None
AWS_MYSQL_USER = ""
AWS_MYSQL_PASSWORD = ""

with open('creds.txt') as f:
    credentials = [x.strip().split(':') for x in f.readlines()]
    for username, password in credentials:
        AWS_MYSQL_USER = str(username)
        AWS_MYSQL_PASSWORD = str(password)

print AWS_MYSQL_USER
print AWS_MYSQL_PASSWORD

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(10000)
        # Make random entry 
        from random_entries import create_entries
        import fn
        from db_init import Murder
        import random
        import mysql.connector

        #cxn = mysql.connector.connect(user=AWS_MYSQL_USER, password=AWS_MYSQL_PASSWORD, 
            #host='freshmeat.c3ne5kfmg1jo.us-west-2.rds.amazonaws.com', database='animals')
        #cursor = cxn.cursor()
        #query = ("select * from murder order by RAND() limit 1")
        #cursor.execute(query)
        #for i in cursor:
        #    randRow = list(i)
        row = create_entries(1, today=True)[0]
        print row
        newMurder = Murder.create(animal=row[0], quantity=row[1], body_part_found=row[2],
            date_started=row[3], date_closed=row[4], source=row[5], division=row[6],
            form=row[7], status=row[8], priority=row[9], location=row[10],
            complaint_type=row[11], resolution=row[12])
        newMurder.save()
        row.insert(0, "")
        socketio.emit('murder',
                      {'data': row},
                      namespace='/test')

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('index.html')

@app.route('/query')
def query():
    return render_template('query.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/submit')
def submit():
    return render_template('submit.html')

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')

@app.route('/about')
def about():
    return render_template('about.html')
    

@socketio.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})


if __name__ == '__main__':
    socketio.run(app, port=5000,debug=True)
