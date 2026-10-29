"""
Unified Enterprise Database & Concurrency Engine for Laveto Wisdom & AW-1.
Supports PostgreSQL (via connection pool) and SQLite (with forced WAL mode & thread serialization).
"""
import os
import sqlite3
import threading
import contextlib

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_FALLBACK_PATH = os.getenv("LAVETO_DB_PATH", "/home/LavetoLab/lvt_backend/lvt_database.db")

_POSTGRES_POOL = None
_SQLITE_LOCK = threading.RLock()

def is_postgres():
    return bool(DATABASE_URL and DATABASE_URL.startswith("postgres"))

def _get_postgres_pool():
    global _POSTGRES_POOL
    if _POSTGRES_POOL is None and is_postgres():
        from psycopg2 import pool
        _POSTGRES_POOL = pool.ThreadedConnectionPool(
            minconn=int(os.getenv("DB_POOL_MIN", "2")),
            maxconn=int(os.getenv("DB_POOL_MAX", "20")),
            dsn=DATABASE_URL
        )
    return _POSTGRES_POOL

@contextlib.contextmanager
def get_db_connection():
    if is_postgres():
        p = _get_postgres_pool()
        conn = p.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            p.putconn(conn)
    else:
        db_path = os.getenv("LAVETO_DB_PATH", SQLITE_FALLBACK_PATH)
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        with _SQLITE_LOCK:
            conn = sqlite3.connect(db_path, timeout=60.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA busy_timeout = 60000;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA foreign_keys = ON;")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

@contextlib.contextmanager
def get_db_cursor():
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

def init_enterprise_schema():
    db_path = os.getenv("LAVETO_DB_PATH", SQLITE_FALLBACK_PATH)
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    if not is_postgres():
        c = sqlite3.connect(db_path, timeout=60.0)
        c.execute("PRAGMA journal_mode = WAL;")
        c.execute("PRAGMA synchronous = NORMAL;")
        c.close()

    pk_type = "BIGSERIAL PRIMARY KEY" if is_postgres() else "INTEGER PRIMARY KEY AUTOINCREMENT"
    ts_type = "TIMESTAMP" if is_postgres() else "DATETIME"
    bool_type = "BOOLEAN DEFAULT FALSE" if is_postgres() else "BOOLEAN DEFAULT 0"
    num_type = "DOUBLE PRECISION" if is_postgres() else "FLOAT"

    ddl = f"""
    CREATE TABLE IF NOT EXISTS auto_ingested_tenders (
        id {pk_type},
        tender_ref VARCHAR(64) UNIQUE NOT NULL,
        title VARCHAR(255) NOT NULL,
        procuring_entity VARCHAR(255) NOT NULL,
        is_reserved_sector {bool_type},
        closing_date {ts_type},
        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS audit_ledger (
        block_id {pk_type},
        prev_hash VARCHAR(64) NOT NULL,
        actor_id VARCHAR(64) NOT NULL,
        tool_name VARCHAR(64) NOT NULL,
        payload_hash VARCHAR(64) NOT NULL,
        decision VARCHAR(32) NOT NULL,
        token VARCHAR(64),
        current_hash VARCHAR(64) NOT NULL,
        timestamp {ts_type} DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS pouc_nodes (
        node_id VARCHAR(64) PRIMARY KEY,
        consensus_weight {num_type} DEFAULT 1.0,
        entropy_score {num_type} DEFAULT 0.0,
        hardware_interlock_pass BOOLEAN DEFAULT TRUE,
        last_seen {ts_type} DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS payment_transactions (
        id {pk_type},
        merchant_id BIGINT NOT NULL,
        gross_amount {num_type} NOT NULL,
        merchant_share {num_type} NOT NULL,
        platform_fee {num_type} NOT NULL,
        laveto_fee {num_type} NOT NULL,
        payment_status VARCHAR(32) NOT NULL,
        is_settled {bool_type},
        settlement_ref VARCHAR(64),
        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        if is_postgres():
            cur.execute(ddl)
        else:
            cur.executescript(ddl)
        cur.close()
    return True
