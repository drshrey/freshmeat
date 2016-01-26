import datetime
import json
from peewee import *
import random

'''getCreds returns credentials in current directory
   @returns (str, str) in format (username, password)
'''
def getCreds():
	with open('creds.txt') as f:
	    credentials = [x.strip().split(':') for x in f.readlines()]
	    for username, password in credentials:
	    	return (str(username), str(password))

'''setAsyncMode finds the most optimal async library in the system
   and returns that as the async_mode
'''
def setAsyncMode():
    async_mode = None
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
    return async_mode


'''getFullMurder serializes FullMurder Model objects 
   and returns the JSON output
   @param: full_murder_obj - unserialized FullMurder object
   @return: murderObj - serialized JSON FullMurder object
'''
def getFullMurder(full_murder_obj):
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
            

def backgroundThread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(3)
        # Make random entry  
        randMurder= random.choice([x for x in FullMurder.select()])
        randMurderJson = json.dumps(getFullMurder(randMurder))
        socketio.emit('murder',
                      {'data': randMurderJson},
                      namespace='/test')