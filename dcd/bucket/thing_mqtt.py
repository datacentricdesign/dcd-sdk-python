import requests
import logging
from threading import Thread
import sys
import os
import signal
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import ssl
import random
import json
from dcd.bucket.properties.property import Property


mqtt_client = None

def keyboardInterruptHandler(signal, frame):
    logging.info("[mqtt] Disconnecting...")
    global mqtt_client
    if (mqtt_client is not None):
        mqtt_client.disconnect()
    try:
        sys.exit(0)
    except:
        logging.info("[mqtt] Program closed with CTRL+C")
        os._exit(0)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

load_dotenv()
MQTT_HOST = os.getenv("MQTT_HOST", "dwd.tudelft.nl")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_SECURED = os.getenv("MQTT_SECURED", "True") == "True"

class ThingMQTT:

    def __init__(self, thing):
        """Create the MQTT link between the Thing and its digital twin on Bucket

        Args:
            thing : Thing
                The Thing to connect to Bucket via MQTT
        """
        self.thing = thing
        self.logger = thing.logger

        self.mqtt_client = None
        self.connected = False 
        
        self.thread_mqtt = Thread(target=self.init)
        self.thread_mqtt.start()       

    def is_connected(self):
        return self.connected

    def init(self):
        self.logger.debug("[mqtt] Initialising connection.")

        self.mqtt_client = mqtt.Client()
        global mqtt_client
        mqtt_client = self.mqtt_client
        self.mqtt_client.on_connect = self.__on_mqtt_connect
        self.mqtt_client.on_message = self.__on_mqtt_message

        # self.mqtt_client.on_subscribe = self.on_mqtt_subscribe
        # mqtt.on_publish = on_publish
        # mqtt.on_disconnect = on_disconnect
        # mqtt.on_log = on_log

        if (MQTT_SECURED):
            check_digi_cert_ca()
            self.mqtt_client.tls_set(
                "DigiCertCA.crt", cert_reqs=ssl.CERT_NONE,
                tls_version=ssl.PROTOCOL_TLSv1_2)

            self.mqtt_client.tls_insecure_set(True)

        self.mqtt_client.username_pw_set(username=self.thing.thing_id,
                                         password=self.thing.token.get_token())
        self.mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded
        # interface and a manual interface.
        self.mqtt_client.loop_forever()

    def read(self):
        if self.mqtt_connected:
            topic = "/things/" + self.thing.thing_id + "/read"
            requestId = random.randint(0, 100)
            self.logger.debug(
                "[mqtt] Reading thing, response will come via /reply (request id: " + str(requestId) + ")")
            self.mqtt_client.publish(
                topic, json.dumps({"requestId": requestId}))

    def create_property(self, name: str, type_id: str):
        my_property = Property(name=name, type_id=type_id)
        if self.mqtt_connected:
            topic = "/things/" + self.thing.thing_id + "/properties/create"
            requestId = random.randint(0, 100)
            self.logger.debug(
                "[mqtt] Creating a property, response will come via /reply (request id: " + str(requestId) + ")")
            self.mqtt_client.publish(topic, json.dumps(
                {"property": my_property, "requestId": requestId}))

    def find_or_create_property(self, property_name: str, type_id: str):
        """Search for a property in thing by name, create it if not found & return it.

        Args:
            property_name : str
                The name of the property to look for.
            type_id : str
                The type of the property, so that we can create it if it is not found.
        """
        # property not found
        if self.thing.find_property_by_name(property_name) is None:
            self.create_property(name=property_name, type_id=type_id)

    def update_property(self, prop: Property, file_name: str):
        """Send new property values to Bucket

        Args:
            prop : Property
                The property containing values to send
            file_name : str, optional
                If media type property, the path to the file to upload. Defaults to None.
        """
        requestId = random.randint(0, 100)
        topic = "/things/" + self.thing.thing_id + "/properties/" + prop.property_id + "/update"
        self.logger.debug("[mqtt] Updating property " + prop.property_id + "...")
        self.__publish(topic, json.dumps(
            {"requestId": requestId, "property": prop.value_to_json()}))

    def __publish(self, topic: str, payload: str):
        self.mqtt_client.publish(topic, payload)

    def __on_mqtt_connect(self, client, userdata, flags, rc):
        """
        The callback for when the client receives
        a CONNACK response from the server.
        """
        self.logger.info("[mqtt] " + mqtt_result_code(rc))

        self.mqtt_connected = True

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.

        # self.mqtt_client.subscribe([("/things/" + self.thing_id + "/#",1)])
        self.mqtt_client.subscribe(
            [("/things/" + self.thing.thing_id + "/log", 1), ("/things/" + self.thing.thing_id + "/reply", 1)])

    def __on_mqtt_message(self, client, userdata, msg):
        """
        The callback for when a PUBLISH message is received from the server.
        """
        if msg.topic.endswith("/log"):
            jsonMsg = json.loads(msg.payload)
            if jsonMsg["level"] == "error":
                self.logger.error("[mqtt-bucket] " + str(jsonMsg))
            elif jsonMsg["level"] == "info":
                self.logger.info("[mqtt-bucket] " + str(jsonMsg))
            elif jsonMsg["level"] == "debug":
                self.logger.debug("[mqtt-bucket] " + str(jsonMsg))

        elif msg.topic.endswith("/reply"):
            jsonMsg = json.loads(msg.payload)
            self.logger.debug(
                "[mqtt] Received response on /reply (request id: " + str(jsonMsg["requestId"]) + ")")
            if jsonMsg["thing"] is not None:
                self.logger.debug(
                    "Loading thing details received from Bucket...")
                self.thing.from_json(jsonMsg["thing"])
                self.logger.debug(json.dumps(self.thing.to_json()))
            elif jsonMsg["property"] is not None:
                self.logger.debug("Adding new property " +
                                  jsonMsg["property"].id + "...")
                created_property = Property(json_property=jsonMsg["property"])
                created_property.belongs_to(self)
                self.thing.properties[created_property.property_id] = created_property
                return created_property

        else:
            self.logger.info("[mqtt] " + msg.topic +
                             ": " + msg.payload.toString())


def mqtt_result_code(rc):
    switcher = {
        0: "MQTT connection successful",
        1: "MQTT Connection refused - incorrect protocol version",
        2: "MQTT Connection refused - invalid client identifier",
        3: "MQTT Connection refused - server unavailable",
        4: "MQTT Connection refused - bad username or password",
        5: "MQTT Connection refused - not authorised"
    }
    return switcher.get(rc, "Unknown result code: " + str(rc))


def check_digi_cert_ca():
    try:
        f = open("DigiCertCA.crt")
        logging.debug("DigiCertCA.crt exist.")
        f.close()
    except IOError:
        logging.debug("DigiCertCA.crt missing, downloading...")
        # Send HTTP GET request to github to fetch the certificate
        response = requests.get("https://raw.githubusercontent.com/datacentricdesign/dcd-hub/develop/certs/DigiCertCA.crt")
        # If the HTTP GET request can be served
        if response.status_code == 200:
            # Write the file contents in the response to a file specified by
            # local_file_path
            with open("DigiCertCA.crt", "wb") as local_file:
                for chunk in response.iter_content(chunk_size=128):
                    local_file.write(chunk)
            logging.debug("DigiCertCA.crt downloaded.")
        else:
            logging.warn("DigiCertCA not found.")
