''' User Related '''
from lib import setAsyncMode, getCreds

''' Flask Related '''
from flask import Flask, session
from flask_socketio import SocketIO, emit

ASYNC_MODE = setAsyncMode()
AWS_MYSQL_USER, AWS_MYSQL_PASSWORD = getCreds()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=ASYNC_MODE)

# Import all routes and socketio routes
from routes import *
from sockets import *
    
if __name__ == '__main__':
    socketio.run(app, port=5000,debug=True)
