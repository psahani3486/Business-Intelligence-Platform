import logging
import duckdb
import os
import pandas as pd
from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Get absolute path to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'warehouse.duckdb')

# Connection string determines backend mode
DATABASE_URL = os.environ.get("DATABASE_URL")
IS_POSTGRES = DATABASE_URL is not None and DATABASE_URL.startswith("postgresql")

# Setup SQLAlchemy engine if PostgreSQL is configured
engine = None
if IS_POSTGRES:
    logger.info(f"Initializing PostgreSQL connection to {DATABASE_URL.split('@')[-1]}")
    engine = create_engine(DATABASE_URL)

@contextmanager
def get_db_connection(read_only=True):
    """Yields a database connection (DuckDB or SQLAlchemy)."""
    if IS_POSTGRES:
        with engine.connect() as conn:
            yield conn
    else:
        # Fallback to DuckDB
        db_path = os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = duckdb.connect(database=db_path, read_only=read_only)
        try:
            yield conn
        finally:
            conn.close()

def execute_query(query: str, fetch_results: bool = True):
    """
    Executes a query and returns results as a Pandas DataFrame.
    Seamlessly switches between PostgreSQL and DuckDB.
    """
    with get_db_connection(read_only=fetch_results) as conn:
        if IS_POSTGRES:
            if fetch_results:
                # Pandas handles the SQLAlchemy connection natively
                return pd.read_sql(query, conn)
            else:
                from sqlalchemy import text
                conn.execute(text(query))
                conn.commit()
                return None
        else:
            result = conn.execute(query)
            if fetch_results:
                return result.fetchdf()
            return None

# Redis / In-Memory Cache implementation
_redis_client = None
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

try:
    import redis
    _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    _redis_client.ping()
    logger.info(f"Connected to Redis cache at {REDIS_URL}")
except Exception as e:
    logger.info("Redis server un-reachable; operating with local in-memory fallback cache.")
    _redis_client = None

_memory_cache = {}

def get_cache(key: str) -> Optional[str]:
    """Retrieves cached entry from Redis or local memory cache."""
    if _redis_client:
        try:
            return _redis_client.get(key)
        except Exception:
            pass
    entry = _memory_cache.get(key)
    if entry and entry['expires_at'] > pd.Timestamp.now().timestamp():
        return entry['value']
    return None

def set_cache(key: str, value: str, ttl_seconds: int = 300):
    """Sets cached entry in Redis or local memory cache with TTL."""
    if _redis_client:
        try:
            _redis_client.setex(key, ttl_seconds, value)
            return
        except Exception:
            pass
    _memory_cache[key] = {
        'value': value,
        'expires_at': pd.Timestamp.now().timestamp() + ttl_seconds
    }

def invalidate_cache(pattern: str = "*"):
    """Invalidates cache matching key pattern."""
    if _redis_client:
        try:
            for k in _redis_client.scan_iter(pattern):
                _redis_client.delete(k)
        except Exception:
            pass
    _memory_cache.clear()
