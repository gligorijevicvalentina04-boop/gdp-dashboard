"""FreezerFlow visual design: CSS-only enhancements, no database writes."""
import streamlit as st


def apply_design():
    st.markdown('''<style>
:root{--ff-navy:#081b34;--ff-blue:#12365e;--ff-teal:#0c9e9a;--ff-border:#dbe5f0}
.stApp{background:linear-gradient(145deg,#f6faff 0%,#edf4fc 100%);color:#172c45}
.main .block-container{max-width:1440px;padding-top:1.5rem;padding-bottom:5rem}
[data-testid="stSidebar"]{background:linear-gradient(160deg,#07172d,#102c4d 85%);border-right:1px solid #24425f}
[data-testid="stSidebar"] .stButton button{background:#123454!important;color:#f3f9ff!important;border:1px solid #294b6b!important;border-radius:13px!important;min-height:49px!important;box-shadow:0 3px 8px #00152a20;transition:background .16s,transform .16s}
[data-testid="stSidebar"] .stButton button:hover{background:#17627b!important;border-color:#35c9c0!important;transform:translateY(-1px)}
.stButton button[kind="primary"],.stDownloadButton button[kind="primary"]{background:linear-gradient(115deg,#087f8c,#0d9e9b)!important;color:white!important;border:0!important}
.main .stButton button,.main .stDownloadButton button,.main .stLinkButton a{border-radius:13px;min-height:46px;font-weight:650;border:1px solid #cbd9e8;box-shadow:0 2px 5px #09274410;transition:box-shadow .15s,transform .15s}
.main .stButton button:hover,.main .stDownloadButton button:hover{border-color:#0c9e9a;box-shadow:0 5px 14px #0c5d7b24;transform:translateY(-1px)}
[data-testid="stMetric"]{background:white;border:1px solid var(--ff-border);border-radius:17px;padding:15px 17px;box-shadow:0 4px 16px #11315b0a}
[data-testid="stMetricLabel"]{color:#57718b}
[data-testid="stExpander"]{border:1px solid #d9e5f0;border-radius:15px;background:#fff;overflow:hidden}
[data-testid="stFileUploader"]{border-radius:14px}
.st-key-physical_freezer{background:linear-gradient(160deg,#e7f1ff,#d8e7fa)!important;border:1px solid #90b1da!important;border-radius:22px!important;padding:1.1rem!important;box-shadow:0 12px 25px #163c7212}
.st-key-physical_freezer .stButton button{background:linear-gradient(160deg,#fff,#f5fbff)!important;color:#163453!important;border:1px solid #9dbde1!important;border-radius:14px!important;min-height:96px!important;white-space:pre-line!important;box-shadow:0 4px 10px #16457512!important}
.st-key-physical_freezer .stButton button:hover{background:#e9fffc!important;border-color:#0c9e9a!important}
.st-key-box_position_grid .stButton button{background:#fff;min-height:37px;border-radius:7px;font-size:.77rem;padding:0!important}
.st-key-box_position_grid .stButton button:hover{background:#d6f5f1;border-color:#0c9e9a}
.ff-section-title{color:#102f52;font-size:1.1rem;font-weight:800;letter-spacing:.01em;margin:12px 0 9px}
.ff-shelf-head{display:flex;justify-content:space-between;align-items:center;font-size:.9rem;font-weight:750;color:#24466d;margin:.8rem 0 .3rem}
.ff-shelf-line{height:4px;background:linear-gradient(90deg,#4077bc,#0c9e9a);border-radius:4px;margin:.6rem 0 1.1rem}
.ff-breadcrumb{background:#edf5fc;border:1px solid #d5e5f4;border-radius:12px;padding:10px 13px;color:#3b5d80;font-size:.85rem}
.rackslot{border:1px solid #bdd2e6;border-radius:12px;padding:1rem .35rem;min-height:84px;display:flex;align-items:center;justify-content:center;flex-direction:column;overflow-wrap:anywhere}
.rackslot.used{background:#e0f4fc;color:#115b82}.rackslot.free{background:#fff;color:#7890a6}
@media(max-width:760px){
.main .block-container{padding:.75rem .65rem 4rem!important}
[data-testid="stSidebar"]{min-width:min(85vw,300px)!important;max-width:min(85vw,300px)!important}
.st-key-physical_freezer{padding:.75rem .4rem!important}
.st-key-physical_freezer [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:5px!important}
.st-key-physical_freezer [data-testid="column"]{min-width:0!important;width:0!important;flex:1 1 0!important}
.st-key-physical_freezer .stButton button{min-height:83px!important;font-size:clamp(9px,2.6vw,12px)!important;padding:7px 2px!important}
.st-key-box_position_grid [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:2px!important}
.st-key-box_position_grid [data-testid="column"]{min-width:0!important;width:0!important;flex:1 1 0!important}
.st-key-box_position_grid .stButton button{min-height:31px!important;font-size:9px!important}
}
</style>''', unsafe_allow_html=True)
