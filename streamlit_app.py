import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st
from freezerflow.database import init_db,fetchall
from freezerflow.services import *
from freezerflow.ui import inject_css,hero

st.set_page_config(page_title="FreezerFlow",page_icon="🧊",layout="wide",initial_sidebar_state="collapsed")
init_db();inject_css()
if "page" not in st.session_state:st.session_state.page="Tableau de bord"
if "focus" not in st.session_state:st.session_state.focus=None
def go(p,f=None):st.session_state.page=p;st.session_state.focus=f;st.rerun()
NAV=["Tableau de bord","Stockage","Disponibilités","Tubes","Scanner / QR","Recherche","Historique","Inventaire photo","Administration"]
with st.sidebar:
 st.markdown("## 🧊 FreezerFlow");st.caption("Laboratory sample storage");st.divider()
 for p in NAV:
  if st.button(p,use_container_width=True,key="nav"+p):go(p)
 st.divider();st.caption("V4.1 • Responsive • Multi-tubes • Excel • OCR")
st.title("FreezerFlow");st.caption("Gestion hiérarchique et traçable du stockage de laboratoire");page=st.session_state.page

def object_actions(o):
 with st.expander("✏️ Modifier / supprimer"):
  n=st.text_input("Nom",value=o["name"],key="nm"+o["uid"]);u=st.text_input("Utilisateur",key="usr"+o["uid"])
  a,b=st.columns(2)
  if a.button("Enregistrer",key="sv"+o["uid"],use_container_width=True):rename_object(o["uid"],n,u);st.rerun()
  confirm=st.checkbox("Confirmer la suppression",key="cf"+o["uid"])
  if b.button("Supprimer",key="del"+o["uid"],disabled=not confirm,use_container_width=True):
   ok,msg=archive_object(o["uid"],u)
   if ok:go("Stockage",o["parent_uid"])
   else:st.error(msg)

def excel_tools(o):
 st.subheader("Excel / import")
 st.download_button("Exporter ce niveau en Excel",export_excel(o["uid"]),f"{o['name']}_inventaire.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key="exp"+o["uid"])
 if o["kind"] not in ("SHELF","RACK","BOX"):return
 template={"SHELF":shelf_template,"RACK":rack_template,"BOX":box_template}[o["kind"]](o["uid"])
 st.download_button("Télécharger le template Excel",template,f"{o['name']}_template.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key="tpl"+o["uid"])
 up=st.file_uploader("Réimporter le template rempli",type=["xlsx"],key="xls"+o["uid"])
 if up:
  rows=parse_excel(up,o["kind"]);st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
  if st.button("Valider l'import Excel",key="ix"+o["uid"]):
   n,errs=import_rows(o["uid"],o["kind"],rows)
   if n:st.success(f"{n} élément(s) ajouté(s).")
   for e in errs:st.error(e)
   if n:st.rerun()

if page=="Tableau de bord":
 hero("Vue d'ensemble","Du congélateur au tube : naviguez, scannez et tracez chaque mouvement.")
 fs=roots();bs=all_boxes();ts=fetchall("SELECT * FROM tubes WHERE active=1 AND status='PRESENT'")
 cap=sum((b["rows_count"] or 0)*(b["cols_count"] or 0) for b in bs)
 a,b,c,d=st.columns(4);a.metric("Congélateurs",len(fs));b.metric("Boîtes",len(bs));c.metric("Tubes présents",len(ts));d.metric("Places libres",max(cap-len(ts),0))
 a,b,c,d=st.columns(4)
 if a.button("Stockage",use_container_width=True):go("Stockage")
 if b.button("Tubes",use_container_width=True):go("Tubes")
 if c.button("Scanner / QR",use_container_width=True):go("Scanner / QR")
 if d.button("Rechercher",use_container_width=True):go("Recherche")

elif page=="Stockage":
 st.header("Stockage");st.caption("Congélateur → Étagère → Rack → Boîte → Position")
 f=st.session_state.focus
 if not f:
  objs=roots();cols=st.columns(3)
  for i,o in enumerate(objs):
   with cols[i%3]:
    st.markdown(f"### 🧊 {o['name']}");st.caption(o["uid"])
    if st.button("Ouvrir",key="op"+o["uid"],use_container_width=True):go("Stockage",o["uid"])
    object_actions(o)
  with st.expander("➕ Ajouter un congélateur"):
   n=st.text_input("Nom",key="newfz")
   if st.button("Créer") and n.strip():create_storage("FREEZER",n);st.rerun()
 else:
  o=get_object(f)
  if not o:go("Stockage")
  trail=breadcrumb(f);st.caption(" → ".join(x["name"] for x in trail))
  if st.button("← Retour"):go("Stockage",trail[-2]["uid"] if len(trail)>1 else None)
  st.subheader(f"{o['name']} · {o['uid']}");object_actions(o)
  q=qr_png(o["uid"]);st.image(q,width=115);st.download_button("QR PNG",q,f"{o['uid']}.png","image/png")
  if o["kind"]=="BOX":
   pp=o.get("photo_path")
   if pp and Path(pp).exists():st.image(pp,caption="Photo de la boîte",use_container_width=True)
   tubes=tubes_in_box(o["uid"]);tm={t["position"]:t for t in tubes};cap=(o["rows_count"] or 0)*(o["cols_count"] or 0)
   st.metric("Occupation",f"{len(tubes)} / {cap}")
   st.subheader("Positions")
   # Interactive position selector is much clearer/responsive than 81 tiny buttons.
   pos=st.selectbox("Sélectionner une position", [f"{chr(65+r)}{c}" for r in range(o["rows_count"] or 0) for c in range(1,(o["cols_count"] or 0)+1)])
   if pos in tm:
    t=tm[pos];st.info(f"{pos} — {t['uid']} — {t['sample_name'] or 'sans nom'}")
    name=st.text_input("Échantillon",value=t["sample_name"] or "",key="pn"+pos);u=st.text_input("Utilisateur",key="pu"+pos)
    a,b=st.columns(2)
    if a.button("Modifier le tube",use_container_width=True):update_tube(t["uid"],name,u);st.rerun()
    if b.button("Retirer le tube",use_container_width=True):remove_tube(t["uid"],u);st.rerun()
   else:
    st.success(f"{pos} est libre.")
    uid=st.text_input("UID tube",key="puid"+pos);name=st.text_input("Échantillon",key="pname"+pos);u=st.text_input("Utilisateur",key="puser"+pos)
    if st.button("Ajouter ici"):
     try:create_tube(uid,name,o["uid"],pos,u);st.rerun()
     except sqlite3.IntegrityError:st.error("UID déjà utilisé ou position occupée.")
   st.subheader("Photo / OCR de la boîte")
   mode=st.radio("Source",["Prendre une photo","Importer une photo"],horizontal=True,key="ocrmode"+o["uid"])
   photo=st.camera_input("Photographier",key="ocrcam"+o["uid"]) if mode=="Prendre une photo" else st.file_uploader("JPG / PNG",type=["jpg","jpeg","png"],key="ocrup"+o["uid"])
   if photo:
    st.image(photo,use_container_width=True)
    if st.button("Lancer l'OCR",key="ocrgo"+o["uid"]):
     text,found,err=ocr_image(photo);st.session_state["ocr_"+o["uid"]]=found;st.session_state["ocrtxt_"+o["uid"]]=text
     if err:st.error("OCR indisponible : "+err)
   found=st.session_state.get("ocr_"+o["uid"],[])
   if found:
    edited=st.data_editor(pd.DataFrame(found),num_rows="dynamic",use_container_width=True,key="ocred"+o["uid"])
    st.caption("Vérifiez/corrigez les résultats avant validation.")
    if st.button("Valider les tubes OCR",key="ocrval"+o["uid"]):
     n,errs=import_rows(o["uid"],"BOX",edited.to_dict("records"))
     if n:st.success(f"{n} tube(s) ajouté(s).")
     for e in errs:st.error(e)
     if n:st.session_state.pop("ocr_"+o["uid"],None);st.rerun()
   with st.expander("Photo générale de la boîte"):
    ph=st.file_uploader("Conserver une photo",type=["jpg","jpeg","png"],key="photo"+o["uid"])
    if ph and st.button("Enregistrer la photo",key="savephoto"+o["uid"]):set_box_photo(o["uid"],ph);st.rerun()
   excel_tools(o)
  elif o["kind"]=="RACK":
   kids=children(o["uid"],"BOX");rr=o.get("rack_rows") or 3;rc=o.get("rack_cols") or 3;occ={x.get("rack_position"):x for x in kids if x.get("rack_position")}
   st.metric("Occupation",f"{len(kids)} / {rr*rc} boîtes");st.subheader("Plan physique du rack")
   for r in range(rr):
    cs=st.columns(rc)
    for c in range(1,rc+1):
     p=f"{chr(65+r)}{c}"
     with cs[c-1]:
      if p in occ:
       bx=occ[p];st.markdown(f'<div class="rackslot used">{p}<br>{bx["name"]}</div>',unsafe_allow_html=True)
       if st.button("Ouvrir",key="rb"+bx["uid"],use_container_width=True):go("Stockage",bx["uid"])
      else:st.markdown(f'<div class="rackslot free">{p}<br>LIBRE</div>',unsafe_allow_html=True)
   with st.expander("➕ Ajouter une boîte"):
    n=st.text_input("Nom",key="bn");slots=free_rack_slots(o["uid"]);rp=st.selectbox("Emplacement",slots) if slots else None
    rows=st.number_input("Lignes",1,26,9);cols=st.number_input("Colonnes",1,20,9)
    if st.button("Créer la boîte") and n.strip() and rp:create_storage("BOX",n,o["uid"],rows,cols,rack_position=rp);st.rerun()
   excel_tools(o)
  else:
   nk={"FREEZER":"SHELF","SHELF":"RACK"}[o["kind"]];kids=children(o["uid"],nk);cols=st.columns(3)
   for i,k in enumerate(kids):
    with cols[i%3]:
     st.markdown(f"### {k['name']}");st.caption(k["uid"])
     if st.button("Ouvrir",key="kid"+k["uid"],use_container_width=True):go("Stockage",k["uid"])
     object_actions(k)
   with st.expander("➕ Ajouter"):
    n=st.text_input("Nom",key="cn")
    if nk=="RACK":
     rr=st.number_input("Niveaux",1,20,3);rc=st.number_input("Boîtes par niveau",1,20,3)
     if st.button("Créer") and n.strip():create_storage("RACK",n,o["uid"],capacity=rr*rc,rack_rows=rr,rack_cols=rc);st.rerun()
    elif st.button("Créer") and n.strip():create_storage("SHELF",n,o["uid"]);st.rerun()
   excel_tools(o)

elif page=="Disponibilités":
 st.header("Disponibilités");b,p=first_free_location()
 if b:
  st.success(f"Première position libre : {b['name']} · {p}")
  if st.button("Ouvrir cette boîte"):go("Stockage",b["uid"])
 racks=[]
 for r in all_racks():
  total=(r.get("rack_rows") or 3)*(r.get("rack_cols") or 3);used=len(children(r["uid"],"BOX"))
  racks.append({"Rack":r["name"],"Boîtes":used,"Capacité":total,"Libres":max(total-used,0)})
 if racks:st.dataframe(pd.DataFrame(racks),hide_index=True,use_container_width=True)
 boxes=[]
 for b in all_boxes():
  cap=(b["rows_count"] or 0)*(b["cols_count"] or 0);used=len(tubes_in_box(b["uid"]))
  boxes.append({"Boîte":b["name"],"Tubes":used,"Capacité":cap,"Libres":max(cap-used,0)})
 if boxes:st.dataframe(pd.DataFrame(boxes),hide_index=True,use_container_width=True)

elif page=="Tubes":
 st.header("Gestion des tubes")
 boxes=all_boxes()
 tabs=st.tabs(["Ajouter","Modifier / retirer","Déplacer / remettre"])
 if not boxes:
  st.warning("Créez d'abord au moins une boîte.")
 else:
  boxmap={f"{b['name']} · {b['uid']}":b for b in boxes}
  with tabs[0]:
   mode=st.radio("Mode d'ajout",["Tube unique","Plusieurs tubes"],horizontal=True)
   bx=boxmap[st.selectbox("Boîte",list(boxmap),key="addbox")]
   free=free_positions(bx["uid"])
   if mode=="Tube unique":
    uid=st.text_input("Identifiant / QR du tube")
    sample=st.text_input("Nom / référence échantillon")
    pos=st.selectbox("Position libre",free) if free else None
    user=st.text_input("Utilisateur")
    if st.button("Ajouter le tube",use_container_width=True):
     if not uid.strip():st.error("Identifiant obligatoire.")
     elif not pos:st.error("Aucune position libre.")
     else:
      try:create_tube(uid,sample,bx["uid"],pos,user);st.rerun()
      except sqlite3.IntegrityError:st.error("UID déjà utilisé ou position occupée.")
   else:
    st.caption(f"{len(free)} position(s) libre(s) dans cette boîte.")
    sample=st.text_input("Nom / référence commune de l'échantillon",key="msample")
    maxq=max(1,len(free));qty=st.number_input("Nombre de tubes",1,maxq,min(10,maxq),1)
    c1,c2=st.columns(2)
    volume=c1.number_input("Volume par tube (optionnel)",min_value=0.0,value=0.0,step=0.1)
    unit=c2.selectbox("Unité",["µL","mL"])
    lot=st.text_input("Lot (optionnel)")
    prefix=st.text_input("Préfixe UID",value="T")
    user=st.text_input("Utilisateur",key="muser")
    proposed=free[:int(qty)]
    if proposed:
     st.subheader("Positions proposées")
     st.dataframe(pd.DataFrame({"Tube":[f"{prefix}-AUTO-{i+1:02d}" for i in range(int(qty))],"Échantillon":[sample]*int(qty),"Position":proposed}),hide_index=True,use_container_width=True)
    if st.button(f"Créer les {int(qty)} tubes",type="primary",use_container_width=True):
     created,errs=create_multiple_tubes(sample,bx["uid"],int(qty),user,prefix,volume if volume>0 else "",unit,lot)
     if created:st.success(f"{len(created)} tube(s) créé(s), chacun avec son UID/QR.");st.dataframe(pd.DataFrame(created),hide_index=True,use_container_width=True)
     for e in errs:st.error(e)
  with tabs[1]:
   ts=fetchall("SELECT * FROM tubes WHERE active=1 ORDER BY uid")
   if ts:
    mp={f"{t['uid']} · {t['status']}":t for t in ts};t=mp[st.selectbox("Tube",list(mp),key="edittube")]
    n=st.text_input("Échantillon / référence",value=t["sample_name"] or "",key="editname");u=st.text_input("Utilisateur",key="edituser")
    c1,c2=st.columns(2)
    if c1.button("Enregistrer",use_container_width=True):update_tube(t["uid"],n,u);st.rerun()
    if t["status"]=="PRESENT" and c2.button("Retirer",use_container_width=True):remove_tube(t["uid"],u);st.rerun()
   else:st.info("Aucun tube.")
  with tabs[2]:
   ts=fetchall("SELECT * FROM tubes WHERE active=1 ORDER BY uid")
   if ts:
    mp={f"{t['uid']} · {t['status']}":t for t in ts};t=mp[st.selectbox("Tube",list(mp),key="movetube")]
    dest=boxmap[st.selectbox("Boîte de destination",list(boxmap),key="destbox")];fp=free_positions(dest["uid"])
    if fp:
     pos=st.selectbox("Position libre",fp,key="destpos");u=st.text_input("Utilisateur",key="moveuser")
     if t["status"]=="PRESENT":
      if st.button("Déplacer le tube",use_container_width=True):move_tube(t["uid"],dest["uid"],pos,u);st.rerun()
     else:
      if st.button("Remettre le tube",use_container_width=True):restore_tube(t["uid"],dest["uid"],pos,u);st.rerun()

elif page=="Scanner / QR":
 st.header("Scanner / QR");code=st.text_input("QR / identifiant")
 if code:
  o=get_object(code);t=tube(code)
  if o:
   st.success(f"{o['kind']} : {o['name']}")
   if st.button("Ouvrir"):go("Stockage",o["uid"])
  elif t:st.success(f"{t['uid']} — {t['sample_name'] or ''} — {t['status']}")
  else:st.warning("Identifiant inconnu.")

elif page=="Recherche":
 st.header("Recherche globale");q=st.text_input("Rechercher")
 if q:
  like=f"%{q}%";oo=fetchall("SELECT uid,kind,name,parent_uid FROM storage_objects WHERE active=1 AND (uid LIKE ? OR name LIKE ?)",(like,like))
  tt=fetchall("SELECT uid,sample_name,box_uid,position,status FROM tubes WHERE active=1 AND (uid LIKE ? OR sample_name LIKE ?)",(like,like))
  if oo:st.dataframe(pd.DataFrame(oo),hide_index=True,use_container_width=True)
  if tt:st.dataframe(pd.DataFrame(tt),hide_index=True,use_container_width=True)
  if not oo and not tt:st.warning("Aucun résultat.")

elif page=="Historique":
 st.header("Historique / audit");r=fetchall("SELECT * FROM movements ORDER BY id DESC")
 if r:
  df=pd.DataFrame(r);st.dataframe(df,hide_index=True,use_container_width=True);st.download_button("Exporter CSV",df.to_csv(index=False).encode(),"historique.csv","text/csv")

elif page=="Inventaire photo":
 st.header("Inventaire photo / OCR");st.info("L'OCR opérationnel est maintenant intégré directement dans chaque boîte afin de connaître la boîte cible avant validation.")

elif page=="Administration":
 st.header("Administration");st.info("La modification et la suppression sécurisée sont maintenant disponibles directement dans Stockage, au niveau de chaque objet.")
