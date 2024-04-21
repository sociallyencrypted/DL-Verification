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

# Drop the collection
licenses_collection.drop()

# Close the connection
client.close()