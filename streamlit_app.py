import sqlite3
import streamlit as st
import pandas as pd
from freezerflow.database import init_db, fetchall
from freezerflow.services import (
    create_storage, roots, children, get_object, breadcrumb, create_tube,
    tubes_in_box, remove_tube, restore_tube, move_tube, archive_object,
    qr_png, free_positions, tube
)
from freezerflow.ui import inject_css, hero

st.set_page_config(page_title="FreezerFlow", page_icon="🧊", layout="wide",
                   initial_sidebar_state="expanded")
init_db()
inject_css()

if "page" not in st.session_state: st.session_state.page="Tableau de bord"
if "focus" not in st.session_state: st.session_state.focus=None

def go(page, focus=None):
    st.session_state.page=page
    st.session_state.focus=focus
    st.rerun()

def all_boxes():
    return fetchall("SELECT * FROM storage_objects WHERE kind='BOX' AND active=1 ORDER BY name")

def label_obj(o):
    return f"{o['name']} · {o['uid']}"

with st.sidebar:
    st.markdown("## 🧊 FreezerFlow")
    st.caption("Laboratory sample storage")
    st.divider()
    for p in ["Tableau de bord","Stockage","Tubes","Scanner / QR","Recherche","Historique","Inventaire photo","Administration"]:
        if st.button(p,use_container_width=True,key="nav"+p):
            go(p)
    st.divider()
    st.caption("Prototype V2 • SQLite")

st.title("FreezerFlow")
st.caption("Gestion hiérarchique et traçable du stockage de laboratoire")

page=st.session_state.page

if page=="Tableau de bord":
    hero("Vue d'ensemble","Du congélateur au tube : naviguez, scannez et tracez chaque mouvement.")
    fs=fetchall("SELECT * FROM storage_objects WHERE kind='FREEZER' AND active=1")
    bs=all_boxes()
    ts=fetchall("SELECT * FROM tubes WHERE active=1 AND status='PRESENT'")
    cap=sum((b["rows_count"] or 0)*(b["cols_count"] or 0) for b in bs)
    a,b,c,d=st.columns(4)
    a.metric("Congélateurs",len(fs)); b.metric("Boîtes",len(bs))
    c.metric("Tubes présents",len(ts)); d.metric("Places libres",max(cap-len(ts),0))
    st.subheader("Accès rapide")
    x,y,z=st.columns(3)
    if x.button("🧊 Explorer le stockage",use_container_width=True): go("Stockage")
    if y.button("➕ Gérer les tubes",use_container_width=True): go("Tubes")
    if z.button("▣ Scanner / QR",use_container_width=True): go("Scanner / QR")

elif page=="Stockage":
    st.header("Stockage")
    st.caption("Navigation zoom / dézoom : Congélateur → Étagère → Rack → Boîte → Position")
    focus=st.session_state.focus
    if not focus:
        st.subheader("Congélateurs")
        objs=roots()
        cols=st.columns(3)
        for i,o in enumerate(objs):
            with cols[i%3]:
                st.markdown(f"### 🧊 {o['name']}")
                st.caption(o["uid"])
                if st.button("Ouvrir",key="open"+o["uid"],use_container_width=True): go("Stockage",o["uid"])
        st.divider()
        with st.expander("➕ Ajouter un congélateur",expanded=not objs):
            name=st.text_input("Nom",placeholder="FZ-01",key="newfz")
            if st.button("Créer le congélateur"):
                if name.strip():
                    create_storage("FREEZER",name); st.rerun()
    else:
        obj=get_object(focus)
        if not obj:
            st.session_state.focus=None; st.rerun()
        trail=breadcrumb(focus)
        st.markdown(" → ".join(f"**{x['name']}**" for x in trail))
        if len(trail)>1:
            if st.button("← Niveau précédent"): go("Stockage",trail[-2]["uid"])
        else:
            if st.button("← Tous les congélateurs"): go("Stockage")
        st.subheader(f"{obj['name']}  ·  {obj['uid']}")
        qr=qr_png(obj["uid"])
        q1,q2=st.columns([1,4])
        with q1:
            st.image(qr,width=130)
            st.download_button("QR PNG",qr,file_name=f"{obj['uid']}.png",mime="image/png")

        next_kind={"FREEZER":"SHELF","SHELF":"RACK","RACK":"BOX"}.get(obj["kind"])
        next_name={"FREEZER":"étagère","SHELF":"rack","RACK":"boîte"}.get(obj["kind"])

        if obj["kind"]=="BOX":
            tubes=tubes_in_box(obj["uid"]); tm={t["position"]:t for t in tubes}
            capacity=obj["rows_count"]*obj["cols_count"]
            st.metric("Occupation",f"{len(tubes)} / {capacity}")
            h=st.columns(obj["cols_count"]+1)
            for c in range(1,obj["cols_count"]+1): h[c].markdown(f"**{c}**")
            for r in range(obj["rows_count"]):
                letter=chr(65+r); cs=st.columns(obj["cols_count"]+1); cs[0].markdown(f"**{letter}**")
                for c in range(1,obj["cols_count"]+1):
                    pos=f"{letter}{c}"
                    css="occupied" if pos in tm else "empty"
                    cs[c].markdown(f'<div class="slot {css}">{pos}</div>',unsafe_allow_html=True)
            if tubes:
                st.dataframe(pd.DataFrame(tubes)[["uid","sample_name","position","status"]],
                             hide_index=True,use_container_width=True)
        else:
            kids=children(obj["uid"],next_kind)
            st.subheader(f"{next_name.capitalize()}s")
            cols=st.columns(3)
            for i,k in enumerate(kids):
                with cols[i%3]:
                    st.markdown(f"### {k['name']}")
                    st.caption(k["uid"])
                    if st.button("Zoom →",key="kid"+k["uid"],use_container_width=True): go("Stockage",k["uid"])
            st.divider()
            with st.expander(f"➕ Ajouter un(e) {next_name}"):
                nm=st.text_input("Nom",key="childname",placeholder={"SHELF":"Étagère 01","RACK":"Rack 01","BOX":"Boîte 01"}[next_kind])
                if next_kind=="BOX":
                    typ=st.selectbox("Format",["81 places — 9 × 9","Demi-boîte configurable","Personnalisée"])
                    if typ=="81 places — 9 × 9": rows,cols_n=9,9
                    else:
                        rows=st.number_input("Lignes",1,26,5 if "Demi" in typ else 9)
                        cols_n=st.number_input("Colonnes",1,20,9)
                else: rows=cols_n=None
                if st.button("Créer",key="createchild"):
                    if nm.strip():
                        uid=create_storage(next_kind,nm,obj["uid"],rows,cols_n)
                        st.success(f"Créé : {uid}"); st.rerun()

elif page=="Tubes":
    st.header("Gestion des tubes")
    boxes=all_boxes()
    if not boxes:
        st.warning("Crée d'abord au moins une boîte dans Stockage.")
    else:
        tabs=st.tabs(["Ajouter","Retirer / remettre","Déplacer"])
        boxmap={label_obj(b):b for b in boxes}
        with tabs[0]:
            bx=boxmap[st.selectbox("Boîte",list(boxmap),key="abox")]
            free=free_positions(bx["uid"])
            with st.form("addtube"):
                uid=st.text_input("Identifiant / QR du tube",placeholder="T-2026-00452")
                sample=st.text_input("Nom / référence échantillon")
                pos=st.selectbox("Position libre",free) if free else None
                user=st.text_input("Utilisateur")
                ok=st.form_submit_button("Ajouter le tube",use_container_width=True)
                if ok:
                    if not uid.strip(): st.error("Identifiant obligatoire.")
                    elif not pos: st.error("Boîte complète.")
                    else:
                        try:
                            create_tube(uid,sample,bx["uid"],pos,user); st.success(f"{uid} ajouté en {pos}.")
                        except sqlite3.IntegrityError: st.error("Identifiant déjà utilisé ou position occupée.")
        with tabs[1]:
            all_t=fetchall("SELECT * FROM tubes WHERE active=1 ORDER BY uid")
            if all_t:
                tm={f"{t['uid']} · {t['status']}":t for t in all_t}
                t=tm[st.selectbox("Tube",list(tm),key="rtube")]
                user=st.text_input("Utilisateur",key="ruser")
                if t["status"]=="PRESENT":
                    if st.button("Confirmer le retrait",type="primary"):
                        remove_tube(t["uid"],user); st.rerun()
                else:
                    bx=boxmap[st.selectbox("Boîte de remise",list(boxmap),key="rbox")]
                    fp=free_positions(bx["uid"])
                    if fp:
                        pos=st.selectbox("Position",fp,key="rpos")
                        if st.button("Remettre le tube"):
                            restore_tube(t["uid"],bx["uid"],pos,user); st.rerun()
            else: st.info("Aucun tube.")
        with tabs[2]:
            present=fetchall("SELECT * FROM tubes WHERE active=1 AND status='PRESENT' ORDER BY uid")
            if present:
                tm={t["uid"]:t for t in present}
                t=tm[st.selectbox("Tube à déplacer",list(tm),key="mtube")]
                bx=boxmap[st.selectbox("Nouvelle boîte",list(boxmap),key="mbox")]
                fp=free_positions(bx["uid"])
                if fp:
                    pos=st.selectbox("Nouvelle position",fp)
                    user=st.text_input("Utilisateur",key="muser")
                    if st.button("Déplacer"):
                        move_tube(t["uid"],bx["uid"],pos,user); st.rerun()

elif page=="Scanner / QR":
    st.header("Scanner / QR")
    st.info("V2 : saisissez/scannez l'identifiant avec un lecteur QR USB/Bluetooth. La caméra QR web sera ajoutée avec le module OCR.")
    code=st.text_input("QR / identifiant")
    if code:
        o=get_object(code)
        t=tube(code)
        if o:
            st.success(f"{o['kind']} : {o['name']}")
            if st.button("Ouvrir cet emplacement"): go("Stockage",o["uid"])
        elif t:
            st.success(f"Tube {t['uid']} — {t['sample_name'] or 'sans référence'} — {t['status']}")
        else: st.warning("Identifiant inconnu.")
    st.subheader("Générer / imprimer un QR")
    objs=fetchall("SELECT uid,name,kind FROM storage_objects WHERE active=1 ORDER BY kind,name")
    vals=[(o["uid"],f"{o['kind']} · {o['name']} · {o['uid']}") for o in objs]
    vals += [(t["uid"],f"TUBE · {t['uid']}") for t in fetchall("SELECT uid FROM tubes WHERE active=1 ORDER BY uid")]
    if vals:
        mp={lab:uid for uid,lab in vals}; lab=st.selectbox("Objet",list(mp)); uid=mp[lab]; q=qr_png(uid)
        st.image(q,width=230); st.code(uid)
        st.download_button("Télécharger le QR",q,file_name=f"{uid}.png",mime="image/png")

elif page=="Recherche":
    st.header("Recherche globale")
    q=st.text_input("Tube, échantillon, boîte, rack, étagère ou congélateur")
    if q:
        like=f"%{q}%"
        objs=fetchall("""SELECT uid,kind,name,parent_uid FROM storage_objects
                         WHERE active=1 AND (uid LIKE ? OR name LIKE ?) ORDER BY kind,name""",(like,like))
        ts=fetchall("""SELECT uid,sample_name,box_uid,position,status FROM tubes
                       WHERE active=1 AND (uid LIKE ? OR sample_name LIKE ?) ORDER BY uid""",(like,like))
        if objs: st.subheader("Emplacements"); st.dataframe(pd.DataFrame(objs),hide_index=True,use_container_width=True)
        if ts: st.subheader("Tubes"); st.dataframe(pd.DataFrame(ts),hide_index=True,use_container_width=True)
        if not objs and not ts: st.warning("Aucun résultat.")

elif page=="Historique":
    st.header("Historique / audit")
    rows=fetchall("SELECT * FROM movements ORDER BY id DESC")
    if rows:
        df=pd.DataFrame(rows); st.dataframe(df,hide_index=True,use_container_width=True)
        st.download_button("Exporter CSV",df.to_csv(index=False).encode("utf-8"),
                           "freezerflow_historique.csv","text/csv")
    else: st.info("Aucun mouvement.")

elif page=="Inventaire photo":
    st.header("Inventaire photo / OCR")
    st.caption("L'OCR proposera les lectures ; aucune modification de stock sans validation humaine.")
    img=st.camera_input("Photographier la boîte")
    up=st.file_uploader("ou importer une image",type=["jpg","jpeg","png"])
    source=img or up
    if source:
        st.image(source,caption="Photo source")
        st.warning("OCR réel non activé dans ce package : la détection de texte et de positions sera branchée après le test fonctionnel V2. Aucun faux résultat n'est généré.")

elif page=="Administration":
    st.header("Administration")
    st.subheader("Archivage des objets")
    st.caption("Archivage logique : l'historique est conservé.")
    objs=fetchall("SELECT uid,kind,name FROM storage_objects WHERE active=1 ORDER BY kind,name")
    if objs:
        mp={f"{o['kind']} · {o['name']} · {o['uid']}":o for o in objs}
        lab=st.selectbox("Objet à archiver",list(mp))
        confirm=st.checkbox("Je confirme l'archivage")
        if st.button("Archiver",disabled=not confirm):
            archive_object(mp[lab]["uid"]); st.rerun()
    st.divider()
    st.warning("Prototype : SQLite. Pour une utilisation réelle simultanée par plusieurs personnes, migration PostgreSQL + authentification avant mise en production.")
