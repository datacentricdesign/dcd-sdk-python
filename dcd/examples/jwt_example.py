import json
import datetime
import requests

from jwt import (
    JWT,
    jwk_from_dict,
    jwk_from_pem,
)

verifyCert = True

current_time = datetime.datetime.utcnow().timestamp()

message = {
    'iss': 'https://dwd.tudelft.nl:443/api',
    'aud': 'https://dwd.tudelft.nl:443/api',
    'sub': 'dcd:things:my-test-thing-365a',
    'iat': int(current_time),
    'exp': int(current_time + 36000)
}

with open('private.pem', 'rb') as fh:
    signing_key = jwk_from_pem(fh.read())

# print(signing_key.to_dict())

# body = {"pem": json.dumps(signing_key.to_dict())}
# #
# uri = "https://dwd.tudelft.nl:443/api/things/dcd:things:test-8a42/pem";
# headers = {'Authorization': 'bearer 1dycpEr4jARHdu5U0OJYmdewvMIekwdte1Wr0Vdb_P8.IQ4NA5Nwrwg6Q5ZCWP0yUWfRoZziQQa-wNizs9qXptc' }
# json_result = requests.put(uri, headers=headers,
#                            json=body, verify=verifyCert).json()

jwt = JWT()
compact_jws = jwt.encode(message, signing_key, 'RS256')

# print(compact_jws)

with open('public.pem', 'rb') as fh:
    verifying_key = jwk_from_pem(fh.read())

print(verifying_key.to_dict())

message_received = jwt.decode(compact_jws, verifying_key)

assert message == message_received

# print(message_received)
