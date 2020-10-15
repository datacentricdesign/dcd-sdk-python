# This example shows how to subscribe to and handle
# value updates from shared properties.
from random import random
import time
import json

import sys

from dcd.bucket.thing import Thing

def main():
    # Instantiate a thing with its credential
    # By default, looking into .env for THING_ID and PRIVATE_KEY_PATH (default "./private.pem")
    my_thing = Thing()

    # Instead you code put your credentials in the code (not recommended)
    # my_thing = Thing(thing_id="dcd:things:...", private_key_path="path/to/private.pem")

    # If we fail to connect to the Thing, we leave the program
    if not my_thing.http.is_connected:
        sys.exit()

def subscribe_to_other_ightbulbs():
    """Search for all properties shared with our Thing and subscribe to MQTT messages from those of type LIGHTBULB_STATUS
    """
    # search for shared properties, leave empty for all
    # add "dcd:group:..." to target shared properties within a specific group.
    shared_properties = my_thing.find_shared_properties()
    # Show a message if we did no find any shared properties
    if len(shared_properties) == 0:
        print("No shared property found.")
    # Select only the properties of type LIGHTBULB_STATUS and not from our Thing
    for prop in shared_properties:
        if prop.type_id == "LIGHTBULB_STATUS" and my_thing.thing_id != prop.thing.id:
            # Prepare the MQTT topic to subscribe
            topic = "/things/" + prop.thing.id + "/properties/" + prop.property_id
            # Set the handler on this topic
            my_thing.mqtt.mqtt_client.message_callback_add(topic, other_lightbulb_handler)
            # Subscribe to the topic
            my_thing.mqtt.mqtt_client.subscribe([(topic, 1)])

def other_lightbulb_handler(client, userdata, msg):
    """Handle events from other lightbulbs

    Args:
        client: the MQTT client instance for this callback
        userdata: the private user data
        msg (MQTTMessage): an instance of MQTTMessage.
    """
    print("Event from an other lightbulb!")
    print("Topic: " + msg.topic)
    jsonMsg = json.loads(msg.payload)
    print("JSON message: " +str(jsonMsg))

if __name__ == "__main__":
    main()