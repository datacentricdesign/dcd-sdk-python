

import datetime

from jwt import (
    JWT,
    jwk_from_dict,
    jwk_from_pem,
)


class ThingToken:

    def __init__(self, private_key_path, subject, issuer, audience):
        self.private_key_path = private_key_path
        self.subject = subject
        self.issuer = issuer
        self.audience = audience

    def get_token(self):
        # Get current time
        current_time = datetime.datetime.utcnow().timestamp()
        if self.exp <= current_time:
            # If token expired, refresh it
            return self.refresh()
        return self.jwt

    def refresh(self):
        # Read private key from file
        with open(self.private_key_path, 'rb') as fh:
            signing_key = jwk_from_pem(fh.read())
        # Get current time
        current_time = datetime.datetime.utcnow().timestamp()
        # Build token message
        self.iat = int(current_time)
        self.exp = int(current_time + 3600)
        message = {
            'iss': self.issuer,
            'aud': self.audience,
            'sub': self.subject,
            'iat': self.iat,
            'exp': self.exp
        }
        self.jwt = JWT().encode(message, signing_key, 'RS256')
        return self.jwt


    def read_jwt(self, public_key_path, jwt):
        with open('public.pem', 'rb') as fh:
            verifying_key = jwk_from_pem(fh.read())
        return JWT().decode(jwt, verifying_key)