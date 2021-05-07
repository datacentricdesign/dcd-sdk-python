# This example shows how to establish a connection 
# with Bucket using the credentials of a thing.

# This is a typical case for a Python code running 
# on a device to collect data. 
from random import random
import time

import sys

from dotenv import load_dotenv
import os

# The thing ID and access token
load_dotenv()
THING_ID = os.environ["THING_ID"]
PRIVATE_KEY_PATH = os.environ["PRIVATE_KEY_PATH"]

from dcd.bucket.thing import Thing

def main():
    # Instantiate a thing with its credential
    # By default, looking into .env for THING_ID and PRIVATE_KEY_PATH (default "./private.pem")
    my_thing = Thing(thing_id=THING_ID, private_key_path=PRIVATE_KEY_PATH)

    # Instead you could put your credentials in the code (not recommended)
    # my_thing = Thing(thing_id="dcd:things:...", private_key_path="path/to/private.pem")

    # If we fail to connect to the Thing, we leave the program
    if not my_thing.http.is_connected:
        sys.exit()

    # If you just registered your Thing on the DCD Hub,
    # it has only an id, a name and a type.
    my_thing.describe()

    # If we have no properties, let's create a random one
    my_property = my_thing.find_or_create_property(
        "Random Accelerometer", "ACCELEROMETER")

    # Let's have a look at the property, it should
    # contains the name, a unique id and the dimensions
    my_property.describe()

    # Let's create a function that generate random values
    def generate_dum_property_values(the_property):
        # Define a tuple with the current time, and 3 random values
        values = (random(), random(), random())
        # Update the values of the property
        the_property.update_values(values)

    # # Finally, we call our function to start generating dum values
    while True:
        generate_dum_property_values(my_property)
        # Have a 2-second break
        time.sleep(2)

if __name__ == "__main__":
    main()