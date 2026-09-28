import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    .stApp{background:linear-gradient(180deg,#f8fbff 0%,#f2f6fb 100%)}
    .block-container{max-width:1450px;padding-top:3.8rem;padding-bottom:4rem}
    [data-testid="stSidebar"]{background:linear-gradient(180deg,#07182d,#0b2545)}
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] p{color:#f8fafc}
    [data-testid="stSidebar"] div.stButton>button{
      background:#102c4c;color:#eaf4ff;border:1px solid #244665
    }
    [data-testid="stSidebar"] div.stButton>button:hover{
      background:#17466f;color:white;border-color:#38bdf8
    }
    div.stButton>button{border-radius:12px;font-weight:650;min-height:42px}
    .hero{padding:1.6rem 1.8rem;border-radius:24px;background:linear-gradient(135deg,#0b2545,#0879ae);
      box-shadow:0 16px 42px rgba(15,23,42,.10);margin-bottom:1.4rem}
    .hero h2{color:white;margin:0}.hero p{color:#dff4ff;margin:.5rem 0 0}
    .crumb{display:inline-block;padding:.45rem .8rem;border-radius:999px;background:#e0f2fe;color:#075985;
      font-weight:700;margin:.2rem .25rem .8rem 0}
    .slot{border-radius:11px;text-align:center;padding:.55rem .05rem;font-weight:800;border:1px solid #d8e2ec}
    .occupied{background:#dcfce7;color:#166534}.empty{background:#fff;color:#94a3b8}
    </style>""", unsafe_allow_html=True)

def hero(title, text):
    st.markdown(f'<div class="hero"><h2>{title}</h2><p>{text}</p></div>',unsafe_allow_html=True)
