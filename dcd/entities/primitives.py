from enum import Enum

"""----------------------------------------------------------------------------
    Class that contains all possible property types for a property in a thing
----------------------------------------------------------------------------"""
class PropertyType(Enum):
    ONE_DIMENSION = "1D"
    TWO_DIMENSIONS = "2D"
    THREE_DIMENSIONS = "3D"
    FOUR_DIMENSIONS = "4D"
    FIVE_DIMENSIONS = "5D"
    SIX_DIMENSIONS = "6D"
    SEVEN_DIMENSIONS = "7D"
    EIGHT_DIMENSIONS = "8D"
    NINE_DIMENSIONS = "9D"
    TEN_DIMENSIONS = "10D"
    ELEVEN_DIMENSIONS = "11D"
    TWELVE_DIMENSIONS = "12D"
    ACCELEROMETER = "ACCELEROMETER"
    VIDEO = "VIDEO"
    CLASS = "CLASS"


"""----------------------------------------------------------------------------
    Convenience class, packs id and token of a thing in standard format
----------------------------------------------------------------------------"""
class ThingCredentials:

    #  constructor
    def __init__(self, THING_ID, THING_TOKEN):
        self.THING_TOKEN = THING_TOKEN
        self.THING_ID = THING_ID