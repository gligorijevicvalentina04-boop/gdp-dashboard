import streamlit as st
def inject_css():

 st.markdown("""<style>
 .stApp{background:linear-gradient(180deg,#f8fbff,#f2f6fb)}.block-container{max-width:1450px;padding-top:2.5rem;padding-bottom:4rem}
 [data-testid="stSidebar"]{background:linear-gradient(180deg,#07182d,#0b2545)}
 [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] p{color:#f8fafc}
 [data-testid="stSidebar"] div.stButton>button{background:#102c4c;color:#eaf4ff;border:1px solid #244665}
 div.stButton>button{border-radius:12px;font-weight:650;min-height:44px}
 .hero{padding:1.45rem 1.65rem;border-radius:24px;background:linear-gradient(135deg,#0b2545,#0879ae);margin-bottom:1.3rem}
 .hero h2{color:white;margin:0}.hero p{color:#dff4ff;margin:.5rem 0 0}
 .rackslot{border:1px solid #cbd5e1;border-radius:12px;padding:.65rem;text-align:center;min-height:62px;font-weight:750}
 .used{background:#e0f2fe;color:#075985}.free{background:#fff;color:#64748b}
 @media(max-width:768px){.block-container{padding:.7rem .65rem 3rem}.hero{padding:.9rem 1rem;border-radius:17px}
 h1{font-size:1.7rem!important}h2{font-size:1.35rem!important}h3{font-size:1.1rem!important}
 div.stButton>button{min-height:46px}[data-testid="stSidebar"]{min-width:min(86vw,320px)!important;max-width:min(86vw,320px)!important}}
 </style>""",unsafe_allow_html=True)
 st.markdown("""<style>
 .st-key-physical_freezer{background:linear-gradient(150deg,#e9f1ff,#dce8fa);border:1px solid #7da3d8;border-radius:18px;padding:1rem 1.15rem;margin:.6rem 0 1.2rem}
 .st-key-physical_freezer .stButton>button{min-height:82px!important;border:1px solid #80a5db!important;background:#fff!important;color:#0b2545!important;border-radius:10px!important;white-space:pre-line!important;box-shadow:0 2px 6px #14375a12}
 .st-key-physical_freezer .stButton>button:hover{border-color:#0d9488!important;background:#f0fdfa!important}
 .st-key-physical_freezer hr{border-color:#9db7d8}
 @media(max-width:640px){
 .st-key-physical_freezer{padding:.7rem .45rem!important}
 .st-key-physical_freezer [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:4px!important}
 .st-key-physical_freezer [data-testid="column"]{flex:1 1 0!important;width:0!important;min-width:0!important}
 .st-key-physical_freezer .stButton>button{min-height:75px!important;font-size:clamp(9px,2.7vw,12px)!important;padding:.3rem .15rem!important}
 }
 </style>""",unsafe_allow_html=True)
def hero(t,x):st.markdown(f'<div class="hero"><h2>{t}</h2><p>{x}</p></div>',unsafe_allow_html=True)

def inject_responsive_css():
    st.markdown("""
<style>
html,body{max-width:100%;overflow-x:hidden;-webkit-text-size-adjust:100%}
.main .block-container{width:100%;max-width:1500px;padding-left:clamp(.7rem,3vw,3rem);padding-right:clamp(.7rem,3vw,3rem)}
[data-testid="stSidebar"]{min-width:260px;max-width:320px}
[data-testid="stSidebar"] *,.stMarkdown,p,label,[data-testid="stWidgetLabel"]{overflow-wrap:anywhere;word-break:normal}
h1{font-size:clamp(1.55rem,4.5vw,2.6rem)!important;line-height:1.15!important}
h2{font-size:clamp(1.3rem,3.8vw,2rem)!important;line-height:1.2!important}
h3{font-size:clamp(1.08rem,3.2vw,1.55rem)!important}
.stButton>button,.stDownloadButton>button{min-height:44px;white-space:normal!important;overflow-wrap:anywhere;line-height:1.2}
[data-testid="stMetric"]{min-width:0}
[data-testid="stMetricValue"]{font-size:clamp(1.2rem,5vw,2rem)!important}
[data-testid="stDataFrame"],[data-testid="stTable"]{max-width:100%;overflow-x:auto}
img{max-width:100%;height:auto}
@media(max-width:640px){
 .main .block-container{padding:.75rem .6rem 4rem!important}
 [data-testid="stSidebar"]{width:min(86vw,320px)!important;min-width:min(86vw,320px)!important;max-width:min(86vw,320px)!important}
 [data-testid="column"]{width:100%!important;flex:1 1 100%!important;min-width:100%!important}
 div[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.5rem!important}
 .stButton,.stDownloadButton,.stButton>button,.stDownloadButton>button{width:100%!important}
 .stButton>button,.stDownloadButton>button{font-size:.94rem!important;padding:.55rem .6rem!important}
 [role="radiogroup"]{flex-wrap:wrap!important}
 [data-baseweb="tab-list"]{overflow-x:auto!important;flex-wrap:nowrap!important}
 [data-baseweb="tab"]{flex:0 0 auto!important;white-space:nowrap!important}
 .st-key-box_position_grid [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:2px!important}
 .st-key-box_position_grid [data-testid="column"]{width:auto!important;flex:1 1 0!important;min-width:0!important}
 .st-key-box_position_grid button{padding:0!important;min-height:32px!important;font-size:9px!important;letter-spacing:-.6px!important}
 input,textarea,select{font-size:16px!important}
}
@media(max-width:390px){
 h1{font-size:1.48rem!important}
 h2{font-size:1.24rem!important}
 [data-testid="stSidebar"]{width:88vw!important;min-width:88vw!important;max-width:88vw!important}
}
</style>
""", unsafe_allow_html=True)
