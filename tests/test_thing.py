from dcd.entities.thing import Thing
from dcd.services.things import ThingService

import unittest

dcdhub_uri = "http://10.0.1.16:4478/api"
token = ""

class ThingTest(unittest.TestCase):

    def test_instance_thing(self):
        t = Thing(name="test",
                  description="a test desc",
                  thing_type="ACCELEROMETER")
        self.assertEqual(t.name, "test")
        self.assertEqual(t.description, "testtest")
        print(t.to_json())

    def test_create_thing(self):
        test_thing = Thing(name="test",
                           description="a test desc",
                           thing_type="ACCELEROMETER")
        things = ThingService(dcdhub_uri, token)
        result = things.create(test_thing)
        print(result["thingId"])


if __name__ == '__main__':
    unittest.main()
