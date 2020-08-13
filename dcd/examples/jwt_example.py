# Example of generating/reading a JWT token
# This is integrated in the Thing and done automatically

from dcd.helpers.token import generate_jwt
from dcd.helpers.token import read_jwt

from dotenv import load_dotenv
import os

# The thing ID and access token
load_dotenv()
THING_ID = os.environ['THING_ID']

API_URL='https://dwd.tudelft.nl:443/bucket/api'

jwt = generate_jwt('private.pem', THING_ID, API_URL, API_URL)

print(jwt)

message = read_jwt('public.pem', jwt)

print(message)
