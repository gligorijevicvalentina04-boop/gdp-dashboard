import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "freezerflow.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c=sqlite3.connect(DB_PATH,check_same_thread=False)
    c.row_factory=sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("PRAGMA busy_timeout=5000")
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
    oldcols=_cols(c,"tubes")
    base=["id","uid","sample_name","box_uid","position","status","active","created_at","removed_at"]
    extra=[(n,t) for n,t in [("volume","REAL"),("volume_unit","TEXT"),("lot","TEXT"),("updated_at","TEXT")] if n in oldcols]
    fields=base+[n for n,_ in extra]
    with c:
        c.execute("DROP TABLE IF EXISTS tubes_new")
        c.execute("""CREATE TABLE tubes_new(
          id INTEGER PRIMARY KEY AUTOINCREMENT,uid TEXT UNIQUE NOT NULL,sample_name TEXT,
          box_uid TEXT NOT NULL,position TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'PRESENT',
          active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,removed_at TEXT,
          volume REAL,volume_unit TEXT,lot TEXT,updated_at TEXT)""")
        columns=",".join(fields)
        c.execute(f"INSERT INTO tubes_new ({columns}) SELECT {columns} FROM tubes")
        c.execute("DROP TABLE tubes")
        c.execute("ALTER TABLE tubes_new RENAME TO tubes")

def _init_db_schema():
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


# ---- V4.2: persistence / safe upgrades ----
def database_path():
    """Return the persistent SQLite file used by FreezerFlow."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DB_PATH

def backup_database(destination=None):
    """Create a consistent SQLite backup without modifying the live database."""
    from datetime import datetime
    if destination is None:
        backup_dir = DB_PATH.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        destination = backup_dir / f"freezerflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with connect() as source, sqlite3.connect(destination) as target:
        source.backup(target)
    return destination

def migrate_v42():
    """Non-destructive V4.2 migration. Existing tubes/history are preserved."""
    with connect() as c:
        cols = {r["name"] for r in c.execute("PRAGMA table_info(tubes)").fetchall()}
        additions = {
            "volume": "REAL",
            "volume_unit": "TEXT",
            "lot": "TEXT",
            "updated_at": "TEXT",
        }
        for name, sql_type in additions.items():
            if name not in cols:
                c.execute(f"ALTER TABLE tubes ADD COLUMN {name} {sql_type}")
        c.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations(
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
        """)
        c.execute("INSERT OR IGNORE INTO schema_migrations(version,applied_at) VALUES(?,?)",
                  ("4.2", now()))
        c.commit()

# V4.2.3 startup wrapper: schema + non-destructive migrations.
def init_db():
    _init_db_schema()
    migrate_v42()
