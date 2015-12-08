from peewee import *
AWS_MYSQL_USER = ""
AWS_MYSQL_PASSWORD = ""

with open('creds.txt') as f:
    credentials = [x.strip().split(':') for x in f.readlines()]
    for username, password in credentials:
        AWS_MYSQL_USER = str(username)
        AWS_MYSQL_PASSWORD = str(password)


animalsDB = MySQLDatabase("animals", host="freshmeat.c3ne5kfmg1jo.us-west-2.rds.amazonaws.com", port=3306, user=AWS_MYSQL_USER, passwd=AWS_MYSQL_PASSWORD)
#animals2DB = MySQLDatabase("animals", host="159.203.64.63", port=3306, user="root", passwd="Idaman2015")

class Murder(Model):
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

	class Meta:
		database = animalsDB


class Subscriber(Model):
	phone_number = CharField(unique=True)
	email = CharField(unique=True)
	animal_type = CharField()

	class Meta:
		database = animalsDB

#animalsDB.drop_tables([Murder, Subscriber])
#animalsDB.create_tables([Murder, Subscriber])



