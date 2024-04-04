from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# MongoDB connection URL
MONGO_URL = "mongodb://mongo:27017"
client = AsyncIOMotorClient(MONGO_URL)
database = client["mydatabase"]
collection = database["pitches"]
