"""MongoDB access. One document per lead in the `leads` collection.

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
    return _db


def leads():
    return get_db().leads


def ping():
    try:
        get_db().command("ping")
        return True, get_db().name
    except Exception as e:  # report, never crash the health check
        return False, str(e)[:200]
