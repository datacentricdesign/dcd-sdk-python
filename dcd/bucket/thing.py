from typing import List
from dotenv import load_dotenv
import json
import os
from datetime import datetime

from .thing_token import ThingToken
from .thing_mqtt import ThingMQTT
from .thing_http import ThingHTTP
from .thing_logger import ThingLogger
from .properties.property import Property
from .properties.ip_address_property import IPAddressProperty

load_dotenv()
THING_ID = os.getenv("THING_ID", None)
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", None)
HTTP_API_URI = os.getenv(
    "HTTP_API_URI", "https://dwd.tudelft.nl:443/bucket/api")
TOKEN_ALGO = os.getenv(
    "TOKEN_ALGO", "RS256")

DIGI_CERT_CA = os.getenv("DIGI_CERT_CA", "DigiCertCA.crt")

class Thing:
    """
    This is a conceptual class representation of a physical or virtual entity collecting data.

    Attributes:
        thing_id : str
            The id of the Thing, starting with "dcd:things:".
        name : str
            Name of the Thing
        description : str
            Description of the Thing
        thing_type : str
            Type of the Thing
        properties : Property[]
            Properties of the Thing
        private_key_path : str
            Path to the private key to use for the generation of authentication tokens.

        created_at : int
            Creation time of the Thing on Bucket (UNIX timestamp)
        updated_at : int
            Last update time of the Thing on Bucket (UNIX timestamp)
    """

    def __init__(self,
                 thing_id: str = None,
                 private_key_path: str = None,
                 private_key: str = None,
                 json_thing: dict = None,
                 connect = True):
        """
        Constructs a Thing, generating an JSON Web token, attempting a connection via HTTP to read the Thing deails from Bucket, connecting to MQTT

        Args:
            thing_id : str, optional
                The id of the Thing, starting with "dcd:things:". Looks for a THING_ID environment variable if None. Defaults to None.
            private_key_path : str, optional
                Path to the private key to use for the generation of authentication tokens. The associated public key must be registered on Bucket. Defaults to "private.pem".
            json_thing : dict, optional
                Provision thing details from a JSON object. Defaults to None.
        """

        self.properties = []
        self.shared_properties = []
        self.video_recorder = None
        if json_thing is not None:
            self.from_json(json_thing)
        else:
            self.thing_id = thing_id

            # If the thing_id was not provided, try to load it from the environment variables
            if self.thing_id is None:
                self.thing_id = THING_ID

            self.name = None
            self.description = None
            self.thing_type = None
            self.private_key_path = private_key_path

            # If the private_key_path was not provided, try to load it from the environment variables
            if self.private_key_path is None:
                if PRIVATE_KEY_PATH is not None:
                    self.private_key_path = PRIVATE_KEY_PATH
                else:
                    self.private_key_path = "private.pem"

            self.created_at = None
            self.updated_at = None

            self.logger = ThingLogger(self)

            # If there is a thing id, try to connect
            if self.thing_id is not None:
                self.token = ThingToken(
                    private_key_path, self.thing_id, HTTP_API_URI, HTTP_API_URI, algorithm=TOKEN_ALGO)
                self.http = ThingHTTP(self, HTTP_API_URI)

                # Loads all thing's details
                if self.http.is_connected():
                    if (connect):
                        self.ip_address_property = IPAddressProperty(self.logger, self)
                    # Init the MQTT
                    self.mqtt = ThingMQTT(self, connect=connect)

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
            for prop in self.properties.items():
                t["properties"].append(prop[1].to_json())

        if self.created_at is not None:
            t["createdAt"] = self.created_at
        if self.updated_at is not None:
            t["updatedAt"] = self.updated_at
        return t

    def from_json(self, json_thing: dict) -> bool:
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

                if "properties" in json_thing:
                    for json_property in json_thing["properties"]:
                        prop = Property(json_property=json_property)
                        prop.belongs_to(self)
                        self.properties[prop.property_id] = prop
                return True
        return False

    def get_property(self, property_id):
        for property in self.properties:
            if self.properties[property].property_id == property_id:
                return self.properties[property]
        return None
    
    def get_shared_property(self, property_id):
        for property in self.shared_properties:
            if property.property_id == property_id:
                return property
        return None
        
    def find_property_by_name(self, property_name_to_find: str) -> Property:
        """Search for a property in thing by name

        Args:
            property_name_to_find : str
                The name of the property to look for.

        Returns:
            Property: The found property, None if not found
        """
        if self.properties is not None and len(self.properties) > 0:
            for prop in self.properties.items():
                if prop[1].name == property_name_to_find:
                    return prop[1]
        self.logger.debug(
            "Property " + property_name_to_find + " was not found.")
        return None

    def find_shared_properties(self, group = "*") -> List[Property]:
        """Search for properties that are accessible by the Thing.

        Args:
            group (str, optional): [description]. Defaults to "*", fetching for all groups.

        Returns:
            [Property]: Shared properties accessible by the Thing.
        """
        json_properties = self.http.find_shared_properties(group)
        properties = []
        if "status" not in json_properties:
            for json_prop in json_properties:
                prop = Property(json_property=json_prop)
                prop.belongs_to(Thing(json_thing=json_prop["thing"]))
                properties.append(prop)
            self.shared_properties = properties
        return properties

    def find_or_create_property(self, property_name: str, type_id: str) -> Property:
        """Search for a property in thing by name, create it if not found & return it.

        Args:
            property_name : str
                The name of the property to look for.
            type_id : str
                The type of the property, so that we can create it if it is not found.

        Returns:
            Property: The found or newly created Property.
        """
        # property not found
        if self.find_property_by_name(property_name) is None:
            self.http.create_property(name=property_name,
                                      type_id=type_id)
        return self.find_property_by_name(property_name)

    def update_property(self, prop: Property, file_name: str = None):
        """Send new property values to Bucket

        Args:
            prop : Property
                The property containing values to send
            file_name : str, optional
                If media type property, the path to the file to upload. Defaults to None.
        """
        self.logger.data(prop)
        if file_name is None and self.mqtt.is_connected():
            self.mqtt.update_property(prop, file_name=file_name)
        else:
            self.http.update_property(prop, file_name=file_name)

    def read_property(self, property_id: str, from_ts: int = None, to_ts: int = None, time_interval = None, time_fct = None, fill = None) -> Property:
        """Read the details of a property from Bucket

        Args:
            property_id : str
                The id of the property to read
            from_ts : int, optional
                The start time of the values to fetch. Defaults to None.
            to_ts : int, optional
                The end time of the values to fetch. Defaults to None.

        Raises:
            ValueError: The requested property is not part of the Thing
            ValueError: Could not parse the reponse

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
        return self.http.read_property(property_id, from_ts, to_ts, time_interval, time_fct, fill)

    def describe(self):
        """
        Prints formatted JSON with the details of the Thing
        """
        print(json.dumps(self.to_json(), indent=4, sort_keys=True))