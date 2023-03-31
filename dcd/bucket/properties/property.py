import math
import json
from datetime import datetime

# from ..thing import Thing


class Property:
    """"
    A DCD "Property" represents a numerical property of a Thing.
    """

    def __init__(self,
                 property_id: str = None,
                 name: str = None,
                 description: str = None,
                 type_id: str = None,
                 property_type: dict = None,
                 json_property: dict = None,
                 values: dict = (),
                 thing = None):

        self.update_handler = None
        self.thing = thing

        if json_property is not None:
            self.from_json(json_property)
        else:
            self.property_id = property_id
            self.name = name
            self.description = description
            self.type_id = type_id
            self.type = property_type
            self.values = values

    def from_json(self, json_property: dict):
        self.property_id = json_property["id"]
        self.name = json_property["name"]
        self.description = json_property["description"]
        if "type" in json_property:
            self.type = json_property["type"]
            self.type_id = self.type["id"]
        elif json_property["typeId"] is not None:
            self.type_id = json_property["typeId"]
        if "values" in json_property:
            self.values = json_property["values"]
        else:
            self.values = []

    def to_json(self):
        p = {}
        if self.property_id is not None:
            p["id"] = self.property_id
        if self.name is not None:
            p["name"] = self.name
        if self.description is not None:
            p["description"] = self.description
        if self.type_id is not None:
            p["typeId"] = self.type_id
        if self.values is not None and len(self.values) > 0:
            p["values"] = self.values
        if self.thing is not None and self.thing.id is not None:
            p["thing_id"] = self.thing.id
        return p

    def value_to_json(self) -> dict:
        p = {}
        if self.property_id is not None:
            p["id"] = self.property_id
        if self.values is not None and len(self.values) > 0:
            p["values"] = self.values
        return p

    def belongs_to(self, thing):
        self.thing = thing

    def update_values(self, values: dict, time_ms: int = None, file_name: str = None, mode: str = 'w'):
        """Update the values of a property.
        
        Args:
            values: dict
                List containing values [val-dim1, val-dim2,...]
            time_ms : int, optional
                Collection time in milliseconds to add to the values.
                Default to None
            file_name: path to a file to upload (e.g. for video, image or audio properties)
            mode : str, optional
                Control how to manage existing values.
                - 'w' overwrite existing (local) values, replace with new values, and send to the server
                - 'a' append new values after existing values. In this mode, you must call sync() to upload the data on the server. TODO: does not work with files yet.
                Defaults to 'overwrite'.
        """
        ts = time_ms
        if ts is None:
            dt = datetime.utcnow()
            ts = unix_time_millis(dt)

        values_with_ts = [ts]
        values_with_ts.extend(values)

        # TODO: Remove the following line to accumulate local history
        # (it requires more advanced sync management)
        if (mode == 'w'):
            self.values = []
        self.values.append(values_with_ts)

        if self.type_id == "VIDEO" and file_name is None:
            raise ValueError("Missing file name for VIDEO property update.")
        
        if self.type_id == "IMAGE_PNG" and file_name is None:
            raise ValueError("Missing file name for IMAGE_PNG property update.")

        if (mode == 'w'):
            self.thing.update_property(self, file_name)
        return ts

    def sync(self):
        """Upload values to the server and clean up the loacl values"""
        self.thing.update_property(self)
        self.values = []

    def read(self, from_ts = None, to_ts = None, time_interval = None, time_fct = None, shared_with:str=None):
        """Read the details of a property from Bucket

        Args:
            from_ts : int|str, optional
                The start time of the values to fetch. Can be a UNIX timestamp in milliseconds or a string date '%Y-%m-%d %H:%M:%S'. Defaults to None.
            to_ts : int|str, optional
                The end time of the values to fetch.  Can be a UNIX timestamp in milliseconds or a string date '%Y-%m-%d %H:%M:%S'. Defaults to None.
        Returns:
            Property: The property with its details and values.
        """
        DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
        if type(from_ts) is str:
            from_ts = datetime.timestamp(
                datetime.strptime(from_ts, DATE_FORMAT)) * 1000
        if type(to_ts) is str:
            to_ts = datetime.timestamp(
                datetime.strptime(to_ts, DATE_FORMAT)) * 1000
        self.thing.read_property(self.property_id, from_ts, to_ts, time_interval, time_fct, shared_with)

    def read_media(self, dimension_id, ts):
        return self.thing.read_property_media(self.property_id, dimension_id, ts)

    def set_update_handler(self, handler):
        topic = "/things/" + self.thing.thing_id + "/properties/" + self.property_id
        self.update_handler = handler
        if handler is None:
            self.thing.mqtt_client.message_callback_remove(topic)
        else:
            self.thing.mqtt_client.message_callback_add(topic, self.__mqtt_update_handler)
        

    def __mqtt_update_handler(self, client, userdata, msg):
        self.logger.debug("[Property mqtt] Received update")
        if self.update_handler is not None:
            jsonMsg = json.loads(msg.payload)
            self.update_handler(self, msg.payload)
        else:
            self.logger.debug("[Property mqtt] No handler for subscribed update.")


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
            Create a new Property with id and name of form "prop1+prop2",
            concat dimension and values (MUST have same number of rows)
            and return this new property
        """
        prop3 = Property(
            property_id=f"{self.property_id}+{prop2.property_id}",
            name=f"{self.name}+{prop2.name}")

        # Concat dimensions
        prop3.dimensions = self.dimensions + prop2.dimensions
        # Remove timestamps from property 2
        values2_no_ts = map(lambda x: x[1:], prop2.values)
        # concat property 1 and 2 (only 1 timestamp from prop 1)
        prop3.values = [a+b for a, b in zip(self.values, values2_no_ts)]

        return prop3

    def describe(self):
        print(json.dumps(self.to_json(), indent=4, sort_keys=True))

def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return math.floor((dt - epoch).total_seconds() * 1000.0)
