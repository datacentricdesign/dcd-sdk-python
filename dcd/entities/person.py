import json


class Person:
    """"A DCD 'Person' represents a physical person."""

    def __init__(self,
                 person_id=None,
                 name=None,
                 password=None,
                 properties=(),
                 json_person=None):

        if json_person is not None:
            self.person_id = json_person.id
            self.name = json_person.name
            self.password = json_person.password
            self.properties = json_person.properties
        else:
            self.person_id = person_id
            self.name = name
            self.password = password
            self.properties = properties

    def to_json(self):
        p = {}
        if self.person_id is not None:
            p.id = self.person_id
        if self.name is not None:
            p["name"] = self.name
        if self.password is not None:
            p["password"] = self.password
        if self.properties is not None and len(self.properties) > 0:
            p["properties"] = self.properties
        return p
