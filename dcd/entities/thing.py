import paho.mqtt.client as mqtt
from threading import Thread
from dcd.entities.property import Property
from dcd.entities.property_type import PropertyType
import requests
import json

from dcd.helpers.mqtt import mqtt_result_code

requests.packages.urllib3.disable_warnings()

verifyCert = True

from dotenv import load_dotenv
import os

load_dotenv()
MQTT_HOST = os.getenv('MQTT_HOST', 'dwd.tudelft.nl')
MQTT_PORT = os.getenv('MQTT_PORT', 8883)
HTTP_URI = os.getenv('HTTP_URI', 'https://dwd.tudelft.nl/api')

import logging
logging.basicConfig(level=logging.DEBUG)

def generate_token(private_key_path):
    # Read key from file
    # priv_pem = open(private_key_path, 'r').read()
    # payload = {
    #     'iat': datetime.datetime.utcnow(),
    #     'exp': datetime.timedelta(minutes=5),
    #     'aud': self.http_uri
    # }
    # private_key = jwk.JWK.from_pem(priv_pem)
    # return jwt.generate_jwt(payload, private_key, 'RS256',
    #                         datetime.timedelta(minutes=5))
    return ""


class Thing:
    """"A DCD 'Thing' represents a physical or virtual entity collecting data."""

    def __init__(self,
                 thing_id=None,
                 name=None,
                 description=None,
                 thing_type=None,
                 properties=(),
                 json_thing=None,
                 private_key_path=None,
                 token=None):

        self.properties = []
        if json_thing is not None:
            self.thing_id = json_thing.id
            self.name = json_thing.name
            self.description = json_thing.description
            self.thing_type = json_thing.type

            for json_property in json_thing.properties:
                prop = Property(json_property=json_property)
                prop.belongs_to(self)
                self.properties[prop.property_id] = prop

            self.registered_at = json_thing.registered_at
            self.unregistered_at = json_thing.unegistered_at
        else:
            self.thing_id = thing_id
            self.name = name
            self.description = description
            self.thing_type = thing_type
            self.properties.extend(properties)
            self.private_key_path = private_key_path

        self.mqtt_client = None
        self.mqtt_connected = False

        self.logger = logging.getLogger(self.thing_id or "Thing")

        if self.thing_id is not None:
            self.http_uri = HTTP_URI
            if token is not None:
                self.token = token
            else:
                self.token = generate_token(private_key_path)

            self.thread_mqtt = Thread(target=self.init_mqtt)
            self.thread_mqtt.start()

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
        if self.properties is not None:
            for index, prop in self.properties.items():
                t["properties"].append(prop.to_json())

        if self.registered_at is not None:
            t["registered_at"] = self.registered_at
        if self.unregistered_at is not None:
            t["unregistered_at"] = self.registered_at
        return t

    def read(self):
        uri = self.http_uri + "/things/" + self.thing_id
        headers = {'Authorization': 'bearer ' + self.token}
        json_result = requests.get(uri, headers=headers,
                                   verify=verifyCert).json()
        if json_result["thing"] is not None:
            json_thing = json_result["thing"]
            self.name = json_thing["name"]
            self.description = json_thing["description"]
            self.thing_type = json_thing["type"]
            self.registered_at = json_thing["registered_at"]
            self.unregistered_at = json_thing["unregistered_at"]
            self.properties = {}

            for json_property in json_thing["properties"]:
                prop = Property(json_property=json_property)
                prop.belongs_to(self)
                self.properties[prop.property_id] = prop

    def find_property_by_name(self, property_name_to_find):
        for index, prop in self.properties.items():
            if prop.name == property_name_to_find:
                return prop

    def create_property(self, name, property_type):
        my_property = Property(name=name,
                               property_type=property_type)
        headers = {'Authorization': 'bearer ' + self.token}
        uri = self.http_uri + "/things/" + self.thing_id + "/properties"
        response = requests.post(uri, headers=headers, verify=verifyCert,
                                 json=my_property.to_json())
        created_property = Property(json_property=response.json()['property'])
        created_property.belongs_to(self)
        self.properties[created_property.property_id] = created_property
        return created_property

    def update_property(self, prop):
        topic = "/things/" + self.thing_id + "/properties/" + prop.property_id
        if self.mqtt_connected:
            self.logger.debug('Updating property ' + prop.property_id)
            self.mqtt_client.publish(topic,
                                     json.dumps(prop.value_to_json()))

    def read_property(self, property_id, from_ts=None, to_ts=None):
        prop = self.properties[property_id]
        if prop is not None:
            uri = self.http_uri + "/things/" + self.thing_id
            uri += "/properties/" + property_id
            if from_ts is not None and to_ts is not None:
                uri += "?from=" + str(from_ts) + "&to=" + str(to_ts)
            headers = {'Authorization': 'bearer ' + self.token}
            json_result = requests.get(uri, headers=headers,
                                       verify=verifyCert).json()

            if json_result["property"] is not None:
                prop.name = json_result['property']['name']
                prop.description = json_result['property']['description']
                prop.property_type = PropertyType[
                    json_result['property']['type']]
                prop.dimensions = json_result['property']['dimensions']
                prop.values = json_result['property']['values']
                return prop
            raise ValueError(
                "read_property() - unknown response: " + json_result)
        raise ValueError("Property id '" + property_id + "' not part of Thing '"
                         + self.thing_id + "'. Did you call read_thing() first?")

    def init_mqtt(self):
        self.logger.info(
            'Initialising MQTT connection for Thing \'' + self.thing_id + '\'')

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        # self.mqtt_client.on_subscribe = self.on_mqtt_subscribe
        # mqtt.on_publish = on_publish
        # mqtt.on_disconnect = on_disconnect
        # mqtt.on_log = on_log

        self.mqtt_client.username_pw_set(username=self.thing_id,
                                         password=self.token)
        self.mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.mqtt_client.loop_forever()

    # The callback for when the client receives a CONNACK response from the server.
    def on_mqtt_connect(self, client, userdata, flags, rc):
        self.logger.info(mqtt_result_code(rc))

        self.mqtt_connected = True

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.

        # self.mqtt_client.subscribe([("/things/" + self.thing_id + "/#",1)])

    # The callback for when a PUBLISH message is received from the server.
    def on_mqtt_message(self, client, userdata, msg):
        self.logger.info("Received message on topic "
                    + msg.topic + ": " + str(msg.payload))
