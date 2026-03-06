from pymongo import MongoClient

from core.db.config import get_mongo_settings


_client = None


def get_mongo_client():
    global _client
    if _client is None:
        settings = get_mongo_settings()
        _client = MongoClient(settings["uri"])
    return _client


def get_mongo_database():
    settings = get_mongo_settings()
    return get_mongo_client()[settings["db"]]
