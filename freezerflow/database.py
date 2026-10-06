import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/freezerflow.db")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c=sqlite3.connect(DB_PATH,check_same_thread=False)
    c.row_factory=sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _cols(c,t): return {r["name"] for r in c.execute(f"PRAGMA table_info({t})")}

def _migrate_storage(c):
    cols=_cols(c,"storage_objects")
    for n,t in {"capacity":"INTEGER","rack_rows":"INTEGER","rack_cols":"INTEGER",
                "rack_position":"TEXT","photo_path":"TEXT"}.items():
        if n not in cols: c.execute(f"ALTER TABLE storage_objects ADD COLUMN {n} {t}")

def _legacy_tube_unique(c):
    for idx in c.execute("PRAGMA index_list(tubes)"):
        if idx["unique"]:
            cs=[r["name"] for r in c.execute(f'PRAGMA index_info("{idx["name"]}")')]
            if cs==["box_uid","position"]: return True
    return False

def _migrate_tubes(c):
    if not _legacy_tube_unique(c): return
    c.executescript("""
    CREATE TABLE tubes_new(
      id INTEGER PRIMARY KEY AUTOINCREMENT,uid TEXT UNIQUE NOT NULL,sample_name TEXT,
      box_uid TEXT NOT NULL,position TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'PRESENT',
      active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,removed_at TEXT);
    INSERT INTO tubes_new SELECT id,uid,sample_name,box_uid,position,status,active,created_at,removed_at FROM tubes;
    DROP TABLE tubes;
    ALTER TABLE tubes_new RENAME TO tubes;""")

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS storage_objects(
          id INTEGER PRIMARY KEY AUTOINCREMENT,uid TEXT UNIQUE NOT NULL,kind TEXT NOT NULL,
          name TEXT NOT NULL,parent_uid TEXT,rows_count INTEGER,cols_count INTEGER,
          capacity INTEGER,rack_rows INTEGER,rack_cols INTEGER,rack_position TEXT,photo_path TEXT,
          active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tubes(
          id INTEGER PRIMARY KEY AUTOINCREMENT,uid TEXT UNIQUE NOT NULL,sample_name TEXT,
          box_uid TEXT NOT NULL,position TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'PRESENT',
          active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,removed_at TEXT);
        CREATE TABLE IF NOT EXISTS movements(
          id INTEGER PRIMARY KEY AUTOINCREMENT,object_uid TEXT NOT NULL,action TEXT NOT NULL,
          from_location TEXT,to_location TEXT,user_name TEXT,details TEXT,created_at TEXT NOT NULL);
        """)
        _migrate_storage(c); _migrate_tubes(c)
        c.execute("""CREATE UNIQUE INDEX IF NOT EXISTS ux_present_position ON tubes(box_uid,position)
                     WHERE active=1 AND status='PRESENT'""")
        c.execute("""CREATE UNIQUE INDEX IF NOT EXISTS ux_active_rack_position
                     ON storage_objects(parent_uid,rack_position)
                     WHERE active=1 AND kind='BOX' AND rack_position IS NOT NULL""")
        c.commit()

def fetchall(sql,params=()):
    with connect() as c:return [dict(r) for r in c.execute(sql,params).fetchall()]
def fetchone(sql,params=()):
    with connect() as c:
        r=c.execute(sql,params).fetchone();return dict(r) if r else None
def execute(sql,params=()):
    with connect() as c:
        cur=c.execute(sql,params);c.commit();return cur.lastrowid
