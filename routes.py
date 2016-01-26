''' Builtin '''
import json
import time
import random
import datetime
from threading import Thread

''' MySQL Related'''
from peewee import * # ORM

''' Flask Related '''
from flask import render_template, request, jsonify

''' User Local '''
from app import app
from random_entries import ANIMALS
from lib import getFullMurder, backgroundThread
from models import Location, Animal, PredPrey, Division, Murder, \
    AnimalMurder, DivisionMurder,LocationMurder, BodyPart, \
    MurderBodyPart, Subscriber, SubscriberAnimal, SubscriberBodyPart, \
    SubscriberDivision, FullSubscriber, FullMurder

thread = None

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=backgroundThread)
        thread.daemon = True
        thread.start()
    return render_template('index.html')

@app.route('/subscribe_user', methods=['POST', 'GET'])
def subscribeUser():
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
    
    def getFullSubscriber(sub):
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
    '''
    def get_neighborhood_wl(sub):
        #Get div
        div = SubscriberDivision.select().where(SubscriberDivision.subscriber == sub).get().division
        full_wl = FullSubscriber.select().where(FullSubscriber.division==div)
        return full_wl
    '''

    def getPredPrey(x):
        fm = { 
            "animal": x.animal.name,
            "division": x.division.name,
            "location": x.location.address,
            "body_part":x.body_part.name
        }
        print fm
        return fm


    if request.method == "POST":
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
        prey = [x.preyAnimal for x in PredPrey.select(PredPrey, Animal).join(Animal).where(PredPrey.predAnimal == fs.animal)]

        preyMurders = []
        for p in prey:
            q = FullMurder.select(FullMurder, Animal, Division, Location, BodyPart).join(Animal).switch(FullMurder).join(Division).switch(FullMurder).join(Location).switch(FullMurder).join(BodyPart).where(FullMurder.animal == p and FullMurder.division == fs.division)
            preyMurders.extend([x for x in q])
        watchlist = FullSubscriber.select(FullSubscriber, Subscriber, Animal, BodyPart, Division).join(Subscriber).switch(FullSubscriber).join(Animal).switch(FullSubscriber).join(BodyPart).switch(FullSubscriber).join(Division).where(FullSubscriber.division == fs.division and FullSubscriber.subscriber != fs.subscriber)
        results['prey'] = [getPredPrey(pm) for pm in preyMurders]
        results['watchlist'] = [getFullSubscriber(sub) for sub in watchlist]
        results['subFull'] = getFullSubscriber(fs)
        results['borough'] = fs.division.name
        results['number'] = fs.subscriber.number
    if request.method == 'GET':
        sub = None
        print request.args.get('number')
        phonenumber = request.args.get('number')
        try:
            sub = Subscriber.get(Subscriber.number== phonenumber)
        except:
            return render_template('error.html', error='Number does not exist. Subscribe by going to subscribe page and registering!')
        fs = FullSubscriber.get(FullSubscriber.subscriber == sub)
        prey = [x.preyAnimal for x in PredPrey.select(PredPrey, Animal).join(Animal).where(PredPrey.predAnimal == fs.animal)]

        preyMurders = []
        for p in prey:
            q = FullMurder.select(FullMurder, Animal, Division, Location, BodyPart).join(Animal).switch(FullMurder).join(Division).switch(FullMurder).join(Location).switch(FullMurder).join(BodyPart).where(FullMurder.animal == p and FullMurder.division == fs.division)
            preyMurders.extend([x for x in q])
        watchlist = FullSubscriber.select(FullSubscriber, Subscriber, Animal, BodyPart, Division).join(Subscriber).switch(FullSubscriber).join(Animal).switch(FullSubscriber).join(BodyPart).switch(FullSubscriber).join(Division).where(FullSubscriber.subscriber != fs.subscriber, FullSubscriber.division == fs.division)
        results['prey'] = [getPredPrey(pm) for pm in preyMurders]
        results['watchlist'] = [getFullSubscriber(sub) for sub in watchlist]
        results['subFull'] = getFullSubscriber(fs)
        results['borough'] = fs.division.name
        results['number'] = fs.subscriber.number
    return render_template("subscriber_results.html", results=results)

@app.route('/query', methods=['GET'])
def query():
    if request.method == 'GET':
        print dir(request)
        print request.get_json()
    return render_template('query.html')

@app.route('/advanced_query_request', methods=['GET'])
def advancedQueryRequest():
    return jsonify({'message':"hello. is it me you're looking for?"})

@app.route('/basic_query_request', methods=['GET'])
def queryRequest():
    animal = request.args.get('animal')
    bodypart = request.args.get('bodypart')
    left = "Left" + bodypart
    right = "Right" + bodypart

    query = FullMurder.select(FullMurder, Animal, Location, Division, BodyPart, Murder).join(Animal).switch(FullMurder).join(Location).switch(FullMurder).join(Division).switch(FullMurder).join(BodyPart).switch(FullMurder).join(Murder).switch(FullMurder).where((Animal.name != animal) & (BodyPart.name == left) | (Animal.name == animal) & (BodyPart.name == right)).aggregate_rows()

    best_locations= FullMurder.select(FullMurder, Animal, Location, Division, BodyPart, Murder).join(Animal).switch(FullMurder).join(Location).switch(FullMurder).join(Division).switch(FullMurder).join(BodyPart).switch(FullMurder).join(Murder).switch(FullMurder).where((Animal.name != animal) & (BodyPart.name == left) | (Animal.name != animal) & (BodyPart.name == right)).aggregate_rows()
    '''
    division_count = {}
    for l in best_locations:
        if location_count[l.division.name]:
            location_count[l.division.name] += 1
        else:
            location_count[l.division.name] = 1
    best_location = 
    '''

    # Query all records related to the animal
    full_murders = [getFullMurder(am) for am in query]
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