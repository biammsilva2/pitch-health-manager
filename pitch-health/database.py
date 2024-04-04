from os import getenv

from pymongo import MongoClient


client = MongoClient(
    host=getenv('MONGO_HOST'),
    port=int(getenv('MONGO_PORT')),
    username=getenv('MONGO_USER'),
    password=getenv('MONGO_PASS'),
    authSource='admin'
)

db = client['pitches']
