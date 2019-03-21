# This example shows how to establish a connection 
# with the DCD HUB using the credentials of a thing.

# This is a typical case for a Python code running 
# on a device to collect data.

from random import random
import time

from dotenv import load_dotenv
import os

from ..entities.thing import Thing

# The thing ID and access token
load_dotenv()
THING_ID = os.environ['THING_ID']
THING_TOKEN = os.environ['THING_TOKEN']

# Instantiate a thing with its credential
my_thing = Thing(thing_id=THING_ID, token=THING_TOKEN)

# Start recording
#
# property_name = 'WebCam'
# port = '/dev/video'
# segment_size = '30'
my_thing.start_video_recording()

# Wait to capture 2 records
time.sleep(70)

my_thing.stop_video_recording()