from context import dcd
from dcd.entities.person import Person
from dcd.services.persons import PersonService

import unittest


class PersonTest(unittest.TestCase):

    def test_instance_person(self):
        p = Person(name="test", password="testtest")
        self.assertEqual(p.name, "test")
        self.assertEqual(p.password, "testtest")
        print(p.to_json())

    def test_create_person(self):
        test_person = Person(name="test", password="testtest")
        persons = PersonService("http://10.0.1.16:4478/api")
        result = persons.create(test_person)
        print(result["personId"])


if __name__ == '__main__':
    unittest.main()
