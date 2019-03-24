# This example shows interact with the DCD Hub to explore the data 
# within a notebook like Jupiter. 

from ..entities.thing import Thing
from ..entities.person import Person
from ..entities.property import PropertyType

# If you use Jupiter on the DCD Hub, you can skip this step
# as it is performed automatically.
import os
PERSON_ID = os.environ['PERSON_ID']
PERSON_SECRET = os.environ['PERSON_SECRET']
me = Person(PERSON_ID, PERSON_SECRET)
dcd_hub = me.dcd_hub


# we want the location
# person.id, time, person.age, person.gender, person.motion, person.location,
# person has property equal to
# thing has property


#persons_with_location = dcd_hub.list_persons(has_properties=PropertyType.LOCATION)

#for person in persons_with_location:


#cd_hub.list_things(has_)
