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
from db_init import Murder, Subscriber, animalsDB

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

'''
compute percentages and give comparison
'''
'''
# Division/ Borough 
def compute_division_scores(area, bodyPart=None):
    division = {}
    division["totalDeaths"] = Murder.select().where(Murder.division == area)
    
    for i in ANIMALS:
        """
        (SELECT * FROM murder
            WHERE murder.animal = iterAnimal)
        INNER JOIN
        (SELECT * from murder
            WHERE murder.division=borough)  

        """
        animalDeaths = Murder.select().where(Murder.animal == i)
        division[i + "-deaths"] = (animalDeaths & division["totalDeaths"])
        division[i+"-deathProb"] = float(division[i+"-deaths"] / division["totalDeaths"]) * 100
        if bodyPart:
            bodyPartDeaths = Murder.select().where(Murder.body_part_found == bodyPart)
            animalBodyPartDeaths = (division[i+"-deaths"] & bodyPartDeaths)
            division[i+"-bodyPartProb"] = float( animalBodyPartDeaths / bodyPartDeaths) * 100

    return division
'''
from peewee import SelectQuery
# Overall City
def compute_city_scores(bodyPart=None):
    city = {}
    city["totalDeaths"] = Murder.select()
    for i in ANIMALS:
        animalDeaths = Murder.select().where(Murder.animal == i)
        city[i + "-deaths"] = animalDeaths
        city[i+"-deathProb"] = float( len(city[i+"-deaths"]) / len(city["totalDeaths"]) ) * 100
        if bodyPart:
            bodyPartDeaths = Murder.select().where(Murder.body_part_found == bodyPart)
            animalBodyPartDeaths = Murder.select().where(Murder.animal == i).join(Murder, on=Murder.body_part_found==bodyPart).get()
            print animalBodyPartDeaths
            # animalBodyPartDeaths = (city[i+"-deaths"] bodyPartDeaths)
            city[i+"-bodyPartProb"] = float( len(animalBodyPartDeaths) / len(bodyPartDeaths) ) * 100

    return city

# Animals that animal_type feeds on if it's a carnivore
'''
Gets a list of prey + its addresses + body part if within a week in the same borough
'''
#def prey_address_list(animal_type, borough):
    #prey = 
    #return []


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(1)
        # Make random entry         
        import fn
        import random
        import mysql.connector

        cxn = mysql.connector.connect(user=AWS_MYSQL_USER, password=AWS_MYSQL_PASSWORD, host='freshmeat.c3ne5kfmg1jo.us-west-2.rds.amazonaws.com', database='animals')
        cursor = cxn.cursor()
        query = ("select * from murder order by RAND() limit 1")
        cursor.execute(query)
        for i in cursor:
            randRow = list(i)
        '''
        row = create_entries(1, today=True)[0]
        print row
        newMurder = Murder.create(animal=row[0], quantity=row[1], body_part_found=row[2],
            date_started=row[3], date_closed=row[4], source=row[5], division=row[6],
            form=row[7], status=row[8], priority=row[9], location=row[10],
            complaint_type=row[11], resolution=row[12])
        newMurder.save()
        row.insert(0, "")
        '''

        socketio.emit('murder',
                      {'data': randRow},
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
    BODY_PART_DICT = {
        'la': "Left Arm",
        'ra': "Right Arm",
        'll': "Left Leg",
        "rl": "Right Leg",
        "t": "Tail"
    }
    if request.method == "POST":
        print request.form
        print request.form['number']
        print request.form['borough']
        print request.form['animal']
        print request.form['body_part']
        bp = BODY_PART_DICT[request.form['body_part']]
        print bp
        try:
            newSubscriber = Subscriber(phone_number=request.form['number'], borough=request.form['borough'], animal_type=request.form['animal'], valued_body_part=bp)
            newSubscriber.save()
        except peewee.IntegrityError:
            return render_template("error.html", error="Duplicate Phone Number. Pick Another One.")
        test = Subscriber.get(Subscriber.phone_number == request.form['number'])
        print test
        print test.phone_number
    if request.method == 'GET':
        print "num", request.args.get("number")
        try:
            user = Subscriber.get(Subscriber.phone_number == request.args.get("number"))
            if not user:
                return render_template("error.html", error="Could not find phone number. Try again or subscribe.")
            print user.animal_type
        except:
            return render_template("error.html", error="Phone number does not match any subscriber. Try again or subscribe in the subscribe page")
        '''
        get all results for this user
        '''
        print "vbp", user.valued_body_part
        cityScores = compute_city_scores(bodyPart=user.valued_body_part)
        #divisionScores = compute_division_scores(area=user.borough, bodyPart=user.valued_body_part)
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
    pigeonAndPig = "Pigeon&Pig"
    doveAndChicken = "Dove&Chicken"
    extraAnimals = None
    queryExtra = None
    fullQuery = None

    if request.args.get("animal") in ["Pigeon", "Pig"]:
        extraAnimals = pigeonAndPig
    if request.args.get("animal") in ["Dove", "Chicken"]:
        extraAnimals = doveAndChicken

    queryOne = Murder.select().where(Murder.animal == request.args.get("animal"))
    if extraAnimals:
        queryExtra = Murder.select().where(Murder.animal == extraAnimals)

    if queryExtra:
        fullQuery = (queryOne | queryExtra)
    else:
        fullQuery = queryOne
        
    '''
    Taken from Murder model in db_init:
        animal = TextField()
        quantity = IntegerField()
        body_part_found = TextField()
        date_started = TextField()
        date_closed = TextField()
        source = TextField()
        division = TextField()
        form = TextField()
        status = TextField()
        priority = TextField()
        location = TextField()
        complaint_type = TextField()
        resolution = TextField()
    '''
    queries = []
    for x in fullQuery:
        queries.append((x.animal, x.quantity, x.body_part_found, x.date_started, x.date_closed, x.source, x.division, x.form, x.status, x.priority,x.location, x.complaint_type,x.resolution))
    return render_template('results.html', animal=request.args.get('animal'), queries=queries)

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
