import os
from pymongo import MongoClient
from models.event import Event, EventAction

_collection = None


def init_db():

    global _collection
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    _collection = client["github_webhooks"]["github_events"]
    return _collection


def _get_collection():
    if _collection is None:
        init_db()
    return _collection


def upsert_webhook_event(event: Event) -> None:
    col = _get_collection()
    col.update_one(
        {"request_id": event.request_id},
        {"$set": event.to_dict()},
        upsert=True,
    )


def find_all_events() -> list[dict]:
    col = _get_collection()
    return list(col.find({}, {"_id": 0}).sort("timestamp", -1))


def find_events_paginated(page: int = 1, per_page: int = 10) -> list[dict]:
    col = _get_collection()
    skip = (page - 1) * per_page
    return list(
        col.find({}, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(per_page)
    )


def count_events() -> int:
    col = _get_collection()
    return col.count_documents({})


def find_events_by_action(action: EventAction) -> list[dict]:
    col = _get_collection()
    return list(
        col.find({"action": action.value}, {"_id": 0}).sort("timestamp", -1)
    )
