import paho.mqtt.client as mqtt
from threading import Thread
from dcd.entities.property import Property
import time
import requests
import json

verifyCert=False
requests.packages.urllib3.disable_warnings()

client = None
mqtt_connected = False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    global mqtt_connected
    mqtt_connected = True

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/things/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def init_mqtt(thing_id, token):
    print('init mqtt')
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # mqtt.on_subscribe = on_subscribe
    # mqtt.on_publish = on_publish
    # mqtt.on_disconnect = on_disconnect
    # mqtt.on_log = on_log

    client.connect(options['mqtt_host'], options['mqtt_port'], 60)
    client.username_pw_set(username=thing_id,
                           password=token)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()


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

options = {
    'mqtt_host': 'dwd.tudelft.nl',
    'mqtt_port': 8883,
    'http_uri': 'https://dwd.tudelft.nl/api'
}


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
                 token=None,
                 on_connect_callback=None):

        self.properties = []
        if json_thing is not None:
            self.thing_id = json_thing.id
            self.name = json_thing.name
            self.description = json_thing.description
            self.thing_type = json_thing.type

            for json_property in json_thing.properties:
                prop = Property(json_property=json_property)
                prop.belongs_to(self)
                self.properties.append(prop)

            self.registered_at = json_thing.registered_at
            self.unregistered_at = json_thing.unegistered_at
        else:
            self.thing_id = thing_id
            self.name = name
            self.description = description
            self.thing_type = thing_type
            self.properties.extend(properties)
            self.private_key_path = private_key_path

        if self.thing_id is not None:
            self.http_uri = options['http_uri']
            if token is not None:
                self.token = token
            else:
                self.token = generate_token(private_key_path)

            self.thread_mqtt = Thread(target = init_mqtt, args = (self.thing_id, self.token))
            self.thread_mqtt.start()

            # self.test()

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
        json = requests.get(uri, headers=headers, verify=verifyCert).json()
        if json["thing"] is not None:
            self.name = json["thing"]["name"]
            self.description = json["thing"]["description"]
            self.thing_type = json["thing"]["type"]
            self.registered_at = json["thing"]["registered_at"]
            self.unregistered_at = json["thing"]["unregistered_at"]
            self.properties = {}

            for json_property in json["thing"]["properties"]:
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
        self.properties.append(created_property)
        return created_property

    def update_property(self, property):
        topic = "/things/" + self.thing_id + "/properties/" + property.property_id
        global mqtt_connected, client
        if mqtt_connected:
            client.publish(topic, json.dumps(property.value_to_json()))
