from pymongo import MongoClient

from app.core.config import get_settings

settings = get_settings()
client = MongoClient(settings.mongo_database_url)
mongo_db = client[settings.mongo_database_name]


def get_mongo_db():
    return mongo_db
