
import json
from typing import List
from .properties.property import Property
from .thing_logger import ThingLogger
import requests

verifyCert = True

class ThingHTTP:
    """Handle Bucket interaction for a Thing via HTTP"""

    def __init__(self, thing, http_uri: str):
        """Create the HTTP link between the Thing and its digital twin on Bucket

        Args:
            thing : Thing
                The Thing to connect to Bucket via HTTP
            http_uri : str
                The URI of Bucket
        """
        self.thing = thing
        self.logger = thing.logger
        self.http_uri = http_uri

        self.connected = False
        self.http_uri = http_uri

        success = self.read()
        if (success):
            self.connected = True
            self.logger.info("[http] Connection successful")

    def is_connected(self) -> bool:
        """Check whether the HTTP connection was established.

        Returns:
            bool: Whether the initial HTTP request `read()` succeeded.
        """
        return self.connected

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
        # Look first in the properties of the Thing
        prop = self.thing.get_property(property_id)
        if prop is None:
            prop = self.thing.get_shared_property(property_id)
        if prop is None:
            # Still not found, trigger an exception
            raise ValueError(
                f"Property id '{property_id}' not part of Thing '{self.thing.thing_id}' nor shared with this Thing. Did you call read_thing() first?")


        uri = f"{self.http_uri}/things/{prop.thing.id}/properties/{property_id}"

        if from_ts is not None and to_ts is not None:
            uri += "?from=" + str(from_ts) + "&to=" + str(to_ts)
            if time_interval is not None and time_fct is not None:
                uri += "&timeInterval=" + time_interval + "&fctInterval=" + time_fct
                if fill is not None:
                    uri +=  "&fill=" + fill
        json_result = requests.get(
            uri, headers=self.__get_headers(), verify=verifyCert).json()

        if "id" in json_result:
            prop.from_json(json_result)
            return prop
        raise ValueError(
            f"read_property() - unknown response: {json_result}")

    
    def read_property_media(self, property_id, dimension_id, ts):
        prop = self.thing.get_property(property_id)
        uri = f"{self.http_uri}/things/{prop.thing.id}/properties/{property_id}/dimensions/{dimension_id}/timestamp/{ts}"

        receive = requests.get(uri, headers=self.__get_headers(), verify=verifyCert)
        return receive.content


    def update_property(self, prop: Property, file_name: str = None) -> int:
        """Update the values of a property on Bucket

        Args:
            prop : Property
                The property to update
            file_name : str, optional
                The media to upload. Defaults to None.

        Returns:
            int: Status response code
        """
        files = None
        if file_name is not None:
            file_name_lc = file_name.lower()
            self.logger.debug(
                f"[http] Uploading {file_name} to property {self.thing.name}")
            if file_name_lc.endswith(".mp4"):
                files = {"video-mp4": (file_name_lc, open("./" + file_name, "rb"),
                                  "video/mp4", {"Expires": "0"})}
            if file_name_lc.endswith(".mp3"):
                files = {"audio-mp3": (file_name_lc, open("./" + file_name, "rb"),
                                  "application/octet-stream", {"Expires": "0"})}
            if file_name_lc.endswith(".jpg"):
                files = {"image-jpg": (file_name_lc, open("./" + file_name, "rb"),
                                  "image/jpeg", {"Expires": "0"})}
            if file_name_lc.endswith(".png"):
                files = {"image-png": (file_name_lc, open("./" + file_name, "rb"),
                                  "image/png", {"Expires": "0"})}
            else:
                self.logger.error("[http] File type not yet supported,"
                                  + "cancelling property update over HTTP")
                return -1

        url = self.http_uri + "/things/" + self.thing.thing_id + \
            "/properties/" + prop.property_id

        self.logger.debug("[http] " + str(prop.to_json()))
        #  sending our post method to upload this file, using our authentication
        #  data dict is converted into a list for all the values of the property
        if (files is not None):
            response = requests.put(url=url,
                                    files=files,
                                    data={'property': json.dumps(prop.to_json())},
                                    headers=self.__get_headers())
        else:
            response = requests.put(url=url,
                                    json=prop.to_json(),
                                    headers=self.__get_headers())

        self.logger.debug("[http] " + str(response.status_code))
        self.logger.debug("[http] " + str(response.text))
        #  method, by the requests library
        return response.status_code

    def read(self) -> bool:
        """Read details of the Thing from Bucket.

        Returns:
            bool: True if succeeded in reading the Thing details from Bucket
        """
        uri = f"{self.http_uri}/things/{self.thing.thing_id}"
        thing_result = requests.get(uri, headers=self.__get_headers(),
                                  verify=verifyCert)
        return self.thing.from_json(thing_result.json())

    def find_shared_properties(self, group) -> List[Property]:
        uri = f"{self.http_uri}/things/{self.thing.thing_id}/properties?sharedWith=" + group
        return requests.get(uri, headers=self.__get_headers(),
                                  verify=verifyCert).json()

    def create_property(self, name: str, type_id: str):
        """Create a new property on Bucket.

        Args:
            name : str
                Name of the property to create
            type_id : str
                Type id of the property to create

        Returns:
            Property: The newly created property
        """
        my_property = Property(name=name, type_id=type_id)
        uri = f"{self.http_uri}/things/{self.thing.thing_id}/properties"
        response = requests.post(
            uri,
            headers=self.__get_headers(),
            verify=verifyCert,
            json=my_property.to_json())
        if "message" in response.json():
            self.logger.error("[http] " + str(response.json()))
            return None
        else:
            created_property = Property(json_property=response.json())
            created_property.belongs_to(self.thing)
            self.thing.properties[created_property.property_id] = created_property
            return created_property

    def __get_headers(self):
        return {
            "Authorization": "bearer " + self.thing.token.get_token()
        }
