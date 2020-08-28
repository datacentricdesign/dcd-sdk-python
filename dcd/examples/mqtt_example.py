# This example shows how to establish a connection 
# with Bucket using the credentials of a thing.

# This is a typical case for a Python code running 
# on a device to collect data. 
from random import random
import time

from dotenv import load_dotenv
import os
import sys

from dcd.entities.thing import Thing

def main():
    # The thing ID
    load_dotenv()
    THING_ID = os.environ['THING_ID']

    # Instantiate a thing with its credential
    my_thing = Thing(thing_id=THING_ID)

    # If you just registered your Thing on the DCD Hub,
    # it has only an id, a name and a type.
    print(my_thing.to_json())

    time.sleep(4)
    my_thing.readMQTT()

    time.sleep(4)
    my_thing.find_or_create_propertyMQTT("Accelerometer from MQTT", "ACCELEROMETER")
    

if __name__ == "__main__":
    main()