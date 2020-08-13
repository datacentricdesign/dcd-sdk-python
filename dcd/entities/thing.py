
from threading import Thread
from dcd.entities.property import Property
from dcd.helpers.mqtt import mqtt_result_code
from dcd.helpers.mqtt import check_digi_cert_ca
from dcd.helpers.token import generate_jwt
# from dcd.helpers.video import VideoRecorder
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import requests
import json
import logging
import os
import ssl
import sys
import signal

mqtt_client = None

def keyboardInterruptHandler(signal, frame):
    print("")
    logging.info("Disconnecting...")
    global mqtt_client
    if (mqtt_client is not None):
        mqtt_client.disconnect()
    try:
        sys.exit(0)
    except:
        logging.info('Program closed with CTRL+C')
        os._exit(0)

signal.signal(signal.SIGINT, keyboardInterruptHandler)


requests.packages.urllib3.disable_warnings()

verifyCert = True

load_dotenv()
MQTT_HOST = os.getenv('MQTT_HOST', 'dwd.tudelft.nl')
MQTT_PORT = os.getenv('MQTT_PORT', 8883)
HTTP_URI = os.getenv('HTTP_URI', 'https://dwd.tudelft.nl:443/bucket/api')

"""----------------------------------------------------------------------------
    Convenience class, packs id and token of a thing in standard format
----------------------------------------------------------------------------"""
class ThingCredentials:

    #  constructor
    def __init__(self, THING_ID, THING_TOKEN, api_url="https://dwd.tudelft.nl/bucket/api"):
        self.THING_TOKEN = THING_TOKEN
        self.THING_ID = THING_ID
        self.api_url = api_url


class Thing:
    """"A DCD 'Thing' represents a physical
    or virtual entity collecting data."""

    def __init__(self,
                 thing_id=None,
                 name=None,
                 description=None,
                 thing_type=None,
                 properties=(),
                 json_thing=None,
                 private_key_path='private.pem',
                 token=None,
                 log_level='DEBUG'):

        self.set_log_level(log_level)
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

            self.createdAt = json_thing.createdAt
            self.updatedAt = json_thing.updatedAt
        else:
            self.thing_id = thing_id
            self.name = name
            self.description = description
            self.thing_type = thing_type
            self.properties.extend(properties)
            self.private_key_path = private_key_path

            self.createdAt = None
            self.updatedAt = None

        self.mqtt_client = None
        self.http_connected = False
        self.mqtt_connected = False

        self.logger = logging.getLogger(self.thing_id or "Thing")

        self.video_recorder = None

        if self.thing_id is not None:
            self.http_uri = HTTP_URI
            if token is not None:
                self.token = token
            else:
                self.token = generate_jwt(private_key_path, self.thing_id, HTTP_URI, HTTP_URI)

            # Loads all thing's details
            success = self.read()
            if success:
                self.http_connected = True
                self.logger.info("HTTP connection successful")
                # Start the MQTT connection
                self.thread_mqtt = Thread(target=self.init_mqtt)
                self.thread_mqtt.start()

    def set_log_level(self, log_level):
        if log_level == 'INFO': logging.basicConfig(level=logging.INFO)
        elif log_level == 'ERROR': logging.basicConfig(level=logging.ERROR)
        elif log_level == 'WARNING': logging.basicConfig(level=logging.WARNING)
        elif log_level == 'DEBUG': logging.basicConfig(level=logging.DEBUG)
        else: logging.error('Unknown log level ' + log_level)

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
        if self.properties is not None and len(self.properties)>0:
            for index, prop in self.properties.items():
                t["properties"].append(prop.to_json())

        if self.createdAt is not None:
            t["createdAt"] = self.createdAt
        if self.updatedAt is not None:
            t["updatedAt"] = self.updatedAt
        return t

    def read(self):
        uri = self.http_uri + "/things/" + self.thing_id
        headers = {'Authorization': 'bearer ' + self.token}
        json_thing = requests.get(uri, headers=headers,
                                   verify=verifyCert).json()
        if json_thing is not None:
            if "message" in json_thing:
                self.logger.error(json_thing)
            else:
                self.name = json_thing["name"]
                self.description = json_thing["description"]
                self.thing_type = json_thing["type"]

                self.createdAt = json_thing["createdAt"]
                self.updatedAt = json_thing["updatedAt"]

                self.properties = {}

                for json_property in json_thing["properties"]:
                    prop = Property(json_property=json_property)
                    prop.belongs_to(self)
                    self.properties[prop.property_id] = prop
                return True
        return False

    def find_property_by_name(self, property_name_to_find):
        if self.properties is not None and len(self.properties)>0:
            for index, prop in self.properties.items():
                if prop.name == property_name_to_find:
                    return prop
        self.logger.debug("Property " + property_name_to_find + " was not found.")

    def create_property(self, name, typeId):
        my_property = Property(name=name,
                               typeId=typeId)
        headers = {'Authorization': 'bearer ' + self.token}
        uri = self.http_uri + "/things/" + self.thing_id + "/properties"
        response = requests.post(uri, headers=headers, verify=verifyCert,
                                 json=my_property.to_json())
        if "message" in response.json():
            self.logger.error(response.json())
            return None
        else:
            created_property = Property(json_property=response.json())
            created_property.belongs_to(self)
            self.properties[created_property.property_id] = created_property
            return created_property

    def update_property(self, prop, file_name=None):
        if file_name is None and self.mqtt_connected:
            topic = "/things/" + self.thing_id\
                    + "/properties/" + prop.property_id
            self.logger.debug('Updating property ' + prop.property_id)
            self.mqtt_client.publish(topic,
                                     json.dumps(prop.value_to_json()))
        else:
            self.update_property_http(prop, file_name=file_name)

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
                prop.property_type = json_result['property']['type']
                prop.dimensions = json_result['property']['dimensions']
                prop.values = json_result['property']['values']
                return prop
            raise ValueError(
                "read_property() - unknown response: " + json_result)
        raise ValueError("Property id '" + property_id+ "' not part of Thing '"
                         + self.thing_id
                         + "'. Did you call read_thing() first?")

    def create_classes(self, prop, classes):
        classes_json = []
        for clazz in classes:
            classes_json.append({'name':clazz})

        json_to_send = {"classes": classes_json}
        headers = {'Authorization': 'bearer ' + self.token}
        uri = self.http_uri + "/things/" + self.thing_id + "/properties/"\
              + prop.property_id + "/classes"
        response = requests.post(uri, headers=headers, verify=verifyCert,
                                 json=json_to_send)
        prop.classes = classes_json

    """-------------------------------------------------------------------------
        Search for a property in thing by name,
        create it if not found & return it
    -------------------------------------------------------------------------"""
    def find_or_create_property(self, property_name, typeId):

        if self.find_property_by_name(property_name) is None: #  property not found
            self.create_property(name=property_name,
                                 typeId=typeId)

        return self.find_property_by_name(property_name)

    """-------------------------------------------------------------------------
        Recording video function, will find or create video property in current 
        thing, with default property name "WebCam", and thing  credentials in
        ThingCredentials class wrapper
    -------------------------------------------------------------------------"""
    def start_video_recording(self,
                              property_name='WebCam',
                              port='/dev/video0',
                              segment_size='30'):

        #  Finding or creating our video property
        video_property = self.find_or_create_property(property_name, 'VIDEO')

        self.video_recorder = VideoRecorder(video_property, port, segment_size)
        self.logger.info('Start video recording on property '
                         + video_property.property_id)

        self.video_recorder.start_recording()

    def stop_video_recording(self):
        if self.video_recorder is not None:
            self.video_recorder.stop_recording()

    """-------------------------------------------------------------------------
        Uploads file to the property given filename, data(list of values
        for the property that will receive it)  an authentification class auth, 
        which contains the thing ID and token, and url (by default gets 
        reconstructed automatically)

        FOR VIDEO:
        data dictionary  must have following pairs  start_ts & duration defined
        like so : {'start_ts': ... , 'duration': ...}
    -------------------------------------------------------------------------"""
    def update_property_http(self, prop, file_name=None): 
        files=None

        if file_name is not None:
            self.logger.debug('Uploading ' + file_name
                              + ' to property ' + self.name)
            if file_name.endswith('.mp4'):
                #  Uploading file of type video in files,
                #  we create a dictionary that maps 'video' to a tuple
                #  (read only list) composed of extra data : name, file object
                #  type of video (mp4 by default),
                #  and expiration tag (also a dict)(?)
                files = {'data': ( file_name, open('./' + file_name, 'rb'),
                                    'video/mp4' , {'Expires': '0'} ) }
            else:
                self.logger.error('File type not yet supported,'
                                  + 'cancelling property update over HTTP')
                return -1

        headers = {
            'Authorization': 'bearer ' + self.token
        }
        jsonValues = {
            "values": prop.values
        }

        url = self.http_uri + '/things/' + self.thing_id + '/properties/' + prop.property_id

        self.logger.debug(prop.to_json())
        #  sending our post method to upload this file, using our authentication
        #  data dict is converted into a list for all the values of the property
        response = requests.put(url=url, files=files, json=jsonValues, headers=headers)

        self.logger.debug(response.status_code)
        #  method, by the requests library
        return response.status_code

    def init_mqtt(self):
        self.logger.info(
            'Initialising MQTT connection for Thing \'' + self.thing_id + '\'')

        self.mqtt_client = mqtt.Client()
        global mqtt_client
        mqtt_client = self.mqtt_client
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message


        # self.mqtt_client.on_subscribe = self.on_mqtt_subscribe
        # mqtt.on_publish = on_publish
        # mqtt.on_disconnect = on_disconnect
        # mqtt.on_log = on_log

        check_digi_cert_ca()
        self.mqtt_client.tls_set(
            "DigiCertCA.crt", cert_reqs=ssl.CERT_NONE,
            tls_version=ssl.PROTOCOL_TLSv1_2)

        self.mqtt_client.tls_insecure_set(True)
        self.mqtt_client.username_pw_set(username=self.thing_id,
                                         password=self.token)
        self.mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)

        # Blocking call that processes network traffic, dispatches callbacks and 
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded
        # interface and a manual interface.
        self.mqtt_client.loop_forever()

    """
        The callback for when the client receives
        a CONNACK response from the server.
    """
    def on_mqtt_connect(self, client, userdata, flags, rc):
        self.logger.info(mqtt_result_code(rc))

        self.mqtt_connected = True

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.

        # self.mqtt_client.subscribe([("/things/" + self.thing_id + "/#",1)])
        self.mqtt_client.subscribe([("/things/" + self.thing_id + "/logs", 1)])

    """
        The callback for when a PUBLISH message is received from the server.
    """
    def on_mqtt_message(self, client, userdata, msg):
        if msg.topic.endswith("/logs"):
            jsonMsg = json.loads(msg.payload)
            if jsonMsg['level'] == 'error':
                self.logger.error("[mqtt-log] " + str(jsonMsg))
            elif jsonMsg['level'] == 'info':
                self.logger.info("[mqtt-log] " + str(jsonMsg))
            elif jsonMsg['level'] == 'debug':
                self.logger.debug("[mqtt-log] " + str(jsonMsg))
            
        else:
            self.logger.info("[mqtt-log] " + msg.topic + ": " + msg.payload.toString())
