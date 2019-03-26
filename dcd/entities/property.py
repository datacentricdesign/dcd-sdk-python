import math

from datetime import datetime
from enum import Enum

"""----------------------------------------------------------------------------
    Class that contains all possible property types for a property in a thing
----------------------------------------------------------------------------"""


class PropertyType(Enum):
    ONE_DIMENSION = "1D"
    TWO_DIMENSIONS = "2D"
    THREE_DIMENSIONS = "3D"
    FOUR_DIMENSIONS = "4D"
    FIVE_DIMENSIONS = "5D"
    SIX_DIMENSIONS = "6D"
    SEVEN_DIMENSIONS = "7D"
    EIGHT_DIMENSIONS = "8D"
    NINE_DIMENSIONS = "9D"
    TEN_DIMENSIONS = "10D"
    ELEVEN_DIMENSIONS = "11D"
    TWELVE_DIMENSIONS = "12D"
    ACCELEROMETER = "ACCELEROMETER"
    GYROSCOPE = "GYROSCOPE"
    BINARY = "BINARY"
    MAGNETIC_FIELD = "MAGNETIC_FIELD"
    GRAVITY = "GRAVITY"
    ROTATION_VECTOR = "ROTATION_VECTOR"
    LIGHT = "LIGHT"
    LOCATION = "LOCATION"
    ALTITUDE = "ALTITUDE"
    BEARING = "BEARING"
    SPEED = "SPEED"
    PRESSURE = "PRESSURE"
    PROXIMITY = "PROXIMITY"
    RELATIVE_HUMIDITY = "RELATIVE_HUMIDITY"
    COUNT = "COUNT"
    FORCE = "FORCE"
    TEMPERATURE = "TEMPERATURE"
    STATE = "STATE"
    VIDEO = "VIDEO"
    CLASS = "CLASS"


class Property:
    """"A DCD 'Property' represents a numerical property of a Thing."""

    def __init__(self,
                 property_id=None,
                 name=None,
                 description=None,
                 property_type=None,
                 dimensions=(),
                 json_property=None,
                 values=(),
                 classes=None,
                 entity=None):

        self.subscribers = []
        self.entity = entity

        if json_property is not None:
            self.property_id = json_property['id']
            self.name = json_property['name']
            self.description = json_property['description']
            self.property_type = PropertyType[json_property['type']]
            self.dimensions = json_property['dimensions']
            self.values = json_property['values']
            self.classes = json_property['classes']
        else:
            self.property_id = property_id
            self.name = name
            self.description = description
            self.property_type = property_type
            self.dimensions = dimensions
            self.values = values
            self.classes = classes

    def to_json(self):
        p = {}
        if self.property_id is not None:
            p["id"] = self.property_id
        if self.name is not None:
            p["name"] = self.name
        if self.description is not None:
            p["description"] = self.description
        if self.property_type is not None:
            p["type"] = self.property_type.name
        if self.dimensions is not None and len(self.dimensions) > 0:
            p["dimensions"] = self.dimensions
        if self.values is not None and len(self.values) > 0:
            p["values"] = self.values
        if self.classes is not None and len(self.classes) > 0:
            p["classes"] = self.classes
        return p

    def value_to_json(self):
        p = {}
        if self.property_id is not None:
            p["id"] = self.property_id
        if self.values is not None and len(self.values) > 0:
            p["values"] = self.values
        return p

    def belongs_to(self, entity):
        self.entity = entity

    def update_values(self, values, time_ms=None, file_name=None):
        ts = time_ms
        if ts is None:
            dt = datetime.utcnow()
            ts = unix_time_millis(dt)

        values_with_ts = [ts]
        values_with_ts.extend(values)

        # TODO: Remove the following line to accumulate local history
        # (it requires more advanced sync management)
        self.values = []
        self.values.append(values_with_ts)

        if self.property_type == PropertyType.VIDEO and file_name is None:
            raise ValueError('Missing file name for VIDEO property update.')

        self.entity.update_property(self, file_name)

    def read(self, from_ts=None, to_ts=None):
        self.entity.read_property(self.property_id, from_ts, to_ts)

    def subscribe(self, uri):
        self.subscribers.append(uri)

<<<<<<< HEAD
    """----------------------------------------------------------------------------
        Uploads file to the property given filename, file type,  data(list of values 
        for the property that will receive it)  an authentification class auth, 
        which contains the thing ID and token, and url (by default gets 
        reconstructed automatically)

        FOR VIDEO:
        data dictionary  must have following pairs  start_ts & duration defined
        like so : {'start_ts': ... , 'duration': ...}
    ----------------------------------------------------------------------------""" 
    def upload_file(self, file_name, file_type, data, auth, url = None):
        #  print statement for what function will do
        print('Uploading ' + file_name + ' of file type ' + file_type +
              ' to property ' + self.name)

        if file_type == 'video': #  Uploading file of type video 
            #  in files, we create a dictionary that maps 'video' to a tuple 
            #  (read only list) composed of extra data : name, file object
            #  type of video (mp4 by default), and expiration tag (also a dict)(?)
            files = {'video': ( file_name, open('./' + file_name, 'rb') ,
                                'video/mp4' , {'Expires': '0'} ) }

            #  creating our video url for upload
            if url is None:
                url = 'https://dwd.tudelft.nl/api/things/' + auth.THING_ID + \
                      '/properties/' + self.property_id + '/values/' + \
                      str(data['start_ts']) + ',' + str(data['duration']) + '/file'
        else:
            print("File type not yet supported")
            return(-1)

        
        

        #  sending our post method to upload this file, using our authentification
        #  data dict is converted into a list for all the values of the property
        response = requests.post(url=url, data= {'values': data.values()}, files=files,
                                 headers={ "Authorization": "bearer " + 
                                 auth.THING_TOKEN})

         
        print(response.status_code) #  print response code of the post
                                    #  method, by the requests library 
        return(response.status_code)  
 
=======
    def align_values_to(self, prop2):
        """
            Create if missing, an intermediary row of values
            for each timestamp in prop2
        """
        new_values = []
        values_index = 0
        last_val = None

        # We want to create a row of values for each row of property 2
        for values_prop2 in prop2.values:
            # As long as our property as values with timestamp lower than property 2
            while values_index < len(self.values) and self.values[values_index][0] <= values_prop2[0]:
                last_val = self.values[values_index]
                values_index += 1


            if last_val is not None:
                # Make a copy, change the timestamp to the one in property 2
                # and add it to the new list of values.
                tmp = last_val.copy()
                tmp[0] = values_prop2[0]
                new_values.append(tmp)

        self.values = new_values

    def merge(self, prop2):
        """
            Create a new Property with id and name of form 'prop1+prop2',
            concat dimension and values (MUST have same number of rows)
            and return this new property
        """
        prop3 = Property(property_id=self.property_id + '+' + prop2.property_id,
                         name=self.name + ' + ' + prop2.name)

        # Concat dimensions
        prop3.dimensions = self.dimensions + prop2.dimensions
        # Remove timestamps from property 2
        values2_no_ts = map(lambda x: x[1:], prop2.values)
        # concat property 1 and 2 (only 1 timestamp from prop 1)
        prop3.values = [a+b for a,b in zip(self.values, values2_no_ts)]

        return prop3

    def create_classes(self, classes):
        self.entity.create_classes(self, classes)

>>>>>>> fe1819a028e00a036ec1d4a6187c4020b4a6b753
def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return math.floor((dt - epoch).total_seconds() * 1000.0)
