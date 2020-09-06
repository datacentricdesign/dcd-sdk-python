
from dcd.bucket.properties.property import Property
import requests

verifyCert = True

class ThingHTTP:


    def __init__(self, logger, thing, http_uri):
        self.logger = logger
        self.thing = thing
        self.http_uri = http_uri

        self.connected = False
        self.http_uri = http_uri

        success = self.read()
        if (success):
            self.connected = True
            self.logger.info("HTTP connection successful")

    def is_connected(self):
        return self.connected

    def read_property(self, property_id, from_ts=None, to_ts=None):
        prop = self.thing.properties[property_id]
        if prop is not None:
            uri = self.http_uri + "/things/" + self.thing.thing_id
            uri += "/properties/" + property_id
            if from_ts is not None and to_ts is not None:
                uri += "?from=" + str(from_ts) + "&to=" + str(to_ts)
            headers = {'Authorization': 'bearer ' + self.thing.token.get_token()}
            json_result = requests.get(uri, headers=headers, verify=verifyCert).json()

            if json_result["property"] is not None:
                prop.name = json_result['property']['name']
                prop.description = json_result['property']['description']
                prop.property_type = json_result['property']['type']
                prop.dimensions = json_result['property']['dimensions']
                prop.values = json_result['property']['values']
                return prop
            raise ValueError(
                "read_property() - unknown response: " + json_result)
        raise ValueError("Property id '" + property_id + "' not part of Thing '"
                         + self.thing.thing_id
                         + "'. Did you call read_thing() first?")

    def update_property(self, prop, file_name=None):
        """
        Uploads file to the property given filename, data(list of values
        for the property that will receive it)  an authentification class auth, 
        which contains the thing ID and token, and url (by default gets 
        reconstructed automatically)

        FOR VIDEO:
        data dictionary  must have following pairs  start_ts & duration defined
        like so : {'start_ts': ... , 'duration': ...}
        """
        files = None

        if file_name is not None:
            self.logger.debug('Uploading ' + file_name
                              + ' to property ' + self.thing.name)
            if file_name.endswith('.mp4'):
                #  Uploading file of type video in files,
                #  we create a dictionary that maps 'video' to a tuple
                #  (read only list) composed of extra data : name, file object
                #  type of video (mp4 by default),
                #  and expiration tag (also a dict)(?)
                files = {'data': (file_name, open('./' + file_name, 'rb'),
                                  'video/mp4', {'Expires': '0'})}
            else:
                self.logger.error('File type not yet supported,'
                                  + 'cancelling property update over HTTP')
                return -1

        headers = {
            'Authorization': 'bearer ' + self.thing.token.get_token()
        }
        jsonValues = {
            "values": prop.values
        }

        url = self.http_uri + '/things/' + self.thing.thing_id + \
            '/properties/' + prop.property_id

        self.logger.debug(prop.to_json())
        #  sending our post method to upload this file, using our authentication
        #  data dict is converted into a list for all the values of the property
        response = requests.put(url=url, files=files,
                                json=jsonValues, headers=headers)

        self.logger.debug(response.status_code)
        #  method, by the requests library
        return response.status_code

    def read(self):
        uri = self.http_uri + "/things/" + self.thing.thing_id
        headers = {'Authorization': 'bearer ' + self.thing.token.get_token()}
        json_thing = requests.get(uri, headers=headers,
                                  verify=verifyCert).json()
        return self.thing.from_json(json_thing)

    def create_property(self, name, typeId):
        my_property = Property(name=name,
                               typeId=typeId)
        headers = {'Authorization': 'bearer ' + self.thing.token.get_token()}
        uri = self.http_uri + "/things/" + self.thing.thing_id + "/properties"
        response = requests.post(uri, headers=headers, verify=verifyCert,
                                 json=my_property.to_json())
        if "message" in response.json():
            self.logger.error(response.json())
            return None
        else:
            created_property = Property(json_property=response.json())
            created_property.belongs_to(self)
            self.thing.properties[created_property.property_id] = created_property
            return created_property