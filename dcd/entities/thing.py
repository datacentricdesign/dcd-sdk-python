import paho.mqtt.client as mqtt
from threading import Thread
from dcd.entities.property import Property
import time
import requests
import json

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
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1NDQzNjc4NjksImV4cCI6MTg1OTk0NzQ2OSwiYXVkIjoiaHR0cDovL2xvY2FsaG9zdDo0NDc4L2FwaSJ9.B_sehC-6grT7W2AaAml2h3twbtzBTIUIcgxlZUahaXPdlblKfzNu7mSHEtMe0p6m1NTFXuj4bdT7ImrCWmDA0zZJPyOSZT8Bjgdkr1jd4bw63ci4v86S_Yk2DSquyrXoSLeqFJcaQhig17NQ8RPA1RDJhnjIf6_Ra1kzxVsDhbKuZ9gIso9JZFSrvBFJOTxKiFUq9zAgdof2VL62s9Gu7ywfRkJt6AnM1eKKqnXzRyOkj-0QaHDAF2r92aaW-RFcAx7mJd4yKiycK_W5AbNBwsC2thZ6KliM9CJvaVSRUMGP_WnsOnXbojOB64WPMLUzc8GkJzASwPf96DNOFRQpMlvOyZHD1Ym59TDSz7EA7nydeSHhZhmZoELuhnlpaL1-YvxM34nY1tm_tXTWRtotLLXQF4OaCZ9-auCzqPabAOhQeXuYkyXpOJr_WOeYYWzxaelz2tSkaSgPwaRYxJyZE8gq0Ylf3gANz5BhJQeRnGEsPufjQwicbIbh7kba1GveWWRtPlBBWfVxT-9irxHt3v1RN-YhSu1PWfFOqbb_n9qsbllQMyhRiiOBATSDa7dqvxDN84emWMt7d5AE7cT8doDX47fhaZalkM9gt5PwdSxAQVtY4SgTPzpKK2fi5GPw0NatHgcX0AJXxrD3wMApMYA7vu9A8EpQ8YqtV71cBaY"


options = {
    'mqtt_host': 'localhost',
    'mqtt_port': 1883,
    'http_uri': 'http://localhost:4478/api'
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
            self.token = generate_token(private_key_path)

            self.thread_mqtt = Thread(target = init_mqtt, args = (self.thing_id, self.token))
            self.thread_mqtt.start()

            # self.test()

    def to_json(self):
        p = {}
        if self.thing_id is not None:
            p["id"] = self.thing_id
        if self.name is not None:
            p["name"] = self.name
        if self.description is not None:
            p["description"] = self.description
        if self.thing_type is not None:
            p["type"] = self.thing_type

        p["properties"] = []
        for prop in self.properties:
            p["properties"].append(prop.to_json())

        if self.registered_at is not None:
            p["registered_at"] = self.registered_at
        if self.unregistered_at is not None:
            p["unregistered_at"] = self.registered_at
        return p

    def read(self):
        uri = self.http_uri + "/things/" + self.thing_id
        headers = {'Authorization': 'bearer ' + self.token};
        json = requests.get(uri, headers=headers).json()
        if json["thing"] is not None:
            self.name = json["thing"]["name"]
            self.description = json["thing"]["description"]
            self.thing_type = json["thing"]["type"]
            self.registered_at = json["thing"]["registered_at"]
            self.unregistered_at = json["thing"]["unregistered_at"]
            self.properties = []

            for json_property in json["thing"]["properties"]:
                prop = Property(json_property=json_property)
                prop.belongs_to(self)
                self.properties.append(prop)

    def find_property_by_name(self, property_name_to_find):
        for thing_property in self.properties:
            if thing_property.name == property_name_to_find:
                return thing_property

    def create_property(self, name, property_type):
        my_property = Property(name=name,
                               property_type=property_type)
        headers = {'Authorization': 'bearer ' + self.token}
        uri = self.http_uri + "/things/" + self.thing_id + "/properties"
        response = requests.post(uri, headers=headers,
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
