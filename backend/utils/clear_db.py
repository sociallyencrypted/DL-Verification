from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json

with open('keys/MongoKeys.json') as f:
    data = json.load(f)
    UserName = data['UserName']
    PSWD = data['PSWD']

uri = f"mongodb+srv://{UserName}:{PSWD}@nsc.8wuh4uj.mongodb.net/?retryWrites=true&w=majority&appName=NSC"
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