
from dcd.bucket.thing_token import ThingToken
from dcd.bucket.thing_mqtt import ThingMQTT
from dcd.bucket.thing_http import ThingHTTP
from dcd.bucket.properties.property import Property
from dcd.bucket.properties.ip_address_property import IPAddressProperty
from dotenv import load_dotenv
import requests
import json
import logging
import os
import sys
import signal
import random
import time

load_dotenv()
HTTP_URI = os.getenv('HTTP_URI', 'https://dwd.tudelft.nl:443/bucket/api')
LOG_PATH = os.getenv('LOG_PATH', './logs/')


class Thing:
    """"
    A DCD 'Thing' represents a physical
    or virtual entity collecting data.

    Attributes
    ----------
    thingId: str
    name: str
    description: str
    thing_type: str
    properties : Property[]
    private_key_path : str
    created_at: int
    updated_at: int


    Methods
    -------
    set_log_level(log_level)
    setup_logger()
    to_json()
    from_json()

    """

    def __init__(self,
                 thing_id: str = None,
                 name: str = None,
                 description: str = None,
                 thing_type=None,
                 properties=(),
                 json_thing=None,
                 private_key_path: str = 'private.pem',
                 log_level: str = 'DEBUG'):
        """
        Parameters
        -------

        thing_id : str, optional,
        name : str, optional
        description : str, optional
        thing_type : str, optional
        properties : dict, optional
        json_thing : str, optional
        private_key_path : str, optional
            The path to the private key (default is 'private.pem')
        log_level : str, optional
            The log level (default is 'DEBUG')
        """
        self.set_log_level(log_level)
        self.properties = []
        if json_thing is not None:
            self.from_json(json_thing)
        else:
            self.thing_id = thing_id
            self.name = name
            self.description = description
            self.thing_type = thing_type
            self.properties.extend(properties)
            self.private_key_path = private_key_path

            self.created_at = None
            self.updated_at = None

        self.setup_logger()
        self.video_recorder = None

        # If there is a thing id, try to connect
        if self.thing_id is not None:
            self.http = ThingHTTP(self.logger, self, HTTP_URI)
            self.token = ThingToken(
                private_key_path, self.thing_id, HTTP_URI, HTTP_URI)

            # Loads all thing's details
            if self.http.is_connected():
                self.ip_address_property = IPAddressProperty(self.logger, self)
                # Start the MQTT connection
                self.mqtt = ThingMQTT(self.logger, self)

    def set_log_level(self, log_level):
        if log_level == 'INFO':
            logging.basicConfig(level=logging.INFO)
        elif log_level == 'ERROR':
            logging.basicConfig(level=logging.ERROR)
        elif log_level == 'WARNING':
            logging.basicConfig(level=logging.WARNING)
        elif log_level == 'DEBUG':
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.error('Unknown log level ' + log_level)

    def setup_logger(self):
        self.logger = logging.getLogger(self.thing_id or "Thing")
        log_folder = LOG_PATH + '/' + self.thing_id
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        fh = logging.FileHandler(
            log_folder + '/' + str(time.strftime("%Y-%m-%d_%H")) + '.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def to_json(self):
        t = {}
        if self.thing_id is not None:
            t["id"] = self.thing_id
        if self.name is not None:
            t["name"] = self.name
        if self.description is not None:
            t["description"] = self.description
        if self.thing_type is not None:
            t["type"] = self.thing_type

        t["properties"] = []
        if self.properties is not None and len(self.properties) > 0:
            for index, prop in self.properties.items():
                t["properties"].append(prop.to_json())

        if self.created_at is not None:
            t["createdAt"] = self.created_at
        if self.updated_at is not None:
            t["updatedAt"] = self.updated_at
        return t

    def from_json(self, json_thing):
        if json_thing is not None:
            if "message" in json_thing:
                self.logger.error(json_thing)
            else:
                self.id = json_thing["id"]
                self.name = json_thing["name"]
                self.description = json_thing["description"]
                self.thing_type = json_thing["type"]

                self.created_at = json_thing["createdAt"]
                self.updated_at = json_thing["updatedAt"]

                self.properties = {}

                for json_property in json_thing["properties"]:
                    prop = Property(json_property=json_property)
                    prop.belongs_to(self)
                    self.properties[prop.property_id] = prop
                return True
        return False

    def find_property_by_name(self, property_name_to_find):
        if self.properties is not None and len(self.properties) > 0:
            for index, prop in self.properties.items():
                if prop.name == property_name_to_find:
                    return prop
        self.logger.debug(
            "Property " + property_name_to_find + " was not found.")

    def update_property(self, prop, file_name=None):
        if file_name is None and self.mqtt.is_connected:
            requestId = random.randint(0, 100)
            topic = "/things/" + self.thing_id + "/properties/" + prop.property_id + '/update'
            self.logger.debug('Updating property ' + prop.property_id + '...')
            self.mqtt.publish(topic, json.dumps(
                {'requestId': requestId, 'property': prop.value_to_json()}))
        else:
            self.http.update_property(prop, file_name=file_name)

    def find_or_create_property(self, property_name, typeId):
        """
        Search for a property in thing by name,
        create it if not found & return it
        """
        # property not found
        if self.find_property_by_name(property_name) is None:
            self.http.create_property(name=property_name,
                                      typeId=typeId)

        return self.find_property_by_name(property_name)
