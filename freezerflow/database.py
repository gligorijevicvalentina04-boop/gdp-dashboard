import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/freezerflow.db")

def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS storage_objects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT UNIQUE NOT NULL,
            kind TEXT NOT NULL,
            name TEXT NOT NULL,
            parent_uid TEXT,
            rows_count INTEGER,
            cols_count INTEGER,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tubes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT UNIQUE NOT NULL,
            sample_name TEXT,
            box_uid TEXT NOT NULL,
            position TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PRESENT',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            removed_at TEXT,
            UNIQUE(box_uid, position)
        );
        CREATE TABLE IF NOT EXISTS movements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_uid TEXT NOT NULL,
            action TEXT NOT NULL,
            from_location TEXT,
            to_location TEXT,
            user_name TEXT,
            details TEXT,
            created_at TEXT NOT NULL
        );
        """)

def fetchall(sql, params=()):
    with connect() as c:
        return [dict(r) for r in c.execute(sql, params).fetchall()]

def fetchone(sql, params=()):
    with connect() as c:
        r = c.execute(sql, params).fetchone()
        return dict(r) if r else None

def execute(sql, params=()):
    with connect() as c:
        cur = c.execute(sql, params)
        c.commit()
        return cur.lastrowid
