# models/license.py
from typing import Optional
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGO_URI")
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Create a new database and collection
db = client['NSC']

# Make collection called licenses
licenses_collection = db['licenses']

class License:
    def __init__(self, license_number: str, name: str, dob: datetime, photo: bytes, validity: datetime, digital_signature: str):
        self.license_number = license_number
        self.name = name
        self.dob = dob
        self.photo = photo
        self.validity = validity
        self.digital_signature = digital_signature

    def save(self):
        license_data = {
            'license_number': self.license_number,
            'name': self.name,
            'dob': self.dob,
            'photo': self.photo,
            'validity': self.validity,
            'digital_signature': self.digital_signature
        }
        licenses_collection.insert_one(license_data)

    @staticmethod
    def find_by_license_number(license_number: str) -> Optional['License']:
        license_data = licenses_collection.find_one({'license_number': license_number})
        if license_data:
            return License(
                license_number=license_data['license_number'],
                name=license_data['name'],
                dob=license_data['dob'],
                photo=license_data['photo'],
                validity=license_data['validity'],
                digital_signature=license_data['digital_signature']
            )
        return None