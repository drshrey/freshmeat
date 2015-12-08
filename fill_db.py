from peewee import *
import csv
from db_init import Murder, animalsDB

AWS_MYSQL_USER = ""
AWS_MYSQL_PASSWORD = ""

with open('creds.txt') as f:
    credentials = [x.strip().split(':') for x in f.readlines()]
    for username, password in credentials:
        AWS_MYSQL_USER = str(username)
        AWS_MYSQL_PASSWORD = str(password)



animalsDB = MySQLDatabase("animals", host="freshmeat.c3ne5kfmg1jo.us-west-2.rds.amazonaws.com", port=3306, user=AWS_MYSQL_PASSWORD, passwd=AWS_MYSQL_USER)

with open('murder.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in spamreader:
		print row[10] + row[11] + row[12] + row[13]
		newMurder = Murder(animal=row[0], quantity=row[1], body_part_found=row[2],
			date_started=row[3], date_closed=row[4], source=row[5], division=row[6],
			form=row[7], status=row[8], priority=row[9], location=row[10] + row[11] + row[12] + row[13],
			complaint_type=row[14], resolution=row[15])
		newMurder.save()
		

for m in Murder.select():
	print m

