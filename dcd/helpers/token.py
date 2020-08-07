

import datetime

from jwt import (
    JWT,
    jwk_from_dict,
    jwk_from_pem,
)

def generate_jwt(private_key_path, sub, issuer, audience):
    # Read private key from file
    with open(private_key_path, 'rb') as fh:
        signing_key = jwk_from_pem(fh.read())
    # Get current time
    current_time = datetime.datetime.utcnow().timestamp()
    # Build token message
    message = {
        'iss': issuer,
        'aud': audience,
        'sub': sub,
        'iat': int(current_time),
        'exp': int(current_time + 36000)
    }
    return JWT().encode(message, signing_key, 'RS256')


def read_jwt(public_key_path, jwt):
    with open('public.pem', 'rb') as fh:
        verifying_key = jwk_from_pem(fh.read())
    return JWT().decode(jwt, verifying_key)