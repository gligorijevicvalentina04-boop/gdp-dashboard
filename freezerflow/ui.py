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
def hero(t,x):st.markdown(f'<div class="hero"><h2>{t}</h2><p>{x}</p></div>',unsafe_allow_html=True)
