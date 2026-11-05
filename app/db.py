"""MongoDB access. Collections: leads, sources, inbox_log, agent_state (see agent/store.py).

Connection string comes from .env (MONGODB=..., MONGODB_URI=... or MONGO_URI=...).
Database name: the one in the URI if present, else MONGODB_DB, else "flytbase_leads".
"""
import datetime

from pymongo import DESCENDING, MongoClient

from agent import config

_client = None
_db = None


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def uri():
    return config._get("MONGODB", "MONGODB_URI", "MONGO_URI")


def get_db():
    global _client, _db
    if _db is None:
        if not uri():
            raise RuntimeError("No MongoDB connection string. Add MONGODB=mongodb+srv://... to .env")
        _client = MongoClient(uri(), serverSelectionTimeoutMS=8000, tz_aware=True)
        try:
            _db = _client.get_default_database()
        except Exception:
            _db = _client[config._get("MONGODB_DB") or "flytbase_leads"]
        _db.leads.create_index([("created_at", DESCENDING)])
        _db.leads.create_index("status")
        # one lead per Gmail message, even if two agent ticks overlap
        _db.leads.create_index("gmail.message_id", unique=True,
                               partialFilterExpression={"gmail.message_id": {"$type": "string"}})
        _db.sources.create_index([("lead_id", 1), ("id", 1)], unique=True)
        _db.sources.create_index([("lead_id", 1), ("url", 1)], unique=True)
        _db.inbox_log.create_index([("checked_at", DESCENDING)])
    return _db


def leads():
    return get_db().leads


def ping():
    try:
        get_db().command("ping")
        return True, get_db().name
    except Exception as e:  # report, never crash the health check
        return False, str(e)[:200]
