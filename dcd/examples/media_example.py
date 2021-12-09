# This example shows how to establish a connection 
# with Bucket using the credentials of a thing.

# This is a typical case for a Python code running 
# on a device to collect data. 
from random import random
import time

import sys

from dcd.bucket.thing import Thing

def main():
    # Instantiate a thing with its credential
    # By default, looking into .env for THING_ID and PRIVATE_KEY_PATH (default "./private.pem")
    my_thing = Thing()

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
        "Test image PNG", "IMAGE_PNG")

    # Let's have a look at the property, it should
    # contains the name, a unique id and the dimensions
    my_property.describe()

    # Define a tuple with the width and height of the image
    values = (25, 25)

    # Update the values of the property, join the file along
    # It returns the timestamp, helpful as we did not specified any ourself
    ts = my_property.update_values(values=values, file_name="test_image.png")

    # We use the timestamp to get back the image
    file_content = my_property.read_media('image-png', ts)

    # Finally we can write the content into a file
    with open('received_image.png','wb') as f:
        f.write(file_content)
    

if __name__ == "__main__":
    main()