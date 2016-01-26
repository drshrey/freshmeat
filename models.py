''' MySQL Related '''
from peewee import *

''' User Related '''
from lib import getCreds

AWS_MYSQL_USER, AWS_MYSQL_PASSWORD = getCreds()
animalsDB = MySQLDatabase("animals2", host="freshmeat.c3ne5kfmg1jo.us-west-2.rds.amazonaws.com", port=3306, user=AWS_MYSQL_USER, passwd=AWS_MYSQL_PASSWORD)

class Animals2DBModel(Model):
    class Meta:
        database = animalsDB

class Location(Animals2DBModel):
    address = TextField()

class Animal(Animals2DBModel):
    name = TextField()

class PredPrey(Animals2DBModel):
    predAnimal = ForeignKeyField(Animal, related_name='pred')
    preyAnimal = ForeignKeyField(Animal, related_name='prey')

class Division(Animals2DBModel):
    name = TextField()

class Murder(Animals2DBModel):
    quantity = IntegerField()
    date_started = DateTimeField()
    date_closed = DateTimeField()
    source = TextField()
    form = TextField()
    status = TextField()
    priority = TextField()
    complaint_type=TextField()
    resolution = TextField()

class AnimalMurder(Animals2DBModel):
    animal = ForeignKeyField(Animal, related_name='animal_murder')
    murder = ForeignKeyField(Murder, related_name='animal_murder')

class DivisionMurder(Animals2DBModel):
    division = ForeignKeyField(Division, related_name='division_murder')
    murder = ForeignKeyField(Murder, related_name='division_murder')

class LocationMurder(Animals2DBModel):
    location = ForeignKeyField(Location, related_name='location_murder')
    murder = ForeignKeyField(Murder, related_name='location_murder')


class BodyPart(Animals2DBModel):
    name = TextField()

class MurderBodyPart(Animals2DBModel):
    murder = ForeignKeyField(Murder, related_name='murderer_body_part')
    body_part = ForeignKeyField(BodyPart, related_name='murderer_body_part')

class FullMurder(Animals2DBModel):
    animal = ForeignKeyField(Animal, related_name='full_murder')
    division = ForeignKeyField(Division, related_name='full_murder')
    location = ForeignKeyField(Location, related_name='full_murder')
    body_part = ForeignKeyField(BodyPart, related_name='full_murder')
    murder = ForeignKeyField(Murder, related_name='full_murder')

class Subscriber(Animals2DBModel):
    number = TextField()

class FullSubscriber(Animals2DBModel):
    subscriber = ForeignKeyField(Subscriber, related_name='full_sub')
    animal = ForeignKeyField(Animal, related_name='full_sub')
    body_part = ForeignKeyField(BodyPart, related_name='body_part')
    division = ForeignKeyField(Division, related_name='division')

class SubscriberAnimal(Animals2DBModel):
    subscriber = ForeignKeyField(Subscriber, related_name='subscriber_animal')
    animal = ForeignKeyField(Animal, related_name='subscriber_animal')

class SubscriberBodyPart(Animals2DBModel):
    subscriber = ForeignKeyField(Subscriber, related_name='subscriber_body_part')
    body_part = ForeignKeyField(BodyPart, related_name='subscriber_body_part')

class SubscriberDivision(Animals2DBModel):
    subscriber = ForeignKeyField(Subscriber, related_name='subscriber_division')
    division = ForeignKeyField(Division, related_name='subscriber_division')
