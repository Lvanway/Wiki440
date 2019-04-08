import os
import json


class ContactManager(object):
    def __init__(self, path):
        self.file = os.path.join(path, './user/contacts.json')

    def read(self):
        if not os.path.exists(self.file):
            return {}
        with open(self.file) as f:
            data = json.loads(f.read())
        return data

    def write(self, data):
        with open(self.file, 'w') as f:
            f.write(json.dumps(data, indent=2))

    def add_contact(self, first_name, last_name, email):
        with open('./user/contacts.json', '+r') as json_file:
            contacts = json.load(json_file)
        contact = Contact(first_name, last_name, email)
        contacts[str(contact.last_name)] = {
            "first_name": str(contact.first_name),
            "last_name": str(contact.last_name),
            "email": str(contact.email)
        }
        with open('./user/contacts.json', 'w') as json_file:
            json_file.seek(0)
            json_file.truncate(0)
            json.dump(contacts, json_file, indent=4, separators=[',', ': '])

        return Contact(first_name, last_name, email)


class Contact(object):
    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def get(self, option):
        return self.email.get(option)