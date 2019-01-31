# This example shows how to establish a connection
# with the DCD HUB using the credentials of a thing.

# This is a typical case for a Python code running
# on a device to collect data.

from random import random
import time

from ..entities.thing import Thing
from ..entities.property_type import PropertyType

# The thing ID and the path of file containing the private key
THING_ID = "test-thing-cf01"
THING_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1NDg5MTc0MzIsImV4cCI6MTg2NDQ5NzAzMiwiYXVkIjoiaHR0cHM6Ly9kd2QudHVkZWxmdC5ubDo0NDMvYXBpIn0.S1BOVX_Rt_2IjZio67EXSE0iyFcgEsDaJyLu09uLlu3DrzuQwV5mr-y82TBg2O5A4sIeB8pScbjTeIPJ9rjQrJOry6jgvYQT2hVQVzzdC69M5bvOkIHSGzGnBX0f14tdmNHUTDnSt05sO1S-a1E_FecMayWs6SGQGmShITmj4i8AHZ0owJub37r2IilEi0tSrI_m6Ga1Jh22uaKN12em-gHsb4U_rYGpMyo0Lmn7edxO1XrSSPG_vk-B9rY_qM8VW7xy2v6KXaj2o5OxqgID5OTpHMc6Ak5bEKnzBPD2WhUb_S5efiech1ydUoP3TAHb59c_0-nmDRoBDUinQrNVKeqQcYTU71_K4Xhmfgv-Ev1sI4_81OvAUzjawjjXKjnetDwCEqfq9YYK5OKRciCTvl7KPt0xJAzgMb5uOHDuYTDqzWr5HhjElETtiLGv3ZM6nNyw44Yv5SsSabG3WUIC4Si7CSYud6vKNZQbUDhDZ15vlVJ1-QRsWgRapaHByxduaKQj_iOCEdfq6RFo_LKgvQNMUm3DVWtf4zMnQe_FqiP6Urc40_9tmss8GV-snWwwfEyjbGeUcuX-r_8G56HRALgAwiZ0ZQWVIdW3w6o-baCJSf21tG2AJCBvFbybwtC3Sp8TyrhusmnO74XB4QATSIR0IySszaeKfl5D3S5Rc9c"

# Instantiate a thing with its credential
my_thing = Thing(thing_id=THING_ID, token=THING_TOKEN)

# We can fetch the details of our thing
my_thing.read()

# If you just registered your Thing on the DCD Hub,
# it has only an id, a name and a type.
print(my_thing.to_json())

# If we have no properties, let's create a random one
if len(my_thing.properties) == 0:
    # By specifying a property type, the DCD Hub will
    # automatically generate the property dimensions
    # (in this case, 3 generic dimensions)
    my_property = my_thing.create_property(name="My Random Property",
                                           property_type=PropertyType.THREE_DIMENSIONS)

    # Let's have a look at the property, it should
    # contains the name, a unique id and the dimensions
    print(my_property.to_json())

# Whether you have just created a property or you retrieved it
# from the DCD Hub (with my_thing.read), you can look for it by name
# WARNING: if you name two property with the same name, the Hub will
# create them both, but this function will randomly return the first
# it finds.
my_property = my_thing.find_property_by_name("My Random Property")


# Let's create a function that generate random values
def generate_dum_property_values(the_property):
    # Define a tuple with the current time, and 3 random values
    values = (random(), random(), random())
    # Update the values of the property
    the_property.update_values(values)
    # Have a 2-second break
    time.sleep(2)
    # Then call the same function again to generate new values
    generate_dum_property_values(the_property)


# Finally, we call our function to start generating dum values
generate_dum_property_values(my_property)