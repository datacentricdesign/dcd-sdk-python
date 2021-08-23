from time import time
import os
from os.path import join
from dotenv import load_dotenv

import jwt

dotenv_path = join(os.getcwd(), '.env')
load_dotenv(dotenv_path)
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "private.pem")
PUBLIC_KEY_PATH = os.getenv("PUBLIC_KEY_PATH", "public.pem")
TOKEN_PERIOD_SECONDS = int(os.getenv("TOKEN_PERIOD_SECONDS", "3600"))


class ThingToken:
    """Handle JSON web token for the Thing authentication"""

    def __init__(self, private_key_path: str, subject: str, issuer: str, audience: str, algorithm = "RS256"):
        """Constructor

        Args:
            private_key_path (str): Path to the private key
            subject (str): The subject of the JWT (should be a thing id)
            issuer (str): The issuer should be the uri to the Bucket api
            audience (str): The audience should be the uri to the Bucket api
        """
        if private_key_path is not None:
            self.private_key_path = private_key_path
        else:
            self.private_key_path = PRIVATE_KEY_PATH
        self.subject = subject
        self.issuer = issuer
        self.audience = audience
        self.exp = None
        self.algorithm=algorithm

    def get_token(self) -> str:
        """Check if the current JWT is still valid, refresh it if necessary and returns it.

        Returns:
            str: The existing (and still valid) JWT or a newly generated JWT
        """
        # Get current time
        current_time = time()
        if self.exp is None or self.exp < current_time:
            # If token expired, refresh it
            return self.refresh()
        return self.jwt

    def refresh(self, duration_sec: int = TOKEN_PERIOD_SECONDS) -> str:
        """Use the private key to generate a new JWT.

        Args:
            duration_sec (int, optional): The life time of the token in seconds

        Returns:
            str: the resulting JSON web token
        """
        # Read private key from file
        with open(self.private_key_path, "rb") as fh:
            signing_key = fh.read()
        # Get current time
        current_time = time()
        # Build token message
        self.iat = int(current_time)
        self.exp = int(current_time + duration_sec)
        payload = {
            "iss": self.issuer,
            "aud": self.audience,
            "sub": self.subject,
            "iat": self.iat,
            "exp": self.exp
        }
        token = jwt.encode(payload, signing_key, algorithm=self.algorithm)
        if isinstance(token,bytes):
            token = token.decode('utf-8')
        self.jwt = token
        return self.jwt

    def decode(self, public_key_path: str = None, jwt_token: str = None) -> dict:
        """Decode a JWT, revealing the dictionary of its values

        Args:
            public_key_path : str, optional
                The path to the public key. If none provided, looking at PUBLIC_KEY_PATH environment variable, or use './public.pem' as default. Defaults to None.
            jwt_token : str, optional
                String representing the JSON web token. If none provided, taking the one from the class Defaults to None.

        Returns:
            dict: Decoded JSON Web Token including the issuer (iss), audience (aud),
            subject (sub), the creation date (iat) and the expiration date (exp) 
        """
        key = PUBLIC_KEY_PATH
        if public_key_path is not None:
            key = public_key_path
        with open(key, "rb") as fh:
            verifying_key = fh.read()
        if (jwt_token is not None):
            return jwt.decode(jwt_token, verifying_key, algorithms=[self.algorithm], audience=self.audience)
        else:
            return jwt.decode(self.jwt, verifying_key, algorithms=[self.algorithm], audience=self.audience)
