from os import getenv, environ

from pymongo import MongoClient


client = MongoClient(
    host=getenv('MONGO_HOST'),
    port=int(environ.get('MONGO_PORT', 0)),
    username=getenv('MONGO_USER'),
    password=getenv('MONGO_PASS'),
    authSource='admin'
)

db = client['pitches']
