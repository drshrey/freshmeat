import csv
import random


ANIMALS = ['Dog', 'Cat', 'Deer', 'Rat', 'Horse', 'Pigeon', 'Chicken', 'Pig']
BODY_PART_FOUND = ["Left Leg", "Right Leg", "Left Arm/ Wing", 'Right Arm/ Wing', 'Head', 'Torso']
DIVISION = ["Manhattan", "Brooklyn", "Bronx", "Queens"]
PRIORITY = ["Normal", "High", "Low"]
RESOLUTION = ["The Department of Parks and Recreation has completed the requested work order and corrected the problem.",
			  "No action was taken because the Department of Parks and Recreation determined that the issue reported was out of its jurisdiction.",
			  "The condition was determined to be an issue appropriate for handling by an alternate entity. The Department of Parks and Recreation has notified the appropriate resource."]


'''createEntries returns x number of randomly generated entries,
   and the startDate depends on whether today is True or False
'''
def createEntries(numTimes, today=False):
	entries = []
	for i in xrange(numTimes):
		animal = random.choice(ANIMALS)
		quantity = random.choice(range(1,6))
		bodyPartFound = random.choice(BODY_PART_FOUND)
		
		# Create random start date
		import datetime
		startDate = None
		dateClosed = None
		if today == False:
			day = random.choice(range(1,26))
			month = random.choice(range(1,13))
			year = random.choice(range(1990, 2016))
			startDate = datetime.datetime(year, month, day)
			dateClosed = datetime.datetime(year, month, random.choice(range(day, day + 3)))
		else:
			now = datetime.datetime.utcnow()
			day = now.day - 1
			year = now.year
			month = now.month
			import math
			hour = random.choice(range(1, 12))
			minutes = random.choice(range(1,60))
			seconds = random.choice(range(1,60))
			startDate = datetime.datetime(year, month, day, hour, minutes, seconds)
			dateClosed = datetime.datetime(year, month, day, random.choice(range(hour+1, hour + 5)), minutes, seconds)
		
		# end date		
		source = random.choice(["3-1-1 Call Center", "911"])
		division = random.choice(DIVISION)
		form = "DPR General Form"
		status = "Closed"
		priority = random.choice(PRIORITY)
		location = getGoogleMapsLocation(getRandomLocation(division))
		complaintType = random.choice(["Animal in a Park", "Animal on the street", "Remains on Personal Property"])
		resolution = random.choice(RESOLUTION)
		entry = [animal, quantity, bodyPartFound, startDate.strftime("%m/%d/%Y %I:%M:%S"), dateClosed.strftime("%m/%d/%Y %I:%M:%S"), source, "Borough Maintenance Operations Office - " + division, form, status, priority, location, complaintType, resolution]
		entries.append(entry)
	return entries

'''getRandomLocation returns a randomly generated location
   in four of the five boroughs of NYC
'''
def getRandomLocation(division):
	import numpy as np
	# Brooklyn : 40.649848 +- .01, -73.945694 +- 0.01
	# Queens : 40.692597 +- 0.01, -73.806657 +- 0.01
	# Manhattan : 40.776462 +- 0.01, -73.971637 +- 0.005
	# Bronx : 40.859689 +- 0.005, -73.889345 +- 0.005
	location = None
	lat = None
	lon = None
	if(division == "Brooklyn"):
		lat = random.choice(np.arange(40.639848, 40.659848, 0.000001))
		lon = -1 * random.choice(np.arange(73.935694, 73.955694, 0.000001))
	if(division == "Queens"):
		lat = random.choice(np.arange(40.682597, 40.699848, 0.000001))
		lon = -1 * random.choice(np.arange(73.79999, 73.81000, 0.000001))
	if(division == "Manhattan"):
		lat = random.choice(np.arange(40.766462, 40.786462, 0.000001))
		lon = -1 * random.choice(np.arange(73.961637, 73.981637, 0.000001))
	if(division == "Bronx"):
		lat = random.choice(np.arange(40.849689, 40.859689, 0.000001))
		lon = -1 * random.choice(np.arange(73.879345, 73.889345, 0.000001))
	return (lat, lon)

'''getGoogleMapsLocation takes in a latitude, longitude
   and returns the street address of the points.
'''
def getGoogleMapsLocation(latLonTuple):
	import requests
	urlstring = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + str(latLonTuple[0]) + "," + str(latLonTuple[1]) + "&key=AIzaSyCfXhO6AKpfJzviYOkZcRH-mwpBVloWzNQ" 
	formatted_address = requests.get(urlstring, verify=True).json()['results'][0]['formatted_address']
	print str(latLonTuple) + "-->" + formatted_address + "\n"
	return formatted_address


if __name__ == '__main__':
	entries = createEntries(500)
	with open('test_incidents.csv', 'wb') as ti:
		writer = csv.writer(ti, delimiter=',')
		for entry in entries:
			writer.writerow(entry)
			
