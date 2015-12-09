from peewee import *
AWS_MYSQL_USER = ""
AWS_MYSQL_PASSWORD = ""

with open('creds.txt') as f:
    credentials = [x.strip().split(':') for x in f.readlines()]
    for username, password in credentials:
        AWS_MYSQL_USER = str(username)
        AWS_MYSQL_PASSWORD = str(password)


animalsDB = MySQLDatabase("animals", host="freshmeat.c3ne5kfmg1jo.us-west-2.rds.amazonaws.com", port=3306, user=AWS_MYSQL_USER, passwd=AWS_MYSQL_PASSWORD)
#animalsDB = MySQLDatabase("animals2", host="freshmeat.c3ne5kfmg1jo.us-west-2.rds.amazonaws.com", port=3306, user=AWS_MYSQL_USER, passwd=AWS_MYSQL_PASSWORD)

class Murder(Model):
	animal = TextField()
	quantity = IntegerField()
	body_part_found = TextField()
	date_started = DateTimeField()
	date_closed = DateTimeField()
	source = TextField()
	division = TextField()
	form = TextField()
	status = TextField()
	priority = TextField()
	location = TextField()
	complaint_type = TextField()
	resolution = TextField()

	class Meta:
		database = animalsDB

'''

class Animal(Model):
	is_carnivore = BooleanField(default=False)
	animal_name = TextField()

	class Meta:
		database = animalsDB

# Junction Table
class AnimalPrey(Model):
	prey = ForeignKeyField(Animal, related_name='prey')

	class Meta:
		database = animalsDB


class AnimalMurder(Model):
	animal = ForeignKeyField(Animal, related_name='murder')
	murder = ForeignKeyField(Murder, related_name='animal')

	class Meta:
		database = animalsDB
'''

class Subscriber(Model):
	phone_number = IntegerField(unique=True)
	borough = TextField()
	animal_type = CharField()
	valued_body_part = TextField()

	class Meta:
		database = animalsDB

#animalsDB.drop_tables([Subscriber])
#animalsDB.create_tables([Subscriber])



