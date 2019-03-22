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
        else:
            self.property_id = property_id
            self.name = name
            self.description = description
            self.property_type = property_type
            self.dimensions = dimensions
            self.values = values

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
 
def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return math.floor((dt - epoch).total_seconds() * 1000.0)
