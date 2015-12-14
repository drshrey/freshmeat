from peewee import *
import csv
from db_init import Location, Animal, Division, Murder, BodyPart, Subscriber, PredPrey, LocationMurder, AnimalMurder, DivisionMurder, MurderBodyPart, FullMurder
import random

bodyParts = ['Left Leg', 'Right Leg', 'Left Arm/ Wing', 'Right Arm/ Wing', 'Head', 'Torso']
locations = ['Brooklyn', 'Manhattan', 'Queens', 'Bronx']
animals = ['Dog', 'Cat', 'Deer', 'Rat', 'Horse', 'Pigeon', 'Chicken', 'Pig']

bmoo = 'Borough Maintenance Operations Office - '
office = {
        bmoo + 'Manhattan': 'Manhattan',
        bmoo + 'Brooklyn': 'Brooklyn',
        bmoo + 'Queens': 'Queens',
        bmoo + 'Bronx': 'Bronx'
        }

'''
with open('test_incidents.csv') as f:
    spamreader = csv.reader(f, delimiter=',',quotechar='|')
    for row in spamreader:
        animal = Animal.get(Animal.name==row[0])
        quantity = row[1]
        bodyPart = BodyPart.get(BodyPart.name==row[2])
        date_started = row[3]
        import datetime
        date_started = datetime.datetime.strptime(date_started, "%m/%d/%Y %I:%M:%S")
        print date_started
        date_closed = row[4]
        date_closed = datetime.datetime.strptime(date_closed, "%m/%d/%Y %I:%M:%S")
        print date_closed
        source = row[5]
        
        division = Division.get(Division.name==office[row[6]])
        form = row[7]
        status = row[8]
        priority = row[9]
        complaint_type = row[14]
        resolution = row[-1]

        location = Location(address=row[10] + row[11] + row[12] + row[13])
        location.save()

        murder = Murder(
                quantity=quantity,
                date_started=date_started,
                date_closed=date_closed,
                source=source,
                form=form,
                status=status,
                priority=priority,
                complaint_type=complaint_type,
                resolution=resolution)
        murder.save()

        locationMurder = LocationMurder(location=location, murder=murder)
        locationMurder.save()
        
        animalMurder = AnimalMurder(animal=animal, murder=murder)
        animalMurder.save()

        divisionMurder = DivisionMurder(division=division, murder=murder)
        divisionMurder.save()

        locationMurder = LocationMurder(location=location, murder=murder)
        locationMurder.save()

        murderBodyPart = MurderBodyPart(murder=murder, body_part=bodyPart)
        murderBodyPart.save()

        # FUll MURDER
        fm = FullMurder(animal=animal, division=division, location=location, body_part=bodyPart,  murder=murder)
        fm.save()
'''
