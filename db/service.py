"""
Database service — handles all MongoDB operations.

Controllers and handlers only consume these functions;
they never touch the database directly.
"""

import os
from pymongo import MongoClient
from models.event import Event, EventAction

# ── module-level state (initialised once via init_db) ─────────────────
_collection = None


def init_db():
    """
    Connect to MongoDB and return the events collection.
    Call this once at app startup.
    """
    global _collection
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    _collection = client["github_webhooks"]["github_events"]
    return _collection


def _get_collection():
    """Return the collection, initialising if needed."""
    if _collection is None:
        init_db()
    return _collection


# ── CRUD operations ───────────────────────────────────────────────────

def upsert_webhook_event(event: Event) -> None:
    """
    Insert a webhook event into the database.
    If an event with the same request_id already exists, update it.
    """
    col = _get_collection()
    col.update_one(
        {"request_id": event.request_id},
        {"$set": event.to_dict()},
        upsert=True,
    )


def find_all_events() -> list[dict]:
    """Return every event, newest first, as plain dicts (no _id)."""
    col = _get_collection()
    return list(col.find({}, {"_id": 0}).sort("timestamp", -1))


def find_events_paginated(page: int = 1, per_page: int = 10) -> list[dict]:
    """Return a page of events, newest first."""
    col = _get_collection()
    skip = (page - 1) * per_page
    return list(
        col.find({}, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(per_page)
    )


def count_events() -> int:
    """Return the total number of events."""
    col = _get_collection()
    return col.count_documents({})


def find_events_by_action(action: EventAction) -> list[dict]:
    """Return events filtered by action type, newest first."""
    col = _get_collection()
    return list(
        col.find({"action": action.value}, {"_id": 0}).sort("timestamp", -1)
    )
