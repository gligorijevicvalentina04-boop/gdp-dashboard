import io, uuid
import qrcode
from freezerflow.database import execute, fetchall, fetchone, now

PREFIX = {"FREEZER":"FZ","SHELF":"SH","RACK":"RK","BOX":"BOX","TUBE":"T"}

def new_uid(kind):
    return f"{PREFIX[kind]}-{uuid.uuid4().hex[:8].upper()}"

def create_storage(kind, name, parent_uid=None, rows=None, cols=None):
    uid = new_uid(kind)
    execute("""INSERT INTO storage_objects(uid,kind,name,parent_uid,rows_count,cols_count,created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (uid, kind, name.strip(), parent_uid, rows, cols, now()))
    execute("""INSERT INTO movements(object_uid,action,to_location,details,created_at)
               VALUES(?,?,?,?,?)""",
            (uid, "CREATION", parent_uid, f"Création {kind}: {name}", now()))
    return uid

def children(parent_uid, kind=None):
    if kind:
        return fetchall("""SELECT * FROM storage_objects WHERE parent_uid=? AND kind=? AND active=1 ORDER BY name""",
                        (parent_uid, kind))
    return fetchall("""SELECT * FROM storage_objects WHERE parent_uid=? AND active=1 ORDER BY kind,name""",
                    (parent_uid,))

def roots():
    return fetchall("""SELECT * FROM storage_objects WHERE kind='FREEZER' AND active=1 ORDER BY name""")

def get_object(uid):
    return fetchone("SELECT * FROM storage_objects WHERE uid=? AND active=1", (uid,))

def breadcrumb(uid):
    out=[]
    cur=get_object(uid)
    while cur:
        out.append(cur)
        cur=get_object(cur["parent_uid"]) if cur["parent_uid"] else None
    return list(reversed(out))

def create_tube(tube_uid, sample_name, box_uid, position, user_name=""):
    tube_uid=tube_uid.strip()
    execute("""INSERT INTO tubes(uid,sample_name,box_uid,position,status,created_at)
               VALUES(?,?,?,?, 'PRESENT', ?)""",
            (tube_uid, sample_name.strip(), box_uid, position, now()))
    execute("""INSERT INTO movements(object_uid,action,to_location,user_name,details,created_at)
               VALUES(?,?,?,?,?,?)""",
            (tube_uid,"AJOUT",f"{box_uid}/{position}",user_name,"Tube ajouté",now()))

def tube(uid):
    return fetchone("SELECT * FROM tubes WHERE uid=? AND active=1", (uid,))

def tubes_in_box(box_uid):
    return fetchall("""SELECT * FROM tubes WHERE box_uid=? AND active=1 AND status='PRESENT' ORDER BY position""",
                    (box_uid,))

def remove_tube(uid, user_name=""):
    t=tube(uid)
    if not t: return False
    execute("UPDATE tubes SET status='RETIRED', removed_at=? WHERE uid=?", (now(),uid))
    execute("""INSERT INTO movements(object_uid,action,from_location,user_name,details,created_at)
               VALUES(?,?,?,?,?,?)""",
            (uid,"RETRAIT",f"{t['box_uid']}/{t['position']}",user_name,"Tube retiré",now()))
    return True

def restore_tube(uid, box_uid, position, user_name=""):
    execute("""UPDATE tubes SET box_uid=?,position=?,status='PRESENT',removed_at=NULL WHERE uid=?""",
            (box_uid,position,uid))
    execute("""INSERT INTO movements(object_uid,action,to_location,user_name,details,created_at)
               VALUES(?,?,?,?,?,?)""",
            (uid,"REMISE",f"{box_uid}/{position}",user_name,"Tube remis",now()))

def move_tube(uid, box_uid, position, user_name=""):
    t=tube(uid)
    old=f"{t['box_uid']}/{t['position']}"
    execute("UPDATE tubes SET box_uid=?,position=? WHERE uid=?", (box_uid,position,uid))
    execute("""INSERT INTO movements(object_uid,action,from_location,to_location,user_name,details,created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (uid,"DEPLACEMENT",old,f"{box_uid}/{position}",user_name,"Tube déplacé",now()))

def archive_object(uid):
    execute("UPDATE storage_objects SET active=0 WHERE uid=?", (uid,))
    execute("""INSERT INTO movements(object_uid,action,details,created_at) VALUES(?,?,?,?)""",
            (uid,"ARCHIVAGE","Objet retiré de la navigation sans effacer l'historique",now()))

def qr_png(value):
    img=qrcode.make(value)
    b=io.BytesIO()
    img.save(b,format="PNG")
    return b.getvalue()

def free_positions(box_uid):
    b=get_object(box_uid)
    if not b or not b["rows_count"] or not b["cols_count"]: return []
    used={t["position"] for t in tubes_in_box(box_uid)}
    return [f"{chr(65+r)}{c}" for r in range(b["rows_count"]) for c in range(1,b["cols_count"]+1)
            if f"{chr(65+r)}{c}" not in used]
