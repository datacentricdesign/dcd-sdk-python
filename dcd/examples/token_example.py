# Example of generating/reading a JWT token
# This is integrated in the Thing and done automatically

from dcd.bucket.thing_token import ThingToken

from dotenv import load_dotenv
import os

# The thing ID and access token
load_dotenv()
THING_ID = os.environ["THING_ID"]
HTTP_API_URI = os.getenv("HTTP_URI", "https://dwd.tudelft.nl:443/bucket/api")

token = ThingToken("private.pem", THING_ID, HTTP_API_URI, HTTP_API_URI)

jwt = token.get_token()

print(jwt)

message = token.decode("public.pem", jwt)

print(message)
