# models/license.py
from typing import Optional
from datetime import datetime
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['driving_license_db']
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