# This example shows how to establish a connection 
# with Bucket using the credentials of a thing.

# This is a typical case for a Python code running 
# on a device to collect data. 
from random import random
import time

from dcd.bucket.thing import Thing

def main():
    # Instantiate a thing with its credential
    my_thing = Thing()

    # If you just registered your Thing on the DCD Hub,
    # it has only an id, a name and a type.
    print(my_thing.to_json())

    time.sleep(4)
    my_thing.mqtt.read()

    time.sleep(4)
    my_thing.mqtt.find_or_create_property("Accelerometer from MQTT", "ACCELEROMETER")
    

if __name__ == "__main__":
    main()