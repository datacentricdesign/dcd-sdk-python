# This example shows how to establish a connection 
# with the DCD HUB using the credentials of a thing.

# This is a typical case for a Python code running
# on a device to collect data.

import time
import os
from dotenv import load_dotenv
from datetime import datetime
import math

from ..entities.thing import Thing
from ..entities.property import PropertyType

# The thing ID and access token
load_dotenv()
THING_ID = os.environ['THING_ID']
THING_TOKEN = os.environ['THING_TOKEN']

# Instantiate a thing with its credential
my_thing = Thing(thing_id=THING_ID, token=THING_TOKEN)

# We can fetch the details of our thing
my_thing.read()

def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return math.floor((dt - epoch).total_seconds() * 1000.0)

# If you just registered your Thing on the DCD Hub,
# it has only an id, a name and a type.
print(my_thing.to_json())

fsr = my_thing.properties["fsr-1ebb"]

dt = datetime.utcnow()
ts = unix_time_millis(dt)
fsr.read(ts-3600000, ts)

print(fsr.to_json())