# This example shows how to establish a connection
# with the DCD HUB using the credentials of a thing.

# This is a typical case for a Python code running
# on a device to collect data.

from random import random
import time

from ..entities.thing import Thing
from ..entities.property_type import PropertyType

# The thing ID and the path of file containing the private key
THING_ID = "my-wheelchair-3198"
THING_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1NTA1MTY2NjMsImV4cCI6MTg2NjA5NjI2MywiYXVkIjoiaHR0cHM6Ly9kd2QudHVkZWxmdC5ubDo0NDMvYXBpIn0.dgDjRP4xKL5XlhsV9kMMRDWElDXHHLKWEDm6LgSgqJW2JqAoGp_dWIBtfecXrc4ULza28S0TnkQ2tVW1p6u1w8cUWVG0OzBlQ5oNqWEiLf8DstmMU2RwxjruxdjivJ0zT6kszB_FN8RLFf7PJLSqc2GUdbmNQOGIqHfc7DdSaPtcn_iaXJpS9JAbhPx3iChlrU89mNfymlctwEuB1xwyPAftik2MuwQ1BXRusaNdwvGELnT_ByNAr1AeRNaHSlfBxyhIM_qEzbP5k-x5s_RwUDqgbZHxIXpUNTrYvxDPUlfPr4xqathftrITZLKHhv2BN_pmS5dmKD2ekQEfJHnehJQs31gQ6edjbqOdli01Wt-ATkr4n8QgjPYW-z2jsOTz9FI9XMPEkG018f4sDgnnPBF39kzltIZ0FJ3uPnuVhfnNj4T8cCQE_x-uaO0k7LWvzzM6Hgd17EBf1EhaGnPGShLMh8Gz4RG5DqbGV8VAbUx4ahvinOT7Us0CmyD_iqwD0FQVbNDir0BzN093fyCDp5Ww1mJs6a9HikjY0Ns9HpRlFt0AQliMgOZV_H-lwQDRSgKpQFwWb8BASNA5vgkE623xiO2AboXoSeFLYthDPORMcaCMWfjZsL2MSfIjS1MMCjJfuQI3IY9hN7DmnBiYn8qEl2Or-szEe15TQ7mF6TM"

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