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
from random_entries import create_entries, ANIMALS
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from db_init import Location, Animal, PredPrey, Division, Murder, AnimalMurder, DivisionMurder,LocationMurder, BodyPart, MurderBodyPart, Subscriber, SubscriberAnimal, SubscriberBodyPart,SubscriberDivision, FullSubscriber, FullMurder


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

def get_full_murder(murder):

    fm= FullMurder.get(FullMurder.murder == murder)

    import datetime
    import json
    date_handler = lambda obj: (
        obj.isoformat()
        if isinstance(obj, datetime.datetime)
        or isinstance(obj, datetime.date)
        else None
    )

    murderObj = {
            "animal": {'name': fm.animal.name},
            "division": {'name':fm.division.name},
            "location": {'address': fm.location.address},
            "body_part": {'body_part': fm.body_part.name},
            "quantity": fm.murder.quantity,
            "date_started": json.dumps(fm.murder.date_started, default=date_handler),
            "date_closed": json.dumps(fm.murder.date_closed, default=date_handler),
            "source": fm.murder.source,
            "form": fm.murder.status,
            "status": fm.murder.status,
            "priority": fm.murder.priority,
            "complaint_type": fm.murder.complaint_type,
            "resolution": fm.murder.resolution
            }
    return murderObj
            

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(3)
        # Make random entry         
        from peewee import *
        import random
        import json
        randMurder= random.choice([x for x in Murder.select()])
        randMurderJson = json.dumps(get_full_murder(randMurder))
        socketio.emit('murder',
                      {'data': randMurderJson},
                      namespace='/test')

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('index.html')


import peewee
import db_init
@app.route('/subscribe_user', methods=['POST', 'GET'])
def subscribe_user():
    results = {
       'borough': "",
       'number': '',
       'animal': None,
       'prey' : None
    }
    BODY_PART_DICT = {
        'la': "Left Arm",
        'ra': "Right Arm",
        'll': "Left Leg",
        "rl": "Right Leg",
        "t": "Tail"
    }
    
    def get_full_subscriber(sub):
        sub = FullSubscriber.get(FullSubscriber.subscriber)
        return {
                "number": sub.subscriber.number,
                "animal": {
                    "name": sub.animal.name
                    },
                "body_part": {
                    "name": sub.body_part.name
                    },
                "division":{
                    "name": sub.division.name
                    }   
            }

    def get_neighborhood_wl(sub):
        #Get div
        div = SubscriberDivision.select().where(SubscriberDivision.subscriber == sub).get().division
        full_wl = FullSubscriber.select().where(FullSubscriber.division==div)
        return full_wl

    import json
    import datetime
    def get_predprey(sub):
        FORMAT = "%m/%d/%Y %I:%M:%S"
        fs = FullSubscriber.get(FullSubscriber.subscriber == sub)
        prey = PredPrey.select().where(PredPrey.predAnimal == fs.animal)
        preyRecords = []
        predRecords = []
        for p in prey:
            qry = FullMurder.select().where(FullMurder.animal == p)
            for x in qry:
                fm = { 
                "animal": {'name': x.animal.name},
                "division": {'name':x.division.name},
                "location": {'address': x.location.address},
                "body_part": {'body_part': x.body_part.name},
                "quantity": x.murder.quantity,
                "date_started": json.dumps(x.murder.date_started.strftime(FORMAT)),
                "date_closed": json.dumps(x.murder.date_closed.strftime(FORMAT)),
                "source": x.murder.source,
                "form": x.murder.status,
                "status": x.murder.status,
                "priority": x.murder.priority,
                "complaint_type": x.murder.complaint_type,
                "resolution": x.murder.resolution
                }
                preyRecords.append(fm)
 
        
        return preyRecords


    if request.method == "POST":
        print request.form
        print request.form['number']
        print request.form['borough']
        print request.form['animal']
        print request.form['body_part']
        try:
            # Check if number exists
            check = None
            try:
                check = Subscriber.get(Subscriber.number == request.form['number'])
            except:
                pass
            if check:
                return render_template('error.html', error="Number already picked. Try another one.")
            sub = Subscriber(number=request.form['number'])
            sub.save()
            an = Animal.get(Animal.name==request.form['animal'])
            
            sa = SubscriberAnimal(subscriber=sub, animal=an)
            sa.save()

            bodypart = BodyPart.get(BodyPart.name==request.form['body_part'])
            sb = SubscriberBodyPart(subscriber=sub, body_part=bodypart)
            sb.save()
            div= Division.get(Division.name==request.form['borough'])
            sd = SubscriberDivision(subscriber=sub, division=div)
            sd.save()
            fs = FullSubscriber(subscriber=sub, animal=an, body_part=bodypart, division=div)
            fs.save()
        except peewee.IntegrityError:
            return render_template("error.html", error="Duplicate Phone Number. Pick Another One.")
        sub = Subscriber.get(Subscriber.number == request.form['number'])
        subFull = get_full_subscriber(sub)
        wl = get_neighborhood_wl(sub)
        wlSubs = [get_full_subscriber(x) for x in wl]
        results['watchlist'] = wlSubs
        results['subFull'] = subFull
        results['borough'] = subFull['division']['name']
        results['number'] = subFull['number']
        results['animal'] = request.form['animal']
        prey= get_predprey(sub)
        results['prey'] = prey
        print subFull
        print wl
    if request.method == 'GET':
        sub = None
        print request.args.get('number')
        phonenumber = request.args.get('number')
        try:
            sub = Subscriber.get(Subscriber.number== phonenumber)
        except:
            return render_template('error.html', error='Number does not exist. Subscribe by going to subscribe page and registering!')
        subFull = get_full_subscriber(sub)
        wl = get_neighborhood_wl(sub)
        print subFull
        print wl
        wl_subs = []
        if wl:
            for i in wl:
                if i.subscriber.number != sub.number:
                    wl_subs.append(get_full_subscriber(i))
        results['watchlist'] = wl_subs
        results['subFull'] = subFull
        results['borough'] = subFull['division']['name']
        results['number'] = subFull['number']
        results['animal'] = subFull['animal']['name']
        prey= get_predprey(sub)
        results['prey'] = prey
        print results['prey']


    return render_template("subscriber_results.html", results=results)

@app.route('/query', methods=['GET'])
def query():
    if request.method == 'GET':
        print dir(request)
        print request.get_json()
    return render_template('query.html')

@app.route('/advanced_query_request', methods=['GET'])
def advanced_query_request():
    return jsonify({'message':"hello. is it me you're looking for?"})

@app.route('/basic_query_request', methods=['GET'])
def query_request():
    animal = request.args.get('animal')
    bodypart = request.args.get('bodypart')

    left= "Left"
    right = "Right"

    # Query all records related to the animal
    animal = Animal.select().where(Animal.name == animal).get()
    fm_models = FullMurder.select().where(FullMurder.animal == animal)
    full_murders = [get_full_murder(am.murder) for am in fm_models]
    # Query all records related to the body part and get the borough with the most of that leg type
    return render_template('results.html', queries=full_murders)

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
