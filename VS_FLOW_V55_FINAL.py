import re, time, math
from pathlib import Path
from typing import Optional, Dict, List, Tuple

import numpy as np
import pandas as pd
import requests
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None

APP = "VS FLOW INDIA"
VERSION = "V55"
BASE = Path(__file__).resolve().parent
LOGO = BASE / "vs_flow_logo.png"
LOCAL_UNIVERSE = BASE / "data" / "india_universe.csv"

st.set_page_config(
    page_title="VS FLOW INDIA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# THEME
# =========================
st.markdown("""
<style>
:root{
 --bg:#030914; --bg2:#061321; --panel:#081a2b; --panel2:#0b2136;
 --line:#164461; --cyan:#11dfff; --blue:#4d8dff; --violet:#9b5cff;
 --pink:#ff3ba7; --green:#00e676; --red:#ff4058; --gold:#ffc857;
 --text:#f5f8ff; --muted:#91a8bb;
}
html,body,[class*="css"]{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif}
.stApp{
 background:
 radial-gradient(circle at 80% -10%,rgba(18,90,140,.32),transparent 35%),
 radial-gradient(circle at 10% 0%,rgba(67,20,130,.22),transparent 28%),
 linear-gradient(180deg,#030914,#020711 70%,#02060d);
 color:var(--text);
}
[data-testid="stSidebar"]{
 background:linear-gradient(180deg,#04101d 0%,#020812 100%);
 border-right:1px solid #12354b;
}
[data-testid="stSidebar"] > div{padding-top:.7rem}
.block-container{max-width:1750px;padding:.75rem 1rem 2rem}
.stButton button{
 background:linear-gradient(180deg,#0b2439,#07182a)!important;
 border:1px solid #1b5273!important;color:#eef8ff!important;
 border-radius:10px!important;font-weight:800!important;
}
.stButton button:hover{border-color:var(--cyan)!important;box-shadow:0 0 16px rgba(17,223,255,.15)}
.stTextInput input,.stSelectbox div[data-baseweb="select"]>div,
.stTextArea textarea,.stNumberInput input{
 background:#04101c!important;color:#f3f8ff!important;
 border:1px solid #1a4662!important;border-radius:9px!important;
}
[data-testid="stDataFrame"]{border:1px solid #153e59;border-radius:12px;overflow:hidden}
.vs-brand{font-size:24px;font-weight:950;letter-spacing:.3px}
.vs-brand .india{color:var(--cyan)}
.vs-sub{font-size:10px;color:var(--cyan);letter-spacing:2px;font-weight:800}
.logo-wrap{padding:4px 2px 10px}
.logo-wrap img{border-radius:16px;border:1px solid #204c69;box-shadow:0 0 24px rgba(0,218,255,.10)}
.hero{
 background:linear-gradient(120deg,#071a2d 0%,#06182a 48%,#081d31 100%);
 border:1px solid #1c4d6a;border-radius:20px;padding:22px 25px 16px;
 box-shadow:0 16px 50px rgba(0,0,0,.28);margin-bottom:14px
}
.hero h1{margin:0;font-size:39px;font-weight:950;line-height:1}
.hero p{margin:9px 0 0;color:#8fb9d4;font-size:13px}
.gradient{height:4px;border-radius:9px;margin-top:17px;
 background:linear-gradient(90deg,#00e5ff,#4d8dff,#9b5cff,#ff3ba7,#ff7a18,#ffd22e)}
.section{font-size:21px;font-weight:950;margin:18px 0 10px}
.section small{font-size:11px;color:var(--muted);font-weight:600;margin-left:7px}
