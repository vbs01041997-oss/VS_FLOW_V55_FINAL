
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
.card{
 background:linear-gradient(145deg,#0a2034,#061522);border:1px solid #17425e;
 border-radius:14px;padding:14px;min-height:104px;box-shadow:inset 0 1px rgba(255,255,255,.025)
}
.card .label{font-size:11px;color:#9bb3c7;font-weight:800}
.card .value{font-size:24px;font-weight:950;margin:6px 0}
.up{color:var(--green)} .down{color:var(--red)} .flat{color:#b7c7d4}
.panel{
 background:rgba(7,22,36,.94);border:1px solid #17415d;border-radius:15px;
 padding:14px;box-shadow:0 8px 28px rgba(0,0,0,.13)
}
.pill{display:inline-block;border-radius:999px;padding:5px 9px;font-size:10px;font-weight:900;
 border:1px solid #285675;background:#082237;color:#a8ddf2;margin-right:4px}
.pill.green{border-color:#0a704c;background:#062b20;color:#54ffad}
.pill.red{border-color:#6f2030;background:#2b0a13;color:#ff8a99}
.pill.gold{border-color:#775b16;background:#2b2206;color:#ffd86c}
.metric{
 border:1px solid #17415d;border-radius:12px;background:#071a2c;padding:12px
}
.metric .k{font-size:10px;color:#8ea7ba;font-weight:800}
.metric .v{font-size:22px;font-weight:950;margin-top:4px}
.scorebar{height:9px;border-radius:20px;background:#0b2032;overflow:hidden;border:1px solid #173c55}
.scorebar > div{height:100%;background:linear-gradient(90deg,#ff4058,#ffc857,#00e676)}
.note{
 border-left:3px solid var(--cyan);background:#061b2d;padding:10px 12px;border-radius:8px;
 color:#a9c4d7;font-size:12px
}
.side-note{font-size:10px;line-height:1.5;color:#6f879a;border-top:1px solid #12354b;margin-top:15px;padding-top:13px}
hr{border-color:#14374f!important}

.setup-card{background:linear-gradient(145deg,#091e31,#061321);border:1px solid #174c69;border-radius:14px;padding:14px 16px;margin:8px 0;box-shadow:0 8px 26px rgba(0,0,0,.18)}
.setup-top{display:flex;gap:7px;align-items:center;font-size:18px;margin-bottom:10px}.setup-top b{margin-right:auto}
.setup-grid{display:grid;grid-template-columns:repeat(6,minmax(90px,1fr));gap:8px}.setup-grid div{border:1px solid #153d56;border-radius:9px;padding:8px;background:#061827}.setup-grid span,.trade-line span{display:block;color:#7691a5;font-size:9px;font-weight:800}.setup-grid b{font-size:11px}.trade-line{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px;padding-top:10px;border-top:1px solid #14374f}.trade-line span{display:inline-block}.trade-line b{color:#f5f8ff;font-size:12px;margin-left:4px}
.regime{font-size:30px;font-weight:950;letter-spacing:.5px}.heat{border:1px solid #17415d;border-radius:11px;padding:10px;background:#071a2c;margin:4px 0}.heat .v{font-weight:900;font-size:16px}.heat .s{font-size:10px;color:#8199ac}
@media(max-width:900px){.setup-grid{grid-template-columns:repeat(2,1fr)}.trade-line{grid-template-columns:repeat(2,1fr)}}
.owner-badge{position:absolute;right:18px;top:16px;background:linear-gradient(135deg,#071b2c,#0b2740);border:1px solid #1d6b8d;border-radius:999px;padding:8px 14px;color:#ffffff;font-size:14px;font-weight:950;letter-spacing:.3px;box-shadow:0 6px 20px rgba(0,0,0,.25)}
.click-hint{font-size:10px;color:#6f879a;margin-top:4px}
.action-card{background:linear-gradient(145deg,#091e31,#061321);border:1px solid #174c69;border-radius:14px;padding:14px 16px;min-height:90px}
</style>
""", unsafe_allow_html=True)

# =========================
# DATA UNIVERSE
# =========================
INDEXES = {
 "^NSEI":"NIFTY 50", "^NSEBANK":"NIFTY BANK", "^CNX100":"NIFTY 100",
 "^CNX200":"NIFTY 200", "^CNX500":"NIFTY 500", "^CNXSMALLCAP":"NIFTY Smallcap 100",
 "^BSESN":"SENSEX", "BSEBANK":"BSE BANKEX", "^INDIAVIX":"INDIA VIX",
 "^CNXIT":"NIFTY IT", "^CNXPHARMA":"NIFTY PHARMA", "^CNXAUTO":"NIFTY AUTO",
 "^CNXMETAL":"NIFTY METAL", "^CNXFMCG":"NIFTY FMCG", "^CNXREALTY":"NIFTY REALTY",
 "^CNXENERGY":"NIFTY ENERGY", "^CNXFIN":"FINNIFTY", "^NSMIDCP":"NIFTY NEXT 50",
 "^NSEMDCP50":"NIFTY MIDCAP SELECT",
}

# The OB + Trend scanner uses these key benchmarks alongside the 100-stock universe.
OB_INDEXES = {
 "^NSEI":"NIFTY 50",
 "^NSEBANK":"BANK NIFTY",
 "^BSESN":"SENSEX",
 "^CNXFIN":"FINNIFTY",
 "BSEBANK":"BANKEX",
 "^NSMIDCP":"NIFTY NEXT 50",
 "^CNX100":"NIFTY 100",
}
OB_INDEX_TICKERS = set(OB_INDEXES)

CORE = {
 "RELIANCE":"Reliance Industries","TCS":"Tata Consultancy Services","HDFCBANK":"HDFC Bank",
 "ICICIBANK":"ICICI Bank","INFY":"Infosys","SBIN":"State Bank of India","BHARTIARTL":"Bharti Airtel",
 "ITC":"ITC","LT":"Larsen & Toubro","KOTAKBANK":"Kotak Mahindra Bank","AXISBANK":"Axis Bank",
 "HINDUNILVR":"Hindustan Unilever","BAJFINANCE":"Bajaj Finance","MARUTI":"Maruti Suzuki",
 "SUNPHARMA":"Sun Pharmaceutical","TITAN":"Titan Company","ASIANPAINT":"Asian Paints",
 "HCLTECH":"HCL Technologies","WIPRO":"Wipro","NTPC":"NTPC","POWERGRID":"Power Grid",
 "ONGC":"ONGC","TATASTEEL":"Tata Steel","JSWSTEEL":"JSW Steel","ADANIENT":"Adani Enterprises",
 "ADANIPORTS":"Adani Ports","COALINDIA":"Coal India","M&M":"Mahindra & Mahindra",
 "TECHM":"Tech Mahindra","ULTRACEMCO":"UltraTech Cement","NESTLEIND":"Nestle India",
 "CIPLA":"Cipla","DRREDDY":"Dr Reddy's Laboratories","EICHERMOT":"Eicher Motors",
 "HEROMOTOCO":"Hero MotoCorp","BAJAJFINSV":"Bajaj Finserv","TRENT":"Trent","BEL":"Bharat Electronics",
 "HAL":"Hindustan Aeronautics","ETERNAL":"Eternal","INDUSINDBK":"IndusInd Bank",
 "BANKBARODA":"Bank of Baroda","CANBK":"Canara Bank","PNB":"Punjab National Bank",
 "IDFCFIRSTB":"IDFC First Bank","IRCTC":"IRCTC","DLF":"DLF","IOC":"Indian Oil",
 "BPCL":"Bharat Petroleum","HINDALCO":"Hindalco","VEDL":"Vedanta","SAIL":"Steel Authority of India",
 "NMDC":"NMDC","GAIL":"GAIL India","DMART":"Avenue Supermarts","PIDILITIND":"Pidilite Industries",
 "SIEMENS":"Siemens India","ABB":"ABB India","INDIGO":"InterGlobe Aviation","TATAMOTORS":"Tata Motors",
 "TVSMOTOR":"TVS Motor","MOTHERSON":"Samvardhana Motherson","APOLLOHOSP":"Apollo Hospitals",
 "DIVISLAB":"Divi's Laboratories","MAXHEALTH":"Max Healthcare","DABUR":"Dabur India",
 "BRITANNIA":"Britannia Industries","GODREJCP":"Godrej Consumer Products","HAVELLS":"Havells India",
 "POLYCAB":"Polycab India","PERSISTENT":"Persistent Systems","COFORGE":"Coforge","LTIM":"LTIMindtree",
 "MPHASIS":"Mphasis","BSE":"BSE Ltd","CDSL":"CDSL","MCX":"Multi Commodity Exchange",
 "IRFC":"IRFC","RVNL":"Rail Vikas Nigam","JIOFIN":"Jio Financial Services","TATAPOWER":"Tata Power",
 "INDIANB":"Indian Bank","FEDERALBNK":"Federal Bank","YESBANK":"Yes Bank","IDBI":"IDBI Bank",
 "BAJAJ-AUTO":"Bajaj Auto","SHRIRAMFIN":"Shriram Finance","TATACONSUM":"Tata Consumer Products","JINDALSTEL":"Jindal Steel & Power",
 "HINDZINC":"Hindustan Zinc","ADANIPOWER":"Adani Power","INDHOTEL":"Indian Hotels","VBL":"Varun Beverages",
 "ZYDUSLIFE":"Zydus Lifesciences","TORNTPHARM":"Torrent Pharmaceuticals","LUPIN":"Lupin","ABBOTINDIA":"Abbott India",
 "ICICIGI":"ICICI Lombard General Insurance","SBILIFE":"SBI Life Insurance","HDFCLIFE":"HDFC Life Insurance"
}

def _norm_col(df, names):
    lower={str(c).strip().lower():c for c in df.columns}
    for n in names:
        if n.lower() in lower: return lower[n.lower()]
    return None

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_nse_equity():
    urls=[
        "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
        "https://archives.nseindia.com/content/equities/EQUITY_L.csv",
    ]
    for url in urls:
        try:
            r=requests.get(url,timeout=15,headers={"User-Agent":"Mozilla/5.0","Accept":"text/csv,*/*"})
            r.raise_for_status()
            df=pd.read_csv(pd.io.common.BytesIO(r.content))
            sym=_norm_col(df,["SYMBOL","Symbol"])
            name=_norm_col(df,["NAME OF COMPANY","COMPANY NAME","Company Name"])
            isin=_norm_col(df,["ISIN NUMBER","ISIN"])
            series=_norm_col(df,["SERIES","Series"])
            if sym:
                out=pd.DataFrame({
                    "symbol":df[sym].astype(str).str.strip().str.upper(),
                    "name":df[name].astype(str).str.strip() if name else df[sym].astype(str),
                    "exchange":"NSE",
                    "series":df[series].astype(str).str.strip().str.upper() if series else "EQ",
                    "isin":df[isin].astype(str).str.strip() if isin else ""
                })
                out=out[(out["symbol"]!="NAN") & (out["series"].isin(["EQ","BE","SM","ST","SZ","BZ","M"]))].copy()
                return out.drop_duplicates("symbol")
        except Exception:
            pass
    return pd.DataFrame(columns=["symbol","name","exchange","series","isin"])

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_bse_equity():
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/134 Safari/537.36",
        "Accept":"application/json, text/plain, */*","Referer":"https://www.bseindia.com/"
    }
    url="https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w"
    params={"scripcode":"","Group":"","industry":"","segment":"Equity","status":"Active"}
    try:
        r=requests.get(url,params=params,headers=headers,timeout=18)
        r.raise_for_status()
        data=r.json()
        if isinstance(data,dict):
            for key in ["Table","Data","data","Table1"]:
                if isinstance(data.get(key),list):
                    data=data[key]; break
        if not isinstance(data,list): return pd.DataFrame()
        df=pd.DataFrame(data)
        if df.empty: return df
        sym=_norm_col(df,["Scrip_Id","ScripID","Scrip Id","Security Code","Symbol","Scrip_Name"])
        name=_norm_col(df,["Scrip_Name","Scrip Name","Company Name","Security Name","Issuer Name"])
        code=_norm_col(df,["ScripCode","Scrip Code","Security Code"])
        isin=_norm_col(df,["ISIN","ISIN_NO","ISIN Number"])
        group=_norm_col(df,["Group","Scrip Group"])
        out=pd.DataFrame({
            "symbol":df[sym].astype(str).str.strip().str.upper() if sym else "",
            "name":df[name].astype(str).str.strip() if name else (df[sym].astype(str) if sym else ""),
            "exchange":"BSE",
            "series":df[group].astype(str).str.strip().str.upper() if group else "EQ",
            "isin":df[isin].astype(str).str.strip() if isin else "",
            "bse_code":df[code].astype(str).str.replace(r"\.0$","",regex=True).str.strip() if code else ""
        })
        out=out[out["symbol"].ne("") & out["symbol"].ne("NAN")].drop_duplicates("isin" if out["isin"].ne("").any() else "symbol")
        return out
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=86400, show_spinner=False)
def load_local():
    if LOCAL_UNIVERSE.exists():
        try:
            df=pd.read_csv(LOCAL_UNIVERSE)
            if "symbol" in df.columns:
                for c in ["name","exchange","series","isin"]:
                    if c not in df.columns: df[c]=""
                return df[["symbol","name","exchange","series","isin"]].drop_duplicates()
        except Exception:
            pass
    return pd.DataFrame()

@st.cache_data(ttl=86400, show_spinner=False)
def load_universe():
    nse=fetch_nse_equity()
    bse=fetch_bse_equity()
    local=load_local()
    parts=[x for x in [nse,bse,local] if not x.empty]
    if parts:
        df=pd.concat(parts,ignore_index=True)
    else:
        df=pd.DataFrame(columns=["symbol","name","exchange","series","isin"])
    # Core fallback / guarantee searchable
    core=pd.DataFrame([{"symbol":s,"name":n,"exchange":"NSE","series":"EQ","isin":""} for s,n in CORE.items()])
    df=pd.concat([df,core],ignore_index=True)
    df["symbol"]=df["symbol"].astype(str).str.strip().str.upper()
    df["name"]=df["name"].astype(str).replace("NAN","").str.strip()
    df["exchange"]=df["exchange"].fillna("NSE").astype(str).str.upper()
    df=df[df["symbol"].str.len().between(1,30)].copy()
    # Deduplicate by exchange+symbol first, then keep best named row
    df=df.sort_values(["name"],na_position="last").drop_duplicates(["exchange","symbol"])
    return df.reset_index(drop=True)

UNIV=load_universe()

# =========================
# MARKET DATA
# =========================
def yf_ticker(symbol, exchange="NSE"):
    s=str(symbol).strip().upper()
    if s in OB_INDEX_TICKERS or s.startswith("^") or "=" in s: return s
    if s.endswith(".NS") or s.endswith(".BO"): return s
    return s + (".BO" if str(exchange).upper()=="BSE" else ".NS")

@st.cache_data(ttl=180, show_spinner=False)
def history(ticker, period="6mo", interval="1d"):
    if yf is None: return pd.DataFrame()
    try:
        d=yf.download(ticker,period=period,interval=interval,auto_adjust=False,progress=False,threads=False)
        if d is None or d.empty: return pd.DataFrame()
        if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
        return d.dropna(how="all")
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=120, show_spinner=False)
def quote(ticker):
    d=history(ticker,"5d","1d")
    if d.empty or "Close" not in d: return None
    c=d["Close"].dropna()
    if len(c)==0: return None
    price=float(c.iloc[-1]); prev=float(c.iloc[-2]) if len(c)>1 else price
    return {"price":price,"chg":(price/prev-1)*100 if prev else 0}

def rsi(series, n=14):
    delta=series.diff()
    gain=delta.clip(lower=0).ewm(alpha=1/n,adjust=False).mean()
    loss=-delta.clip(upper=0).ewm(alpha=1/n,adjust=False).mean()
    rs=gain/loss.replace(0,np.nan)
    return 100-(100/(1+rs))

def atr(df,n=14):
    h,l,c=df["High"],df["Low"],df["Close"]
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def technical_snapshot(ticker):
    d=history(ticker,"1y","1d")
    if d.empty or len(d)<60: return None
    c=d["Close"].astype(float); v=d["Volume"].astype(float)
    e20=c.ewm(span=20,adjust=False).mean(); e50=c.ewm(span=50,adjust=False).mean(); e200=c.ewm(span=200,adjust=False).mean()
    rr=rsi(c).iloc[-1]; at=atr(d).iloc[-1]
    price=float(c.iloc[-1]); high52=float(d["High"].tail(252).max()); low52=float(d["Low"].tail(252).min())
    vol=float(v.iloc[-1]); v20=float(v.tail(20).mean()) if v.tail(20).mean() else vol
    trend="BULLISH" if e20.iloc[-1]>e50.iloc[-1] else ("BEARISH" if e20.iloc[-1]<e50.iloc[-1] else "FLAT")
    return {
        "price":price,"ema20":float(e20.iloc[-1]),"ema50":float(e50.iloc[-1]),"ema200":float(e200.iloc[-1]),
        "rsi":float(rr) if pd.notna(rr) else np.nan,"atr":float(at) if pd.notna(at) else np.nan,
        "high52":high52,"low52":low52,"vol_ratio":vol/v20 if v20 else 1,
        "trend":trend,"dist_high":(high52-price)/high52*100 if high52 else np.nan,
        "dist_low":(price-low52)/low52*100 if low52 else np.nan
    }

def selection_score(s):
    # Transparent research score, not probability.
    score=0; reasons=[]
    if s["trend"]=="BULLISH": score+=25; reasons.append("EMA20 > EMA50")
    elif s["trend"]=="BEARISH": score+=25; reasons.append("EMA20 < EMA50")
    if s["price"]>s["ema200"] if pd.notna(s["ema200"]) else False: score+=15; reasons.append("Above EMA200")
    if 45<=s["rsi"]<=68: score+=15; reasons.append("Healthy RSI")
    elif s["rsi"]>70: score+=5; reasons.append("RSI hot")
    if s["vol_ratio"]>=1.5: score+=20; reasons.append("Volume expansion")
    elif s["vol_ratio"]>=1.15: score+=10; reasons.append("Volume above average")
    if s["dist_high"]<=8: score+=15; reasons.append("Near 52W high")
    return min(score,100), reasons

# =========================
# VS FLOW PROXY
# =========================
def structure_score(d):
    if d.empty or len(d)<20: return {"score":0,"side":"WAIT","reason":"Insufficient data"}
    c=d["Close"].astype(float); h=d["High"].astype(float); l=d["Low"].astype(float)
    ema20=c.ewm(span=20,adjust=False).mean().iloc[-1]
    ema50=c.ewm(span=50,adjust=False).mean().iloc[-1] if len(c)>=50 else ema20
    recent_high=float(h.tail(20).max()); recent_low=float(l.tail(20).min())
    price=float(c.iloc[-1]); prev20_high=float(h.iloc[-21:-1].max()) if len(h)>21 else recent_high
    prev20_low=float(l.iloc[-21:-1].min()) if len(l)>21 else recent_low
    up=price>ema20>ema50
    down=price<ema20<ema50
    score=0; side="WAIT"; reasons=[]
    if up: score+=1; side="BUY"; reasons.append("HTF bullish structure")
    if down: score+=1; side="SELL"; reasons.append("HTF bearish structure")
    if price>=prev20_high: score+=1; side="BUY"; reasons.append("Breakout")
    if price<=prev20_low: score+=1; side="SELL"; reasons.append("Breakdown")
    vol=d["Volume"].astype(float); vr=float(vol.iloc[-1]/vol.tail(20).mean()) if vol.tail(20).mean() else 1
    if vr>=1.4: score+=1; reasons.append("Volume expansion")
    # displacement proxy
    move=abs(price/float(c.iloc[-5])-1)*100 if len(c)>=5 else 0
    if move>=2: score+=1; reasons.append("Displacement")
    return {"score":min(score,5),"side":side,"reason":", ".join(reasons) or "No clear alignment"}

def mtf_setup(ticker):
    frames=[]
    configs=[("4H","60d","1h"),("1H","30d","1h"),("15M","30d","15m"),("5M","7d","5m")]
    for label,period,interval in configs:
        d=history(ticker,period,interval)
        if label=="4H" and not d.empty:
            # resample to 4H using OHLCV
            d=d.copy()
            d.index=pd.to_datetime(d.index)
            d=d.resample("4h").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
        if d.empty:
            frames.append({"tf":label,"status":"NO DATA","side":"WAIT","detail":"Provider unavailable"})
            continue
        x=structure_score(d)
        frames.append({"tf":label,"status":f'{x["score"]}/5',"side":x["side"],"detail":x["reason"]})
    valid=[x for x in frames if x["status"]!="NO DATA"]
    buy=sum(x["side"]=="BUY" for x in valid); sell=sum(x["side"]=="SELL" for x in valid)
    if buy>=3 and buy>sell: overall="BUY"
    elif sell>=3 and sell>buy: overall="SELL"
    else: overall="WAIT"
    return frames,overall



# =========================
# VS FLOW CORE SMC ENGINE
# =========================
def core_structure(x, n=5):
    if len(x) < n*2+3: return "WAIT"
    hi=x.High.iloc[-n-1:-1].max(); lo=x.Low.iloc[-n-1:-1].min(); last=x.iloc[-1]
    if last.Close > hi: return "BULL BOS"
    if last.Close < lo: return "BEAR BOS"
    return "WAIT"

def core_liquidity_sweep(x, n=5):
    if len(x) < n+3: return "WAIT"
    hi=x.High.iloc[-n-1:-1].max(); lo=x.Low.iloc[-n-1:-1].min(); last=x.iloc[-1]
    if last.High > hi and last.Close < hi: return "BSL SWEPT"
    if last.Low < lo and last.Close > lo: return "SSL SWEPT"
    return "WAIT"

def core_order_block(x):
    if len(x) < 25: return None
    for i in range(len(x)-2, max(2,len(x)-30), -1):
        cur=x.iloc[i]; prev=x.iloc[i-1]; rng=max(float(cur.High-cur.Low),1e-9); body=abs(float(cur.Close-cur.Open))
        if body/rng < 0.55: continue
        if cur.Close>cur.Open and prev.Close<prev.Open and cur.Close>prev.High:
            return {"side":"BUY","type":"BULL OB","low":float(prev.Low),"high":float(prev.Open)}
        if cur.Close<cur.Open and prev.Close>prev.Open and cur.Close<prev.Low:
            return {"side":"SELL","type":"BEAR OB","low":float(prev.Open),"high":float(prev.High)}
    return None

def core_fvg(x):
    if len(x)<5: return None
    for i in range(len(x)-1,1,-1):
        a,b,c=x.iloc[i-2],x.iloc[i-1],x.iloc[i]
        if c.Low>a.High: return {"side":"BUY","type":"BULL FVG"}
        if c.High<a.Low: return {"side":"SELL","type":"BEAR FVG"}
    return None

def core_analyze(ticker, name=""):
    h1=history(ticker,"6mo","1h"); m15=history(ticker,"60d","15m"); m5=history(ticker,"30d","5m")
    base={"Symbol":ticker,"Name":name or ticker,"4H OB":"WAIT","1H Sweep":"WAIT","1H BOS":"WAIT","15M FVG":"WAIT","5M Trigger":"WAIT","Score":"0/5","Signal":"WAIT","Entry":"","SL":"","TP":"","RR":"","Chart Tally":"PENDING"}
    if h1.empty or m15.empty or m5.empty: base["Signal"]="NO DATA"; return base
    h4=h1.copy(); h4.index=pd.to_datetime(h4.index); h4=h4.resample("4h").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
    ob=core_order_block(h4)
    if not ob: return base
    side=ob["side"]; sw=core_liquidity_sweep(h1); bos=core_structure(h1); fv=core_fvg(m15); tr=core_structure(m5)
    base.update({"4H OB":ob["type"],"1H Sweep":sw,"1H BOS":bos,"15M FVG":fv["type"] if fv else "WAIT","5M Trigger":("5M BULL BOS" if tr=="BULL BOS" else "5M BEAR BOS" if tr=="BEAR BOS" else "WAIT")})
    checks=[True,(side=="BUY" and bos=="BULL BOS") or (side=="SELL" and bos=="BEAR BOS"),(fv is not None and fv["side"]==side),(side=="BUY" and tr=="BULL BOS") or (side=="SELL" and tr=="BEAR BOS")]
    core_score=sum(checks); sweep_ok=(side=="BUY" and sw=="SSL SWEPT") or (side=="SELL" and sw=="BSL SWEPT"); score=core_score+(1 if sweep_ok else 0)
    base["Score"]=f"{score}/5"
    if core_score>=4:
        price=float(m5.Close.iloc[-1]); sl=ob["low"] if side=="BUY" else ob["high"]; risk=price-sl if side=="BUY" else sl-price
        if risk>0:
            base.update({"Signal":("A+ BUY" if side=="BUY" else "A+ SELL") if score==5 else ("SETUP BUY" if side=="BUY" else "SETUP SELL"),"Entry":round(price,4),"SL":round(sl,4),"TP":round(price+2*risk if side=="BUY" else price-2*risk,4),"RR":"1:2","Chart Tally":"COMPLETE" if score==5 else "PENDING"})
    return base


# =========================
# SMC 4H -> 5M SCALP — separate setup
# =========================
def smc_scalp_analyze(ticker, name=""):
    """Research proxy for the user's 4H HTF -> 5M execution model.
    Sequence: 4H direction/location -> 50% equilibrium -> 5M liquidity sweep -> MSS -> FVG -> retest.
    It intentionally remains separate from VS FLOW Core Setup.
    """
    h4=history(ticker,"90d","1h")
    m5=history(ticker,"30d","5m")
    base={"Symbol":ticker,"Name":name or ticker,"4H Direction":"WAIT","4H Zone":"WAIT","5M Sweep":"WAIT","5M MSS":"WAIT","5M FVG":"WAIT","FVG Retest":"WAIT","Score":"0/6","Signal":"WAIT","Entry":"","SL":"","TP":"","RR":"1:2"}
    if h4.empty or m5.empty: base["Signal"]="NO DATA"; return base
    h4=h4.copy(); m5=m5.copy()
    for d in (h4,m5):
        d.index=pd.to_datetime(d.index)
        for c in ["Open","High","Low","Close","Volume"]: d[c]=pd.to_numeric(d[c],errors="coerce")
        d.dropna(subset=["Open","High","Low","Close"],inplace=True)
    h4c=h4.resample("4h").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
    if len(h4c)<12 or len(m5)<40: base["Signal"]="NO DATA"; return base
    # Use completed 4H candle as HTF reference, avoiding the currently forming candle.
    ref=h4c.iloc[-2]
    hh,ll,cc=float(ref.High),float(ref.Low),float(ref.Close)
    eq=(hh+ll)/2
    e20=h4c.Close.ewm(span=20,adjust=False).mean().iloc[-2]
    e50=h4c.Close.ewm(span=50,adjust=False).mean().iloc[-2]
    if e20>e50 and cc>eq: direction="BUY"
    elif e20<e50 and cc<eq: direction="SELL"
    else:
        direction="BUY" if cc>eq else "SELL" if cc<eq else "WAIT"
    zone="DISCOUNT" if cc<eq else "PREMIUM" if cc>eq else "EQUILIBRIUM"
    # HTF direction and location must agree for the preferred setup.
    zone_ok=(direction=="BUY" and zone=="DISCOUNT") or (direction=="SELL" and zone=="PREMIUM")
    # Recent 5M liquidity sweep: use prior 8-bar swing, then find a post-sweep structure shift.
    n=8
    prior=m5.iloc[-(n+18):-1] if len(m5)>n+18 else m5.iloc[:-1]
    if len(prior)<n+5: return base
    recent=m5.iloc[-25:].copy()
    swing_hi=float(recent.High.iloc[:-1].max()); swing_lo=float(recent.Low.iloc[:-1].min())
    sweep_idx=None; sweep_side=None
    for i in range(max(5,len(m5)-18),len(m5)):
        r=m5.iloc[i]
        before=m5.iloc[max(0,i-n):i]
        if len(before)<n: continue
        hi=float(before.High.max()); lo=float(before.Low.min())
        if float(r.Low)<lo and float(r.Close)>lo:
            sweep_idx=i; sweep_side="BUY"; break
        if float(r.High)>hi and float(r.Close)<hi:
            sweep_idx=i; sweep_side="SELL"; break
    sweep="SSL SWEPT" if sweep_side=="BUY" else "BSL SWEPT" if sweep_side=="SELL" else "WAIT"
    mss="WAIT"; fvg="WAIT"; retest="WAIT"; entry=None; slv=None; tp=None
    if sweep_idx is not None:
        post=m5.iloc[sweep_idx+1:]
        for j in range(sweep_idx+1,len(m5)):
            before=m5.iloc[max(sweep_idx+1,j-n):j]
            if len(before)<3: continue
            r=m5.iloc[j]
            hi=float(before.High.max()); lo=float(before.Low.min())
            if sweep_side=="BUY" and float(r.Close)>hi:
                mss="BULL MSS"; mss_idx=j; break
            if sweep_side=="SELL" and float(r.Close)<lo:
                mss="BEAR MSS"; mss_idx=j; break
        if mss!="WAIT":
            # Search for a 3-candle FVG created after MSS.
            for i in range(mss_idx+2,len(m5)):
                a,b,c=m5.iloc[i-2],m5.iloc[i-1],m5.iloc[i]
                if sweep_side=="BUY" and float(c.Low)>float(a.High):
                    fvg="BULL FVG"; fvg_low=float(a.High); fvg_high=float(c.Low); fvg_i=i; break
                if sweep_side=="SELL" and float(c.High)<float(a.Low):
                    fvg="BEAR FVG"; fvg_low=float(c.High); fvg_high=float(a.Low); fvg_i=i; break
            if fvg!="WAIT":
                # Retest = price trades back into the FVG after its creation, while closing in direction.
                for k in range(fvg_i+1,len(m5)):
                    r=m5.iloc[k]; lo=float(r.Low); hi=float(r.High); close=float(r.Close)
                    if sweep_side=="BUY" and lo<=fvg_high and hi>=fvg_low and close>=fvg_low:
                        retest="BULL FVG RETEST"; entry=close; slv=float(m5.Low.iloc[sweep_idx]); risk=entry-slv; tp=entry+2*risk if risk>0 else None; break
                    if sweep_side=="SELL" and hi>=fvg_low and lo<=fvg_high and close<=fvg_high:
                        retest="BEAR FVG RETEST"; entry=close; slv=float(m5.High.iloc[sweep_idx]); risk=slv-entry; tp=entry-2*risk if risk>0 else None; break
    checks=[direction in ("BUY","SELL"),zone_ok,(sweep_side==direction),(mss==("BULL MSS" if direction=="BUY" else "BEAR MSS")),(fvg==("BULL FVG" if direction=="BUY" else "BEAR FVG")),(retest.startswith("BULL") if direction=="BUY" else retest.startswith("BEAR"))]
    score=sum(checks)
    base.update({"4H Direction":direction,"4H Zone":zone,"5M Sweep":sweep,"5M MSS":mss,"5M FVG":fvg,"FVG Retest":retest,"Score":f"{score}/6"})
    if score>=5 and entry is not None and slv is not None and tp is not None and risk>0:
        base.update({"Signal":f"SMC SCALP {direction}","Entry":round(entry,4),"SL":round(slv,4),"TP":round(tp,4),"RR":"1:2"})
    elif score>=4:
        base["Signal"]=f"SMC SCALP {direction} — WATCH"
    return base

# =========================
# CLASSIC PRICE ACTION SETUP — user's established setup
# =========================
def classic_analyze(ticker, name=""):
    d=history(ticker,"1y","1d")
    base={"Symbol":ticker,"Name":name or ticker,"Key Level":"WAIT","Trendline":"WAIT","Breakout/Breakdown":"WAIT","Price Action":"WAIT","Candle Close":"WAIT","Score":"0/6","Signal":"WAIT","Entry":"","SL":"","TP":"","RR":"1:2"}
    if d.empty or len(d)<80:
        base["Signal"]="NO DATA"; return base
    d=d.copy()
    for c in ["Open","High","Low","Close","Volume"]: d[c]=pd.to_numeric(d[c],errors="coerce")
    d=d.dropna(subset=["Open","High","Low","Close"])
    if len(d)<60: base["Signal"]="NO DATA"; return base
    last=d.iloc[-1]; prev=d.iloc[-2]
    close=float(last.Close); op=float(last.Open); hi=float(last.High); lo=float(last.Low)
    body=abs(close-op); rng=max(hi-lo,1e-9)
    upper=hi-max(op,close); lower=min(op,close)-lo
    # Key levels: previous day + recent 20-day swing extremes.
    pdh=float(prev.High); pdl=float(prev.Low)
    rhi=float(d.High.iloc[-21:-1].max()); rlo=float(d.Low.iloc[-21:-1].min())
    tol=max(float((d.High-d.Low).tail(20).mean())*0.25, close*0.002)
    key=None; key_side=None
    if abs(close-rhi)<=tol or abs(hi-rhi)<=tol: key="NEAR 20D RESISTANCE"; key_side="SELL"
    if abs(close-rlo)<=tol or abs(lo-rlo)<=tol: key="NEAR 20D SUPPORT"; key_side="BUY"
    if abs(close-pdh)<=tol: key="NEAR PREV DAY HIGH"; key_side="SELL"
    if abs(close-pdl)<=tol: key="NEAR PREV DAY LOW"; key_side="BUY"
    # Breakout / breakdown with close confirmation.
    breakout=close>rhi and close>pdh
    breakdown=close<rlo and close<pdl
    if breakout: bd="BREAKOUT"
    elif breakdown: bd="BREAKDOWN"
    else: bd="WAIT"
    # Candle quality / price action.
    bull_rej=lower>body*1.5 and close>op and close>=lo+rng*0.65
    bear_rej=upper>body*1.5 and close<op and close<=hi-rng*0.65
    strong_bull=close>op and body/rng>=0.60
    strong_bear=close<op and body/rng>=0.60
    if bull_rej or strong_bull: pa="BULLISH PA"
    elif bear_rej or strong_bear: pa="BEARISH PA"
    else: pa="NEUTRAL"
    # Close confirmation: candle closes beyond the key level, not just wick.
    cc="BULL CLOSE CONFIRM" if breakout else "BEAR CLOSE CONFIRM" if breakdown else "WAIT"
    # Trendline proxy: regression slope of recent lows/highs, with price location.
    n=30; x=np.arange(n)
    lows=d.Low.tail(n).to_numpy(dtype=float); highs=d.High.tail(n).to_numpy(dtype=float)
    sl=np.polyfit(x,lows,1)[0]; sh=np.polyfit(x,highs,1)[0]
    low_line=np.polyval(np.polyfit(x,lows,1),n-1); high_line=np.polyval(np.polyfit(x,highs,1),n-1)
    trend="UP TRENDLINE" if sl>0 and close>=low_line-tol else "DOWN TRENDLINE" if sh<0 and close<=high_line+tol else "NO CLEAN TRENDLINE"
    # Directional scoring. Primary direction is breakout/breakdown; otherwise PA + trendline + key location.
    score=0; reasons=[]; side="WAIT"
    if breakout: score+=2; side="BUY"; reasons.append("breakout + close")
    elif breakdown: score+=2; side="SELL"; reasons.append("breakdown + close")
    if side=="WAIT" and key_side: side=key_side
    if side=="BUY" and key_side=="BUY": score+=1; reasons.append("support/key level")
    if side=="SELL" and key_side=="SELL": score+=1; reasons.append("resistance/key level")
    if side=="BUY" and sl>0: score+=1; reasons.append("rising trendline")
    if side=="SELL" and sh<0: score+=1; reasons.append("falling trendline")
    if side=="BUY" and pa=="BULLISH PA": score+=1; reasons.append("bullish price action")
    if side=="SELL" and pa=="BEARISH PA": score+=1; reasons.append("bearish price action")
    if side=="BUY" and cc.startswith("BULL"): score+=1; reasons.append("candle close confirmation")
    if side=="SELL" and cc.startswith("BEAR"): score+=1; reasons.append("candle close confirmation")
    score=min(score,6)
    if score>=4 and side in ("BUY","SELL"):
        entry=close
        # Structure-based SL: recent swing / candle extreme.
        if side=="BUY":
            slv=min(lo,rlo,pdl)
            risk=entry-slv
            tp=entry+2*risk if risk>0 else entry
        else:
            slv=max(hi,rhi,pdh)
            risk=slv-entry
            tp=entry-2*risk if risk>0 else entry
        if risk>0:
            base.update({"Signal":f"CLASSIC {side}","Entry":round(entry,4),"SL":round(slv,4),"TP":round(tp,4),"RR":"1:2"})
    base.update({"Key Level":key or "WAIT","Trendline":trend,"Breakout/Breakdown":bd,"Price Action":pa,"Candle Close":cc,"Score":f"{score}/6"})
    return base

# =========================
# STRATEGY LAB — 5 complementary lenses
# =========================
def _strategy_daily(ticker):
    d=history(ticker,"1y","1d")
    if d.empty or len(d)<80: return pd.DataFrame()
    d=d.copy();
    for c in ["Open","High","Low","Close","Volume"]: d[c]=pd.to_numeric(d[c],errors="coerce")
    return d.dropna(subset=["Open","High","Low","Close"])

def strategy_smc(d):
    if d.empty: return {"score":0,"bias":"WAIT","reason":"No data"}
    # Existing VS FLOW SMC engine is the primary lens; daily structure proxy adds context.
    x=core_order_block(d)
    bos=core_structure(d)
    sw=core_liquidity_sweep(d)
    side=x.get("side") if x else None
    score=0; reasons=[]
    if x: score+=1; reasons.append(x["type"])
    if side=="BUY" and bos=="BULL BOS" or side=="SELL" and bos=="BEAR BOS": score+=1; reasons.append(bos)
    if side=="BUY" and sw=="SSL SWEPT" or side=="SELL" and sw=="BSL SWEPT": score+=1; reasons.append(sw)
    c=d.Close; e20=c.ewm(span=20,adjust=False).mean().iloc[-1]; e50=c.ewm(span=50,adjust=False).mean().iloc[-1]
    if side=="BUY" and e20>e50 or side=="SELL" and e20<e50: score+=1; reasons.append("EMA structure aligned")
    bias="BUY" if side=="BUY" and score>=2 else "SELL" if side=="SELL" and score>=2 else "WAIT"
    return {"score":min(score,5),"bias":bias,"reason":", ".join(reasons) or "No clear SMC alignment"}

def strategy_price_action(d):
    if len(d)<30: return {"score":0,"bias":"WAIT","reason":"Insufficient data"}
    last=d.iloc[-1]; rng=max(float(last.High-last.Low),1e-9); body=abs(float(last.Close-last.Open))
    recent_hi=float(d.High.iloc[-21:-1].max()); recent_lo=float(d.Low.iloc[-21:-1].min())
    upper=float(last.High-max(last.Open,last.Close)); lower=float(min(last.Open,last.Close)-last.Low)
    score=0; bias="WAIT"; reasons=[]
    if float(last.Close)>recent_hi: score+=2; bias="BUY"; reasons.append("Key-high acceptance")
    elif float(last.Close)<recent_lo: score+=2; bias="SELL"; reasons.append("Key-low acceptance")
    elif lower>body*1.5 and float(last.Close)>float(last.Open): score+=2; bias="BUY"; reasons.append("Bullish rejection")
    elif upper>body*1.5 and float(last.Close)<float(last.Open): score+=2; bias="SELL"; reasons.append("Bearish rejection")
    if rng>float((d.High-d.Low).tail(20).mean())*1.2: score+=1; reasons.append("Range expansion")
    # Location near prior extremes
    if abs(float(last.Close)-recent_hi)/max(recent_hi,1e-9)<.01 and bias=="BUY": score+=1; reasons.append("Near prior high")
    if abs(float(last.Close)-recent_lo)/max(recent_lo,1e-9)<.01 and bias=="SELL": score+=1; reasons.append("Near prior low")
    return {"score":min(score,4),"bias":bias,"reason":", ".join(reasons) or "No clean key-level reaction"}

def strategy_breakout_retest(d):
    if len(d)<40: return {"score":0,"bias":"WAIT","reason":"Insufficient data"}
    c=d.Close; h=d.High; l=d.Low; last=float(c.iloc[-1]); prev20h=float(h.iloc[-21:-1].max()); prev20l=float(l.iloc[-21:-1].min())
    atrv=float(atr(d).iloc[-1]) if pd.notna(atr(d).iloc[-1]) else 0
    score=0; bias="WAIT"; reasons=[]
    recent5=d.tail(5); max5=float(recent5.High.max()); min5=float(recent5.Low.min())
    # Breakout + controlled retest proxy: prior range broken recently, current close remains on the correct side.
    broke_up=float(h.tail(10).max())>prev20h
    broke_dn=float(l.tail(10).min())<prev20l
    if broke_up and last>prev20h: score+=2; bias="BUY"; reasons.append("Breakout held")
    elif broke_dn and last<prev20l: score+=2; bias="SELL"; reasons.append("Breakdown held")
    elif abs(last-prev20h)<=max(atrv,1e-9)*0.8 and last>=prev20h*0.995: score+=2; bias="BUY"; reasons.append("Retest of breakout")
    elif abs(last-prev20l)<=max(atrv,1e-9)*0.8 and last<=prev20l*1.005: score+=2; bias="SELL"; reasons.append("Retest of breakdown")
    if float(d.Volume.iloc[-1])>=float(d.Volume.tail(20).mean())*1.3: score+=1; reasons.append("Volume confirmation")
    return {"score":min(score,3),"bias":bias,"reason":", ".join(reasons) or "No breakout/retest confirmation"}

def strategy_fibonacci(d):
    if len(d)<60: return {"score":0,"bias":"WAIT","reason":"Insufficient data"}
    look=d.tail(60); hi=float(look.High.max()); lo=float(look.Low.min()); last=float(look.Close.iloc[-1]); span=hi-lo
    if span<=0: return {"score":0,"bias":"WAIT","reason":"No range"}
    # Identify directional swing by location and EMA slope.
    e20=d.Close.ewm(span=20,adjust=False).mean(); e50=d.Close.ewm(span=50,adjust=False).mean()
    bullish=e20.iloc[-1]>e50.iloc[-1]; bearish=e20.iloc[-1]<e50.iloc[-1]
    if bullish:
        fibs={"38.2":hi-span*.382,"50":hi-span*.5,"61.8":hi-span*.618}
        near=min(fibs.items(),key=lambda kv:abs(last-kv[1])); dist=abs(last-near[1])/span
        if dist<.08: return {"score":3 if dist<.04 else 2,"bias":"BUY","reason":f"Bullish structure near Fib {near[0]}%"}
        if last>fibs["38.2"]: return {"score":1,"bias":"BUY","reason":"Above 38.2% retracement"}
    if bearish:
        fibs={"38.2":lo+span*.382,"50":lo+span*.5,"61.8":lo+span*.618}
        near=min(fibs.items(),key=lambda kv:abs(last-kv[1])); dist=abs(last-near[1])/span
        if dist<.08: return {"score":3 if dist<.04 else 2,"bias":"SELL","reason":f"Bearish structure near Fib {near[0]}%"}
        if last<fibs["38.2"]: return {"score":1,"bias":"SELL","reason":"Below 38.2% retracement"}
    return {"score":0,"bias":"WAIT","reason":"No clean Fib/structure confluence"}

def strategy_momentum(d):
    if len(d)<60: return {"score":0,"bias":"WAIT","reason":"Insufficient data"}
    c=d.Close; e20=c.ewm(span=20,adjust=False).mean(); e50=c.ewm(span=50,adjust=False).mean(); e200=c.ewm(span=200,adjust=False).mean(); rr=float(rsi(c).iloc[-1]); vr=float(d.Volume.iloc[-1]/d.Volume.tail(20).mean()) if d.Volume.tail(20).mean() else 1
    score=0; reasons=[]
    if e20.iloc[-1]>e50.iloc[-1]>e200.iloc[-1]: bias="BUY"; score+=2; reasons.append("EMA20>50>200")
    elif e20.iloc[-1]<e50.iloc[-1]<e200.iloc[-1]: bias="SELL"; score+=2; reasons.append("EMA20<50<200")
    else: bias="WAIT"
    if bias=="BUY" and 50<=rr<=68: score+=1; reasons.append("RSI momentum")
    if bias=="SELL" and 32<=rr<=50: score+=1; reasons.append("RSI momentum")
    if vr>=1.3: score+=1; reasons.append("Volume expansion")
    return {"score":min(score,4),"bias":bias if score>=2 else "WAIT","reason":", ".join(reasons) or "No clean momentum alignment"}

def strategy_suite(ticker):
    d=_strategy_daily(ticker)
    if d.empty: return pd.DataFrame(), {"overall":"NO DATA","confidence":0}
    funcs=[("SMC",strategy_smc,5),("PRICE ACTION",strategy_price_action,4),("BREAKOUT + RETEST",strategy_breakout_retest,3),("FIBONACCI",strategy_fibonacci,3),("MOMENTUM",strategy_momentum,4)]
    rows=[]
    for name,fn,maxs in funcs:
        r=fn(d); rows.append({"Strategy":name,"Score":f"{r['score']}/{maxs}","Bias":r["bias"],"Reason":r["reason"]})
    buy=sum(1 for r in rows if r["Bias"]=="BUY"); sell=sum(1 for r in rows if r["Bias"]=="SELL")
    overall="BUY" if buy>=3 else "SELL" if sell>=3 else "MIXED / WAIT"
    conf=int(min(95,50+max(buy,sell)*9-abs(buy-sell==0)*5))
    return pd.DataFrame(rows), {"overall":overall,"confidence":conf,"buy":buy,"sell":sell}

# =========================
# OPTIONS CHAIN ANALYSIS
# =========================
NSE_OC_PAGE="https://www.nseindia.com/option-chain"
NSE_OC_INFO="https://www.nseindia.com/api/option-chain-contract-info"
NSE_OC_V3="https://www.nseindia.com/api/option-chain-v3"

@st.cache_data(ttl=45, show_spinner=False)
def nse_option_expiries(symbol, kind="Indices"):
    h={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/139 Safari/537.36","Accept":"application/json,text/plain,*/*","Referer":NSE_OC_PAGE}
    try:
        ss=requests.Session(); ss.get(NSE_OC_PAGE,headers=h,timeout=12)
        r=ss.get(NSE_OC_INFO,params={"symbol":symbol},headers=h,timeout=12)
        r.raise_for_status(); j=r.json()
        dates=j.get("expiryDates") or j.get("records",{}).get("expiryDates") or []
        return dates, None
    except Exception as e:
        return [], str(e)

@st.cache_data(ttl=30, show_spinner=False)
def nse_option_chain(symbol, expiry, kind="Indices"):
    h={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/139 Safari/537.36","Accept":"application/json,text/plain,*/*","Referer":NSE_OC_PAGE}
    try:
        ss=requests.Session(); ss.get(NSE_OC_PAGE,headers=h,timeout=12)
        r=ss.get(NSE_OC_V3,params={"type":kind,"symbol":symbol,"expiry":expiry},headers=h,timeout=15)
        r.raise_for_status(); return r.json(), None
    except Exception as e:
        return None, str(e)

def option_rows(raw):
    if not raw: return pd.DataFrame(), {}
    records=raw.get("records",{}) if isinstance(raw,dict) else {}
    data=records.get("data",[]) or raw.get("filtered",{}).get("data",[]) if isinstance(raw,dict) else []
    rows=[]
    for item in data:
        ce=item.get("CE") or {}; pe=item.get("PE") or {}
        rows.append({
            "STRIKE":item.get("strikePrice"),
            "CE_OI":ce.get("openInterest",0),"CE_CHG_OI":ce.get("changeinOpenInterest",0),"CE_VOL":ce.get("totalTradedVolume",0),"CE_IV":ce.get("impliedVolatility",0),"CE_LTP":ce.get("lastPrice",0),"CE_CHG":ce.get("change",0),"CE_BID":ce.get("buyPrice1",0),"CE_ASK":ce.get("sellPrice1",0),
            "PE_BID":pe.get("buyPrice1",0),"PE_ASK":pe.get("sellPrice1",0),"PE_LTP":pe.get("lastPrice",0),"PE_CHG":pe.get("change",0),"PE_IV":pe.get("impliedVolatility",0),"PE_VOL":pe.get("totalTradedVolume",0),"PE_CHG_OI":pe.get("changeinOpenInterest",0),"PE_OI":pe.get("openInterest",0)
        })
    df=pd.DataFrame(rows)
    meta={"spot":records.get("underlyingValue"),"expiry":records.get("expiryDates",[None])[0] if records.get("expiryDates") else None}
    if isinstance(raw,dict): meta["timestamp"]=raw.get("records",{}).get("timestamp")
    return df,meta

def parse_pasted_chain(txt):
    try:
        import json
        raw=json.loads(txt); return option_rows(raw)
    except Exception as e: return pd.DataFrame(), {"error":str(e)}

def max_pain(df):
    if df.empty: return np.nan
    strikes=df["STRIKE"].astype(float).dropna().unique(); best=None
    for k in strikes:
        call=(np.maximum(k-df["STRIKE"].astype(float),0)*df["CE_OI"].fillna(0)).sum()
        put=(np.maximum(df["STRIKE"].astype(float)-k,0)*df["PE_OI"].fillna(0)).sum()
        pain=call+put
        if best is None or pain<best[0]: best=(pain,k)
    return float(best[1]) if best else np.nan

def option_analysis(df, spot):
    if df.empty: return {}
    d=df.copy().sort_values("STRIKE"); spot=float(spot) if spot is not None and pd.notna(spot) else float(d["STRIKE"].median())
    atm=float(d.iloc[(d["STRIKE"].astype(float)-spot).abs().argsort()[:1]]["STRIKE"].iloc[0])
    call_oi=float(d["CE_OI"].fillna(0).sum()); put_oi=float(d["PE_OI"].fillna(0).sum())
    call_chg=float(d["CE_CHG_OI"].fillna(0).sum()); put_chg=float(d["PE_CHG_OI"].fillna(0).sum())
    pcr=put_oi/call_oi if call_oi else np.nan; pcr_chg=put_chg/call_chg if call_chg else np.nan
    call_wall=float(d.loc[d["CE_OI"].idxmax(),"STRIKE"]) if d["CE_OI"].sum()>0 else np.nan
    put_wall=float(d.loc[d["PE_OI"].idxmax(),"STRIKE"]) if d["PE_OI"].sum()>0 else np.nan
    atmrow=d.iloc[(d["STRIKE"].astype(float)-atm).abs().argsort()[:1]].iloc[0]
    ce=float(atmrow.get("CE_LTP",0) or 0); pe=float(atmrow.get("PE_LTP",0) or 0)
    if pcr>=1.15 and put_chg>0 and call_chg<=put_chg: bias="BULLISH"
    elif pcr<=0.80 and call_chg>0 and put_chg<=0: bias="BEARISH"
    elif pcr>=1.05: bias="BULLISH"
    elif pcr<=0.90: bias="BEARISH"
    else: bias="NEUTRAL"
    confidence=55
    if bias=="BULLISH": confidence+=min(20,max(0,(pcr-1)*30))
    if bias=="BEARISH": confidence+=min(20,max(0,(1-pcr)*50))
    if abs(put_chg)>abs(call_chg)*1.2 if abs(call_chg)>0 else put_chg>0: confidence+=10
    confidence=int(min(95,max(45,confidence)))
    return {"spot":spot,"atm":atm,"call_oi":call_oi,"put_oi":put_oi,"call_chg_oi":call_chg,"put_chg_oi":put_chg,"pcr":pcr,"call_wall":call_wall,"put_wall":put_wall,"max_pain":max_pain(d),"atm_ce":ce,"atm_pe":pe,"bias":bias,"confidence":confidence}

def trade_plan(df, ana):
    if df.empty or not ana: return {}
    spot=ana["spot"]; bias=ana["bias"]; atm=ana["atm"]
    if bias=="BULLISH":
        candidates=df[df["STRIKE"]>=atm].copy().sort_values("STRIKE").head(3)
        if candidates.empty: return {}
        row=candidates.iloc[0]; side="CALL"; premium=float(row["CE_LTP"] or 0); strike=float(row["STRIKE"])
        optsym=f"{strike:g} CE"; reason="PCR/OI structure supports bullish bias"
    elif bias=="BEARISH":
        candidates=df[df["STRIKE"]<=atm].copy().sort_values("STRIKE",ascending=False).head(3)
        if candidates.empty: return {}
        row=candidates.iloc[0]; side="PUT"; premium=float(row["PE_LTP"] or 0); strike=float(row["STRIKE"])
        optsym=f"{strike:g} PE"; reason="PCR/OI structure supports bearish bias"
    else: return {"side":"WAIT","reason":"Neutral option-chain structure"}
    if premium<=0: return {"side":"WAIT","reason":"No valid premium"}
    entry=premium; sl=round(premium*0.70,2); tp1=round(premium*1.50,2); tp2=round(premium*2.00,2)
    otm=abs(strike-spot)/spot*100
    hero_zero="HERO-ZERO HIGH RISK" if (premium/spot*100)<0.20 and otm<2.0 else "NORMAL PREMIUM"
    return {"side":side,"strike":strike,"option":optsym,"entry":entry,"sl":sl,"tp1":tp1,"tp2":tp2,"rr":"1:1.67 / 1:3.33","reason":reason,"class":hero_zero,"otm_pct":otm}


# =========================
# HERO-ZERO SCANNER
# =========================
def hero_zero_candidates(df, ana):
    if df is None or df.empty or not ana:
        return pd.DataFrame()
    d=df.copy()
    spot=float(ana.get("spot") or 0)
    atm=float(ana.get("atm") or spot)
    bias=str(ana.get("bias","NEUTRAL"))
    if spot<=0 or atm<=0: return pd.DataFrame()
    atm_row=d.iloc[(d["STRIKE"].astype(float)-atm).abs().argsort()[:1]].iloc[0]
    atm_prem=float((atm_row.get("CE_LTP",0) if bias!="BEARISH" else atm_row.get("PE_LTP",0)) or 0)
    rows=[]
    for _,r in d.iterrows():
        k=float(r["STRIKE"]); dist=abs(k-spot)/spot*100
        if dist < 0.25 or dist > 3.0: continue
        side="CALL" if bias=="BULLISH" else "PUT" if bias=="BEARISH" else ("CALL" if k>spot else "PUT")
        ltp=float((r.get("CE_LTP",0) if side=="CALL" else r.get("PE_LTP",0)) or 0)
        oi=float((r.get("CE_OI",0) if side=="CALL" else r.get("PE_OI",0)) or 0)
        chg=float((r.get("CE_CHG_OI",0) if side=="CALL" else r.get("PE_CHG_OI",0)) or 0)
        vol=float((r.get("CE_VOL",0) if side=="CALL" else r.get("PE_VOL",0)) or 0)
        iv=float((r.get("CE_IV",0) if side=="CALL" else r.get("PE_IV",0)) or 0)
        # Hero-zero = inexpensive premium + enough liquidity + directional OI support.
        if ltp<=0 or oi<=0 or vol<=0: continue
        if atm_prem>0 and ltp>atm_prem*0.55: continue
        score=40
        score += min(20, (vol/max(1,oi))*100*2)
        if chg>0: score += 15
        if 0.5<=dist<=2.0: score += 10
        if iv<=35: score += 10
        score=int(min(95,round(score)))
        entry=ltp; sl=round(entry*0.55,2); tp1=round(entry*1.8,2); tp2=round(entry*2.5,2)
        rows.append({"Side":side,"Strike":k,"Premium":round(ltp,2),"Distance %":round(dist,2),"OI":int(oi),"Change OI":int(chg),"Volume":int(vol),"IV":round(iv,2),"Score":score,"Entry":round(entry,2),"SL":sl,"TP1":tp1,"TP2":tp2,"RR":"1:1.78 / 1:3.33"})
    out=pd.DataFrame(rows)
    return out.sort_values(["Score","Volume"],ascending=False).head(10) if not out.empty else out

# =========================
# PROFESSIONAL DASHBOARD HELPERS
# =========================
SECTORS = {
    "BANKING": ["HDFCBANK","ICICIBANK","SBIN","KOTAKBANK","AXISBANK","BANKBARODA","CANBK","PNB","INDUSINDBK","IDFCFIRSTB","INDIANB","FEDERALBNK","YESBANK","IDBI"],
    "IT": ["TCS","INFY","HCLTECH","WIPRO","TECHM","PERSISTENT","COFORGE","LTIM","MPHASIS"],
    "AUTO": ["MARUTI","M&M","TATAMOTORS","BAJAJ-AUTO","EICHERMOT","HEROMOTOCO","TVSMOTOR"],
    "PHARMA": ["SUNPHARMA","CIPLA","DRREDDY","DIVISLAB","LUPIN","ZYDUSLIFE","TORNTPHARM","ABBOTINDIA"],
    "METAL": ["TATASTEEL","JSWSTEEL","HINDALCO","VEDL","SAIL","NMDC","JINDALSTEL","HINDZINC"],
    "ENERGY": ["RELIANCE","ONGC","NTPC","POWERGRID","COALINDIA","IOC","BPCL","GAIL","TATAPOWER","ADANIPOWER"],
    "FMCG": ["ITC","HINDUNILVR","NESTLEIND","BRITANNIA","DABUR","GODREJCP","TATACONSUM","VBL"],
    "DEFENCE": ["HAL","BEL"],
    "REALTY": ["DLF"],
    "CAPITAL GOODS": ["LT","SIEMENS","ABB","POLYCAB","HAVELLS"],
}

def market_regime():
    rows=[]
    for t,n in list(INDEXES.items())[:6]:
        d=history(t,"6mo","1d")
        if d.empty or len(d)<50: continue
        c=d["Close"].astype(float)
        e20=c.ewm(span=20,adjust=False).mean().iloc[-1]
        e50=c.ewm(span=50,adjust=False).mean().iloc[-1]
        rows.append((n,"BULLISH" if e20>e50 else "BEARISH" if e20<e50 else "RANGE"))
    bull=sum(x[1]=="BULLISH" for x in rows); bear=sum(x[1]=="BEARISH" for x in rows)
    regime="BULLISH" if bull>=4 else "BEARISH" if bear>=4 else "MIXED / RANGE"
    return regime,rows

def sector_snapshot():
    rows=[]
    for sector,syms in SECTORS.items():
        changes=[]
        for s in syms[:8]:
            if s not in CORE: continue
            d=history(yf_ticker(s,"NSE"),"5d","1d")
            if not d.empty and len(d)>=2:
                c=d["Close"].dropna()
                if len(c)>=2: changes.append((float(c.iloc[-1])/float(c.iloc[-2])-1)*100)
        if changes:
            avg=float(np.mean(changes)); rows.append({"Sector":sector,"Avg % Change":round(avg,2),"Stocks":len(changes)})
    return pd.DataFrame(rows).sort_values("Avg % Change",ascending=False) if rows else pd.DataFrame()


# =========================
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_nifty100_symbols():
    """Official NSE NIFTY 100 constituents; CORE is the offline fallback."""
    urls=[
        "https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv",
        "https://archives.nseindia.com/content/indices/ind_nifty100list.csv",
    ]
    for url in urls:
        try:
            r=requests.get(url,timeout=15,headers={"User-Agent":"Mozilla/5.0","Accept":"text/csv,*/*"})
            r.raise_for_status()
            d=pd.read_csv(pd.io.common.BytesIO(r.content))
            sym=_norm_col(d,["Symbol","SYMBOL"])
            if sym:
                vals=d[sym].astype(str).str.strip().str.upper().tolist()
                vals=[x for x in vals if x and x!="NAN"]
                if len(vals)>=90:
                    return vals[:100]
        except Exception:
            pass
    return list(CORE)[:100]


def top100_stock_pairs():
    """Return 100 NIFTY-100 companies, resolving each to NSE first and BSE as fallback."""
    symbols=fetch_nifty100_symbols()
    pairs=[]
    for sym in symbols:
        n=UNIV[(UNIV["symbol"]==sym)&(UNIV["exchange"]=="NSE")]
        b=UNIV[(UNIV["symbol"]==sym)&(UNIV["exchange"]=="BSE")]
        if not n.empty:
            row=n.iloc[0]; pairs.append((sym,str(row.get("name",sym)),"NSE"))
        elif not b.empty:
            row=b.iloc[0]; pairs.append((sym,str(row.get("name",sym)),"BSE"))
        else:
            pairs.append((sym,sym,"NSE"))
    return pairs[:100]

# VS FLOW OB + TREND RADAR
# =========================
OB_TFS = ["1M", "1W", "1D", "4H", "1H"]


def _clean_ohlcv(d):
    if d is None or d.empty:
        return pd.DataFrame()
    x=d.copy()
    for c in ["Open","High","Low","Close","Volume"]:
        if c not in x.columns: return pd.DataFrame()
        x[c]=pd.to_numeric(x[c],errors="coerce")
    return x.dropna(subset=["Open","High","Low","Close"])


def _resample_4h(h1):
    x=_clean_ohlcv(h1)
    if x.empty: return x
    try:
        return x.resample("4h").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna(subset=["Open","High","Low","Close"])
    except Exception:
        return pd.DataFrame()


def _tf_data(ticker, tf):
    if tf=="1M": return _clean_ohlcv(history(ticker,"10y","1mo"))
    if tf=="1W": return _clean_ohlcv(history(ticker,"5y","1wk"))
    if tf=="1D": return _clean_ohlcv(history(ticker,"2y","1d"))
    if tf=="4H": return _resample_4h(history(ticker,"60d","1h"))
    if tf=="1H": return _clean_ohlcv(history(ticker,"60d","1h"))
    return pd.DataFrame()


def _trend_label(d):
    if d.empty or len(d)<55: return "NO DATA"
    c=d["Close"].astype(float)
    e20=c.ewm(span=20,adjust=False).mean().iloc[-1]
    e50=c.ewm(span=50,adjust=False).mean().iloc[-1]
    px=float(c.iloc[-1])
    if e20>e50 and px>e20: return "BULLISH"
    if e20<e50 and px<e20: return "BEARISH"
    return "MIXED"


def _ob_candidates(d):
    """Detect displacement-created opposite candles and keep only later-unbroken zones."""
    x=_clean_ohlcv(d)
    if x.empty or len(x)<30: return []
    a=atr(x,14)
    out=[]
    # Recent history gets priority, while still allowing a meaningful HTF zone.
    start=max(1,len(x)-220)
    for i in range(start,len(x)-2):
        o,h,l,c=[float(x.iloc[i][k]) for k in ["Open","High","Low","Close"]]
        nxt=x.iloc[i+1]
        na=float(a.iloc[i+1]) if pd.notna(a.iloc[i+1]) else 0
        if na<=0: continue
        body=abs(c-o)
        disp=abs(float(nxt["Close"])-float(nxt["Open"]))
        nr=float(nxt["High"])-float(nxt["Low"])
        # Bullish OB: bearish/base candle followed by strong bullish displacement.
        if c<o and float(nxt["Close"])>float(nxt["Open"]) and disp>=0.9*na and nr>=1.15*na:
            zl,zh=l,h
            future=x.iloc[i+2:]
            broken=not future.empty and float(future["Low"].min()) < zl*(1-0.0005)
            if not broken:
                out.append({"side":"BULL","low":zl,"high":zh,"idx":i,"strength":disp/na})
        # Bearish OB: bullish/base candle followed by strong bearish displacement.
        if c>o and float(nxt["Close"])<float(nxt["Open"]) and disp>=0.9*na and nr>=1.15*na:
            zl,zh=l,h
            future=x.iloc[i+2:]
            broken=not future.empty and float(future["High"].max()) > zh*(1+0.0005)
            if not broken:
                out.append({"side":"BEAR","low":zl,"high":zh,"idx":i,"strength":disp/na})
    return out


def _nearest_ob(d, side, price):
    cands=[z for z in _ob_candidates(d) if z["side"]==side]
    if not cands: return None
    def dist(z):
        if z["low"]<=price<=z["high"]: return 0.0
        return min(abs(price-z["low"]),abs(price-z["high"]))
    # nearest first, then newer/stronger zone.
    return sorted(cands,key=lambda z:(dist(z),-z["idx"],-z["strength"]))[0]


def _ob_status(z, price, atrv):
    if z is None or atrv<=0: return "NONE", np.nan
    if z["low"]<=price<=z["high"]: return "TOUCHING", 0.0
    dist=min(abs(price-z["low"]),abs(price-z["high"]))
    atr_dist=dist/atrv
    if atr_dist<=0.50: return "NEAR", atr_dist
    if atr_dist<=1.00: return "APPROACHING", atr_dist
    return "FAR", atr_dist


def _zone_text(z):
    return "—" if z is None else f"{z['low']:,.2f}–{z['high']:,.2f}"


@st.cache_data(ttl=300, show_spinner=False)
def ob_trend_scan(ticker):
    frames={}
    price=np.nan
    for tf in OB_TFS:
        d=_tf_data(ticker,tf)
        frames[tf]=d
        if not d.empty: price=float(d["Close"].iloc[-1])
    if pd.isna(price):
        return {"Price":np.nan,"Trend Score": "NO DATA","Decision":"NO DATA"}
    trends={tf:_trend_label(frames[tf]) for tf in OB_TFS}
    bull_score=sum(trends[tf]=="BULLISH" for tf in OB_TFS)
    bear_score=sum(trends[tf]=="BEARISH" for tf in OB_TFS)
    d1=frames.get("1D",pd.DataFrame())
    if d1.empty or len(d1)<30:
        location="NO DATA"; pd_score=0
    else:
        hi=float(d1["High"].tail(60).max()); lo=float(d1["Low"].tail(60).min())
        rng=hi-lo
        pos=(price-lo)/rng if rng>0 else .5
        location="PREMIUM" if pos>=0.60 else "DISCOUNT" if pos<=0.40 else "EQUILIBRIUM"
        pd_score=1 if location in ("DISCOUNT","PREMIUM") else 0
    best_bull=None; best_bear=None; bull_status="NONE"; bear_status="NONE"; bull_dist=np.nan; bear_dist=np.nan
    bull_tf="—"; bear_tf="—"
    for tf in OB_TFS:
        d=frames[tf]
        if d.empty: continue
        av=float(atr(d,14).iloc[-1]) if len(d)>=15 and pd.notna(atr(d,14).iloc[-1]) else np.nan
        if not np.isfinite(av) or av<=0: continue
        zb=_nearest_ob(d,"BULL",price)
        zr=_nearest_ob(d,"BEAR",price)
        sb,db=_ob_status(zb,price,av); sr,dr=_ob_status(zr,price,av)
        if zb is not None and (best_bull is None or (db, -zb["idx"]) < (bull_dist if np.isfinite(bull_dist) else 999, -(best_bull["idx"] if best_bull else -1))):
            best_bull=zb; bull_status=sb; bull_dist=db; bull_tf=tf
        if zr is not None and (best_bear is None or (dr, -zr["idx"]) < (bear_dist if np.isfinite(bear_dist) else 999, -(best_bear["idx"] if best_bear else -1))):
            best_bear=zr; bear_status=sr; bear_dist=dr; bear_tf=tf
    # User's primary filter: price must be interacting with a nearby HTF OB.
    bull_ob_ok=bull_status in ("TOUCHING","NEAR","APPROACHING")
    bear_ob_ok=bear_status in ("TOUCHING","NEAR","APPROACHING")
    buy_points=(2 if bull_score>=3 else 0)+(1 if location=="DISCOUNT" else 0)+(2 if bull_status=="TOUCHING" else 1 if bull_status in ("NEAR","APPROACHING") else 0)
    sell_points=(2 if bear_score>=3 else 0)+(1 if location=="PREMIUM" else 0)+(2 if bear_status=="TOUCHING" else 1 if bear_status in ("NEAR","APPROACHING") else 0)
    if bull_score>=3 and bull_ob_ok and location=="DISCOUNT": decision="BUY WATCH"
    elif bear_score>=3 and bear_ob_ok and location=="PREMIUM": decision="SELL WATCH"
    elif bull_status=="TOUCHING" or bear_status=="TOUCHING": decision="OB TOUCH"
    elif bull_ob_ok or bear_ob_ok: decision="OB NEAR"
    else: decision="WAIT"
    return {
        "Price":price, "1M Trend":trends["1M"],"1W Trend":trends["1W"],"1D Trend":trends["1D"],"4H Trend":trends["4H"],"1H Trend":trends["1H"],
        "Bull Trend":bull_score,"Bear Trend":bear_score,"Location":location,
        "Bull OB TF":bull_tf,"Bull OB":_zone_text(best_bull),"Bull Dist ATR":round(float(bull_dist),2) if np.isfinite(bull_dist) else np.nan,"Bull Status":bull_status,
        "Bear OB TF":bear_tf,"Bear OB":_zone_text(best_bear),"Bear Dist ATR":round(float(bear_dist),2) if np.isfinite(bear_dist) else np.nan,"Bear Status":bear_status,
        "BUY Score":buy_points,"SELL Score":sell_points,"Decision":decision
    }


def ob_trend_page():
    st.markdown('<div class="section">🔥 VS FLOW OB + TREND RADAR <small>TOP 100 INDIA + KEY INDICES • 1M → 1W → 1D → 4H → 1H</small></div>',unsafe_allow_html=True)
    st.markdown('<div class="note"><b>Primary filter:</b> nearest active Order Block first. Then VS FLOW filters: multi-timeframe trend alignment → Premium/Discount → OB proximity. This is a radar/filter, not a blind entry signal.</div>',unsafe_allow_html=True)

    top100=top100_stock_pairs()
    stock_items=[(s,n,e) for s,n,e in top100]
    index_items=[(t,n,"INDEX") for t,n in OB_INDEXES.items()]

    c1,c2=st.columns([2.2,1.2])
    with c1:
        universe_mode=st.selectbox(
            "Universe",
            ["TOP 100 INDIA (NSE + BSE)","TOP 100 INDIA + 7 KEY INDICES","7 KEY INDICES ONLY"],
            index=1,
            key="ob_universe_mode_v2"
        )
    with c2:
        limit=st.selectbox("Scan limit",[25,50,100,107],index=3,key="ob_scan_limit_v2")

    if universe_mode=="TOP 100 INDIA (NSE + BSE)":
        items=stock_items
    elif universe_mode=="TOP 100 INDIA + 7 KEY INDICES":
        items=stock_items+index_items
    else:
        items=index_items

    # Keep the requested universe order; limit applies after indices are appended.
    items=items[:int(limit)]
    st.caption(f"Ready to scan: {len(items)} assets • {sum(1 for x in items if x[2] != 'INDEX')} stocks + {sum(1 for x in items if x[2] == 'INDEX')} indices")
    with st.expander("View scan universe",expanded=False):
        st.dataframe(pd.DataFrame(items,columns=["Symbol","Name","Exchange"]),use_container_width=True,hide_index=True)

    if st.button("🚀 SCAN TOP 100 + KEY INDICES",use_container_width=True,key="ob_trend_run_v2"):
        st.session_state.ob_trend_scan=pd.DataFrame()
        rows=[]; bar=st.progress(0); status=st.empty()
        for i,(sym,name,exch) in enumerate(items):
            try:
                ticker=sym if exch=="INDEX" else yf_ticker(sym,exch)
                r=ob_trend_scan(ticker)
                r.update({"Symbol":sym,"Name":name,"Exchange":exch,"Asset Type":"INDEX" if exch=="INDEX" else "STOCK"})
                rows.append(r)
            except Exception as e:
                rows.append({"Symbol":sym,"Name":name,"Exchange":exch,"Asset Type":"INDEX" if exch=="INDEX" else "STOCK","Decision":"ERROR","Error":str(e)[:80]})
            bar.progress((i+1)/max(1,len(items))); status.caption(f"Scanning {i+1}/{len(items)} • {sym}")
        bar.empty(); status.empty()
        out=pd.DataFrame(rows)
        if not out.empty:
            rank={"BUY WATCH":0,"SELL WATCH":0,"OB TOUCH":1,"OB NEAR":2,"WAIT":4,"NO DATA":5,"ERROR":6}
            out["_rank"]=out["Decision"].map(rank).fillna(9)
            out=out.sort_values(["_rank","BUY Score","SELL Score"],ascending=[True,False,False]).drop(columns="_rank")
        st.session_state.ob_trend_scan=out

    df=st.session_state.get("ob_trend_scan",pd.DataFrame())
    if not df.empty:
        buy=int((df["Decision"]=="BUY WATCH").sum()); sell=int((df["Decision"]=="SELL WATCH").sum()); touch=int((df["Decision"]=="OB TOUCH").sum())
        m1,m2,m3,m4=st.columns(4)
        m1.markdown(f'<div class="metric"><div class="k">BUY WATCH</div><div class="v up">{buy}</div></div>',unsafe_allow_html=True)
        m2.markdown(f'<div class="metric"><div class="k">SELL WATCH</div><div class="v down">{sell}</div></div>',unsafe_allow_html=True)
        m3.markdown(f'<div class="metric"><div class="k">OB TOUCH</div><div class="v">{touch}</div></div>',unsafe_allow_html=True)
        m4.markdown(f'<div class="metric"><div class="k">SCANNED</div><div class="v">{len(df)}</div></div>',unsafe_allow_html=True)
        cols=["Symbol","Name","Asset Type","Exchange","Price","1M Trend","1W Trend","1D Trend","4H Trend","1H Trend","Location","Bull OB TF","Bull OB","Bull Dist ATR","Bull Status","Bear OB TF","Bear OB","Bear Dist ATR","Bear Status","BUY Score","SELL Score","Decision"]
        cols=[c for c in cols if c in df.columns]
        st.dataframe(df[cols],use_container_width=True,hide_index=True)
        hits=df[df["Decision"].isin(["BUY WATCH","SELL WATCH","OB TOUCH","OB NEAR"])].copy()
        if not hits.empty:
            st.markdown('<div class="section">🎯 FILTERED RADAR <small>OB interaction + VS FLOW filters</small></div>',unsafe_allow_html=True)
            st.dataframe(hits[cols],use_container_width=True,hide_index=True)
        st.download_button("⬇️ DOWNLOAD OB + TREND CSV",df.to_csv(index=False).encode(),file_name="VS_FLOW_OB_TREND_RADAR.csv",mime="text/csv",use_container_width=True)
    else:
        st.info("TOP 100 India + 7 Key Indices ready. Click SCAN to run the radar.")

def setup_cards(df):
    if df.empty: return
    for i,r in df.iterrows():
        sig=str(r.get("Signal","WAIT")); score=str(r.get("Score","0/5"))
        cls="green" if "BUY" in sig else "red" if "SELL" in sig else "gold"
        st.markdown(f'''<div class="setup-card">
        <div class="setup-top"><b>{r.get("Symbol","")}</b><span class="pill {cls}">{sig}</span><span class="pill">{score}</span></div>
        <div class="setup-grid">
        <div><span>4H</span><b>{r.get("4H OB","")}</b></div><div><span>1H SWEEP</span><b>{r.get("1H Sweep","")}</b></div>
        <div><span>1H BOS</span><b>{r.get("1H BOS","")}</b></div><div><span>15M FVG</span><b>{r.get("15M FVG","")}</b></div>
        <div><span>5M</span><b>{r.get("5M Trigger","")}</b></div>
        <div><span>RR</span><b>{r.get("RR","")}</b></div>
        </div>
        <div class="trade-line"><span>ENTRY <b>{r.get("Entry","")}</b></span><span>SL <b>{r.get("SL","")}</b></span><span>TP <b>{r.get("TP","")}</b></span><span>TALLY <b>{r.get("Chart Tally","")}</b></span></div>
        </div>''',unsafe_allow_html=True)

# =========================
# NAV / UI
# =========================
if "page" not in st.session_state: st.session_state.page="HOME"
if "selected" not in st.session_state: st.session_state.selected="RELIANCE"

with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO),use_container_width=True)
    st.markdown('<div class="vs-brand">⚡ VS FLOW <span class="india">INDIA 🇮🇳</span></div>',unsafe_allow_html=True)
    st.markdown('<div class="vs-sub">SCAN • ANALYSE • TRADE</div>',unsafe_allow_html=True)
    st.markdown("")
    nav=[
        ("🏠","HOME"),("📈","ALL INDIAN STOCKS"),("🎯","SMART STOCK FINDER"),("🌐","INDIAN INDICES"),("🔥","VS FLOW SETUP"),("🧱","VS FLOW OB + TREND"),("⛓️","OPTIONS ANALYSIS"),("💀","HERO-ZERO"),("🧠","STRATEGY LAB"),("⚡","SMC 4H→5M SCALP"),("📐","CLASSIC PRICE ACTION"),
    ]
    for icon,label in nav:
        if st.button(f"{icon}  {label}",key="nav_"+label,use_container_width=True):
            st.session_state.page=label; st.rerun()
    st.markdown('<div class="side-note"><b>Indian Universe</b><br>Exchange-master based NSE/BSE universe. Quotes and charts load only when needed.<br><br><b>Fast mode</b><br>Search is local; market data is cached.<br><br><b>Owner</b><br>vaibhav shirsat</div>',unsafe_allow_html=True)

# Global fast search
search=st.text_input("",placeholder="🔎 Search any Indian stock, company or index — e.g. RELIANCE, TCS, NIFTY, BANKNIFTY",label_visibility="collapsed")
if search.strip():
    q=search.strip().lower()
    u=UNIV[(UNIV["symbol"].str.lower().str.contains(q,regex=False,na=False)) | (UNIV["name"].str.lower().str.contains(q,regex=False,na=False))].head(15).copy()
    idx=[{"symbol":k,"name":v,"exchange":"INDEX","series":"INDEX","isin":""} for k,v in INDEXES.items() if q in k.lower() or q in v.lower()]
    m=pd.concat([pd.DataFrame(idx),u],ignore_index=True).head(15)
    if not m.empty:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        for i,(_,r) in enumerate(m.iterrows()):
            c1,c2,c3=st.columns([1.5,5,1])
            c1.markdown(f"**{r['symbol']}**")
            c2.write(r["name"])
            if c3.button("OPEN",key=f"search_open_{i}_{r['symbol']}"):
                if r["exchange"]=="INDEX":
                    st.session_state.selected_index=r["symbol"]; st.session_state.page="INDIAN INDICES"
                else:
                    st.session_state.selected=r["symbol"]; st.session_state.selected_exchange=r["exchange"]; st.session_state.page="ALL INDIAN STOCKS"
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

st.markdown('<div class="hero" style="position:relative"><div class="owner-badge">vaibhav shirsat</div><h1>VS FLOW INDIA 🇮🇳</h1><p>All Indian Stocks • Indian Indices • Core Setup • SMC 4H→5M • Classic • Options • Hero-Zero • Strategy Lab</p><div class="gradient"></div></div>',unsafe_allow_html=True)

page=st.session_state.page

# =========================
# HOME
# =========================
if page=="HOME":
    # MARKET COMMAND CENTER
    st.markdown('<div class="section">🇮🇳 MARKET COMMAND CENTER <small>decision-first dashboard</small></div>',unsafe_allow_html=True)
    regime, regime_rows = market_regime()
    rc1,rc2,rc3=st.columns([1.1,2.2,2.2])
    with rc1:
        cls="green" if regime=="BULLISH" else "red" if regime=="BEARISH" else "gold"
        st.markdown(f'<div class="panel"><span class="pill {cls}">MARKET REGIME</span><div class="regime">{regime}</div><small>EMA20 / EMA50 index breadth</small></div>',unsafe_allow_html=True)
    with rc2:
        st.markdown('<div class="panel"><b>INDEX BREADTH</b><br><br>'+" &nbsp; ".join([f'<span class="pill {"green" if s=="BULLISH" else "red" if s=="BEARISH" else "gold"}">{n}: {s}</span>' for n,s in regime_rows])+'</div>',unsafe_allow_html=True)
    with rc3:
        st.markdown(f'<div class="panel"><span class="pill green">UNIVERSE</span><div class="regime">{len(UNIV):,}</div><small>NSE + BSE searchable records</small></div>',unsafe_allow_html=True)
    ac1,ac2,ac3=st.columns(3)
    with ac1:
        if st.button("OPEN MARKET REGIME",key="open_regime",use_container_width=True):
            st.session_state.page="INDIAN INDICES"; st.rerun()
    with ac2:
        if st.button("OPEN INDEX BREADTH",key="open_breadth",use_container_width=True):
            st.session_state.page="INDIAN INDICES"; st.rerun()
    with ac3:
        if st.button("OPEN ALL INDIA UNIVERSE",key="open_universe",use_container_width=True):
            st.session_state.page="ALL INDIAN STOCKS"; st.rerun()

    st.markdown('<div class="section">📊 MARKET PULSE <small>click any index for full detail</small></div>',unsafe_allow_html=True)
    pulse_items=[(k,INDEXES[k]) for k in ["^NSEI","^NSEBANK","^CNXFIN","^BSESN","^INDIAVIX","^NSEMDCP50"] if k in INDEXES]
    cols=st.columns(6)
    for i,(t,n) in enumerate(pulse_items):
        r=quote(t)
        with cols[i]:
            if r:
                cls="up" if r["chg"]>0 else "down" if r["chg"]<0 else "flat"
                st.markdown(f'<div class="card"><div class="label">{n}</div><div class="value">{r["price"]:,.2f}</div><div class="{cls}">{r["chg"]:+.2f}%</div><div class="click-hint">Click OPEN for chart + bias + setup</div></div>',unsafe_allow_html=True)
            else: st.markdown(f'<div class="card"><div class="label">{n}</div><div class="value">—</div><div class="flat">Unavailable</div></div>',unsafe_allow_html=True)
            if st.button("OPEN",key=f"home_idx_open_{i}",use_container_width=True):
                st.session_state.selected_index=t; st.session_state.page="INDEX DETAIL"; st.rerun()

    # Today's best setups: use last core scan when available; otherwise a clear action to run it.
    st.markdown('<div class="section">🎯 TODAY\'S BEST SETUPS <small>Core 4/5+ candidates</small></div>',unsafe_allow_html=True)
    cs=st.session_state.get("core_scan",pd.DataFrame())
    if not cs.empty:
        hits=cs[cs["Score"].astype(str).str.startswith(("4/5","5/5"))].copy()
        hits["_rank"]=hits["Score"].map({"5/5":5,"4/5":4}).fillna(0)
        hits=hits.sort_values("_rank",ascending=False).head(6)
        if hits.empty: st.info("No 4/5+ Core setup in the latest scan. Open VS FLOW SETUP and run a scan.")
        else:
            setup_cards(hits)
            if st.button("🔥 OPEN FULL CORE SETUP",use_container_width=True,key="home_open_core"):
                st.session_state.page="VS FLOW SETUP"; st.rerun()
    else:
        st.markdown('<div class="panel"><b>No Core scan loaded yet.</b><br>Run the 100-stock Core scan once. Your latest A+/Core results will automatically appear here on the next visit.</div>',unsafe_allow_html=True)
        if st.button("🚀 RUN CORE SETUP NOW",use_container_width=True,key="home_run_core"):
            st.session_state.page="VS FLOW SETUP"; st.rerun()

    st.markdown('<div class="section">🏭 SECTOR PULSE <small>5-day price breadth snapshot</small></div>',unsafe_allow_html=True)
    if st.button("⚡ LOAD SECTOR PULSE",use_container_width=True,key="sector_run"):
        st.session_state.sector_snapshot=sector_snapshot()
    sec=st.session_state.get("sector_snapshot",pd.DataFrame())
    if not sec.empty:
        c1,c2=st.columns(2)
        for i,(_,r) in enumerate(sec.iterrows()):
            target=c1 if i%2==0 else c2
            val=float(r["Avg % Change"]); cls="up" if val>0 else "down" if val<0 else "flat"
            target.markdown(f'<div class="heat"><span class="s">{r["Sector"]} • {int(r["Stocks"])} stocks</span><div class="v {cls}">{val:+.2f}%</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="section">🛡️ TRADE GUARD <small>decision checklist before execution</small></div>',unsafe_allow_html=True)
    g1,g2,g3,g4=st.columns(4)
    guards=[("MARKET","Index regime aligned"),("SETUP","Core 4/5+ preferred"),("OPTIONS","OI/PCR confirms"),("RISK","Defined SL + minimum RR")]
    for box,(title,txt) in zip([g1,g2,g3,g4],guards):
        with box:
            st.markdown(f'<div class="action-card"><b>{title}</b><br><span class="click-hint">{txt}</span></div>',unsafe_allow_html=True)
    st.markdown('<div class="section">⚡ QUICK ACTIONS</div>',unsafe_allow_html=True)
    q1,q2,q3,q4,q5=st.columns(5)
    actions=[(q1,"🎯 SMART STOCK FINDER","SMART STOCK FINDER"),(q2,"🔥 CORE SETUP","VS FLOW SETUP"),(q3,"⚡ SMC 4H→5M","SMC 4H→5M SCALP"),(q4,"⛓️ OPTIONS","OPTIONS ANALYSIS"),(q5,"💀 HERO-ZERO","HERO-ZERO")]
    for box,label,target in actions:
        if box.button(label,use_container_width=True,key="quick_"+target): st.session_state.page=target; st.rerun()
    st.markdown('<div class="note">Professional workflow: Market Regime → Sector Strength → Smart Stock Finder → 4H/1H/15M/5M Core Setup → Options OI/PCR → CALL/PUT plan → manual chart confirmation → execution.</div>',unsafe_allow_html=True)

# =========================
# SMART STOCK FINDER
# =========================
elif page=="SMART STOCK FINDER":
    st.markdown('<div class="section">🎯 Smart Stock Finder <small>rank the Indian universe before opening charts</small></div>',unsafe_allow_html=True)
    st.markdown('<div class="note">This finder uses the same transparent research score: trend + EMA200 + RSI + volume expansion + 52W location. It is a shortlist engine, not a buy/sell guarantee.</div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: ex=st.selectbox("Exchange",["ALL","NSE","BSE"],key="finder_ex")
    with c2: direction=st.selectbox("Direction",["BOTH","BULLISH","BEARISH"],key="finder_dir")
    with c3: min_score=st.slider("Minimum score",0,100,60,5,key="finder_score")
    with c4: scan_n=st.selectbox("Scan universe",[25,50,100,200],index=1,key="finder_n")
    c5,c6,c7,c8=st.columns(4)
    with c5: min_vol=st.slider("Min Volume / 20D",0.5,3.0,1.0,0.1,key="finder_vol")
    with c6: max_high=st.slider("Max distance from 52W high %",2,50,15,key="finder_high")
    with c7: rsi_min=st.slider("RSI min",0,100,40,key="finder_rsimin")
    with c8: rsi_max=st.slider("RSI max",0,100,70,key="finder_rsimax")
    q=st.text_input("Optional symbol/company filter",key="finder_q",placeholder="e.g. BANK, TATA, RELIANCE")
    base=UNIV.copy()
    if ex!="ALL": base=base[base["exchange"]==ex]
    if q.strip():
        qq=q.strip().lower(); base=base[(base["symbol"].str.lower().str.contains(qq,regex=False,na=False))|(base["name"].str.lower().str.contains(qq,regex=False,na=False))]
    base=base.drop_duplicates(["exchange","symbol"]).head(int(scan_n))
    st.markdown(f'<div class="panel"><span class="pill green">{len(base):,} CANDIDATES</span><span class="pill">LOCAL SEARCH</span><span class="pill gold">LIVE OHLCV ON SCAN</span><br><br>Run the finder, then open only the strongest candidates for full VS FLOW MTF confirmation.</div>',unsafe_allow_html=True)
    if st.button("🎯 FIND BEST STOCKS NOW",use_container_width=True,key="finder_run"):
        rows=[]; bar=st.progress(0)
        for i,(_,r) in enumerate(base.iterrows()):
            snap=technical_snapshot(yf_ticker(r["symbol"],r["exchange"]))
            if snap:
                score,reasons=selection_score(snap)
                ok=(score>=min_score and snap["vol_ratio"]>=min_vol and snap["dist_high"]<=max_high and rsi_min<=snap["rsi"]<=rsi_max)
                if direction!="BOTH": ok=ok and snap["trend"]==direction
                if ok:
                    rows.append({"Symbol":r["symbol"],"Name":r["name"],"Exchange":r["exchange"],"Score":score,"Trend":snap["trend"],"RSI":round(snap["rsi"],1),"Vol×20D":round(snap["vol_ratio"],2),"52W High Dist %":round(snap["dist_high"],2),"Price":round(snap["price"],2),"Reasons":"; ".join(reasons)})
            bar.progress((i+1)/max(1,len(base)))
        bar.empty()
        out=pd.DataFrame(rows)
        if not out.empty:
            out=out.sort_values(["Score","Vol×20D"],ascending=[False,False]).reset_index(drop=True)
            st.session_state.finder_results=out
        else:
            st.session_state.finder_results=pd.DataFrame()
    if "finder_results" in st.session_state:
        out=st.session_state.finder_results
        if out.empty:
            st.info("No stock matched the current filters. Relax score / RSI / 52W filters or scan a larger universe.")
        else:
            st.success(f"{len(out)} stocks matched. Next step: open a candidate → run 4H → 1H → 15M → 5M VS FLOW confirmation.")
            st.dataframe(out,use_container_width=True,hide_index=True)
            st.download_button("⬇️ EXPORT SMART SHORTLIST",out.to_csv(index=False).encode(),file_name="VS_FLOW_SMART_STOCK_SHORTLIST.csv",mime="text/csv")
            opts=[f"{r.Symbol} • {r.Exchange}" for r in out.itertuples()]
            pick=st.selectbox("Open candidate",opts,key="finder_pick")
            if st.button("⚡ OPEN CANDIDATE DETAIL",use_container_width=True,key="finder_open"):
                rr=out.iloc[opts.index(pick)]
                st.session_state.selected=rr["Symbol"]; st.session_state.selected_exchange=rr["Exchange"]; st.session_state.page="STOCK DETAIL"; st.rerun()

# =========================
# ALL STOCKS
# =========================
elif page=="ALL INDIAN STOCKS":
    st.markdown('<div class="section">📈 All Indian Stocks <small>search first • load data only for selected stock</small></div>',unsafe_allow_html=True)
    f1,f2,f3=st.columns([2.2,1.2,1.2])
    with f1:
        q=st.text_input("Search company / symbol",value=st.session_state.get("stock_search",""))
        st.session_state.stock_search=q
    with f2:
        ex=st.selectbox("Exchange",["ALL","NSE","BSE"])
    with f3:
        show=st.selectbox("Show",["25","50","100","250"])
    d=UNIV.copy()
    if ex!="ALL": d=d[d["exchange"]==ex]
    if q.strip():
        qq=q.strip().lower()
        d=d[(d["symbol"].str.lower().str.contains(qq,regex=False,na=False))|(d["name"].str.lower().str.contains(qq,regex=False,na=False))]
    d=d.head(int(show))
    st.markdown(f'<div class="panel"><span class="pill green">{len(UNIV):,} TOTAL</span><span class="pill">NSE + BSE</span><span class="pill gold">SEARCH LOCAL = FAST</span><br><br>Pick a stock below. Live data is fetched only after opening it.</div>',unsafe_allow_html=True)
    if d.empty:
        st.warning("No matching stock.")
    else:
        for i,(_,r) in enumerate(d.iterrows()):
            c1,c2,c3,c4=st.columns([1.3,5,1,1])
            c1.markdown(f"**{r['symbol']}**")
            c2.write(r["name"])
            c3.markdown(f'<span class="pill">{r["exchange"]}</span>',unsafe_allow_html=True)
            if c4.button("OPEN",key=f"stock_open_{i}_{r['exchange']}_{r['symbol']}"):
                st.session_state.selected=r["symbol"]; st.session_state.selected_exchange=r["exchange"]; st.session_state.page="STOCK DETAIL"; st.rerun()

    st.markdown("---")
    if st.button("⚡ OPEN SELECTED STOCK DETAIL",use_container_width=True):
        st.session_state.page="STOCK DETAIL"; st.rerun()

# =========================
# STOCK DETAIL
# =========================
elif page=="STOCK DETAIL":
    sym=st.session_state.get("selected","RELIANCE")
    exch=st.session_state.get("selected_exchange","NSE")
    # resolve exchange if duplicate
    if not ((UNIV["symbol"]==sym)&(UNIV["exchange"]==exch)).any():
        row=UNIV[UNIV["symbol"]==sym].head(1)
        if not row.empty: exch=row.iloc[0]["exchange"]
    ticker=yf_ticker(sym,exch)
    meta=UNIV[(UNIV["symbol"]==sym)&(UNIV["exchange"]==exch)].head(1)
    name=meta.iloc[0]["name"] if not meta.empty else sym
    st.markdown(f'<div class="section">📌 {sym} <small>{name} • {exch}</small></div>',unsafe_allow_html=True)
    if st.button("← BACK TO ALL STOCKS",key="back_stocks"): st.session_state.page="ALL INDIAN STOCKS"; st.rerun()
    snap=technical_snapshot(ticker)
    if snap:
        score,reasons=selection_score(snap)
        m1,m2,m3,m4,m5=st.columns(5)
        m1.markdown(f'<div class="metric"><div class="k">LTP</div><div class="v">₹{snap["price"]:,.2f}</div></div>',unsafe_allow_html=True)
        m2.markdown(f'<div class="metric"><div class="k">TREND</div><div class="v">{snap["trend"]}</div></div>',unsafe_allow_html=True)
        m3.markdown(f'<div class="metric"><div class="k">RSI</div><div class="v">{snap["rsi"]:.1f}</div></div>',unsafe_allow_html=True)
        m4.markdown(f'<div class="metric"><div class="k">VOL / 20D</div><div class="v">{snap["vol_ratio"]:.2f}×</div></div>',unsafe_allow_html=True)
        m5.markdown(f'<div class="metric"><div class="k">SELECTION SCORE</div><div class="v">{score}/100</div></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="scorebar"><div style="width:{score}%"></div></div>',unsafe_allow_html=True)
        c1,c2=st.columns([1.8,1])
        with c1:
            h=history(ticker,"1y","1d")
            if not h.empty:
                st.line_chart(h["Close"],height=310,use_container_width=True)
        with c2:
            st.markdown('<div class="panel"><b>📊 Selection Factors</b></div>',unsafe_allow_html=True)
            for rr in reasons:
                st.markdown(f"✅ {rr}")
            st.markdown(f"**52W High:** ₹{snap['high52']:,.2f}<br>**52W Low:** ₹{snap['low52']:,.2f}<br>**EMA20:** ₹{snap['ema20']:,.2f}<br>**EMA50:** ₹{snap['ema50']:,.2f}<br>**EMA200:** ₹{snap['ema200']:,.2f}",unsafe_allow_html=True)
        st.markdown('<div class="section">🔥 VS FLOW Multi-Timeframe</div>',unsafe_allow_html=True)
        if st.button("RUN 4H → 1H → 15M → 5M SETUP",use_container_width=True):
            frames,overall=mtf_setup(ticker)
            st.session_state.last_mtf=(frames,overall)
        if "last_mtf" in st.session_state:
            frames,overall=st.session_state.last_mtf
            color="green" if overall=="BUY" else ("red" if overall=="SELL" else "gold")
            st.markdown(f'<div class="panel"><span class="pill {color}">OVERALL: {overall}</span></div>',unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(frames),use_container_width=True,hide_index=True)
    else:
        st.warning("Live market data unavailable for this symbol/provider right now. Search and universe remain available.")
    st.markdown('<div class="note">This is an algorithmic research aid. The 4H/1H/15M/5M components are OHLCV proxies and do not guarantee a trade outcome.</div>',unsafe_allow_html=True)

# =========================
# INDICES
# =========================
elif page=="INDIAN INDICES":
    st.markdown('<div class="section">🌐 Indian Indices <small>NIFTY • BANK NIFTY • SENSEX • sector indices</small></div>',unsafe_allow_html=True)
    q=st.text_input("Search index",value="")
    items=[(k,v) for k,v in INDEXES.items() if not q.strip() or q.lower() in k.lower() or q.lower() in v.lower()]
    for start in range(0,len(items),4):
        cols=st.columns(4)
        for j,(t,n) in enumerate(items[start:start+4]):
            r=quote(t)
            with cols[j]:
                if r:
                    cls="up" if r["chg"]>0 else ("down" if r["chg"]<0 else "flat")
                    st.markdown(f'<div class="card"><div class="label">{n}</div><div class="value">{r["price"]:,.2f}</div><div class="{cls}">{r["chg"]:+.2f}%</div></div>',unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="card"><div class="label">{n}</div><div class="value">—</div><div class="flat">Unavailable</div></div>',unsafe_allow_html=True)
                if st.button("OPEN",key=f"idx_{start}_{j}_{t}",use_container_width=True):
                    st.session_state.selected_index=t; st.session_state.page="INDEX DETAIL"; st.rerun()

elif page=="INDEX DETAIL":
    t=st.session_state.get("selected_index","^NSEI")
    n=INDEXES.get(t,t)
    st.markdown(f'<div class="section">🌐 {n}</div>',unsafe_allow_html=True)
    if st.button("← BACK TO INDICES",key="back_indices"): st.session_state.page="INDIAN INDICES"; st.rerun()
    r=quote(t)
    d=history(t,"1y","1d")
    if r:
        x,y,z=st.columns(3)
        x.metric("LTP",f"{r['price']:,.2f}",f"{r['chg']:+.2f}%")
        if not d.empty:
            y.metric("1Y HIGH",f"{d['High'].max():,.2f}")
            z.metric("1Y LOW",f"{d['Low'].min():,.2f}")
            st.line_chart(d["Close"],height=360,use_container_width=True)
        if st.button("RUN VS FLOW INDEX SETUP",use_container_width=True):
            frames,overall=mtf_setup(t)
            st.session_state.last_index_mtf=(frames,overall)
        if "last_index_mtf" in st.session_state:
            frames,overall=st.session_state.last_index_mtf
            st.markdown(f'<div class="panel"><span class="pill green">INDEX BIAS: {overall}</span></div>',unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(frames),use_container_width=True,hide_index=True)
    else:
        st.warning("Index data unavailable right now.")

# =========================
# VS FLOW SETUP SCANNER
# =========================
elif page=="STRATEGY LAB":
    st.markdown('<div class="section">🧠 STRATEGY LAB <small>5 complementary trading lenses • use confluence, not one signal</small></div>',unsafe_allow_html=True)
    st.markdown('<div class="note">Five strategy lenses are available: 1) Smart Money Concepts (SMC), 2) Price Action at Key Levels, 3) Breakout & Retest, 4) Fibonacci-Based Trading, 5) Indicator-Based Momentum. The engine is an OHLCV research proxy; it does not identify institutional intent with certainty.</div>',unsafe_allow_html=True)
    opts=sorted(set(CORE.keys()) | set(UNIV[UNIV["exchange"]=="NSE"]["symbol"].head(1000).tolist()))
    default=st.session_state.get("selected","RELIANCE"); idx=opts.index(default) if default in opts else 0
    c1,c2=st.columns([2,1])
    with c1: strat_sym=st.selectbox("Stock",opts,index=idx,key="strategy_stock")
    with c2: run=st.button("🧠 ANALYSE 5 STRATEGIES",use_container_width=True,key="strategy_run")
    if run:
        t=yf_ticker(strat_sym,"NSE")
        sdf,summary=strategy_suite(t); st.session_state.strategy_result=(strat_sym,sdf,summary)
    if "strategy_result" in st.session_state:
        sym,sdf,summary=st.session_state.strategy_result
        if not sdf.empty:
            cls="green" if summary["overall"]=="BUY" else "red" if summary["overall"]=="SELL" else "gold"
            st.markdown(f'<div class="panel"><span class="pill {cls}">COMBINED BIAS: {summary["overall"]}</span><span class="pill">Confidence {summary["confidence"]}%</span><span class="pill green">BUY {summary["buy"]}</span><span class="pill red">SELL {summary["sell"]}</span><br><br><b>{sym}</b> • Confluence across five strategy lenses</div>',unsafe_allow_html=True)
            st.dataframe(sdf,use_container_width=True,hide_index=True)
            st.markdown('<div class="section">📌 Strategy hierarchy</div>',unsafe_allow_html=True)
            st.markdown('<div class="panel"><b>Primary:</b> SMC → <b>Context:</b> Price Action → <b>Confirmation:</b> Breakout/Retest + Fibonacci → <b>Momentum filter:</b> RSI/EMA/Volume.<br><br><b>Trade rule:</b> Prefer setups where SMC and at least two additional lenses agree with the index/market regime. If signals conflict, WAIT.</div>',unsafe_allow_html=True)
    else:
        st.info("Select a stock and run the 5-strategy analysis.")


elif page=="SMC 4H→5M SCALP":
    st.markdown('<div class="section">⚡ SMC 4H→5M SCALP <small>separate HTF → LTF execution model</small></div>',unsafe_allow_html=True)
    st.markdown('<div class="note"><b>Exact model:</b> 4H HTF direction → 4H 50% equilibrium/premium-discount → 5M liquidity sweep → MSS → FVG → FVG retest → entry. This is deliberately separate from the VS FLOW Core Setup.</div>',unsafe_allow_html=True)
    stock_opts=sorted(set(CORE.keys()) | set(UNIV[UNIV["exchange"]=="NSE"]["symbol"].head(1000).tolist()))
    default=st.session_state.get("selected","RELIANCE")
    sym=st.selectbox("Stock",stock_opts,index=stock_opts.index(default) if default in stock_opts else 0,key="smc_scalp_stock")
    if st.button("⚡ ANALYSE SMC 4H→5M",use_container_width=True,key="smc_scalp_run"):
        row=UNIV[UNIV["symbol"]==sym].head(1); exch=row.iloc[0]["exchange"] if not row.empty else "NSE"; name=row.iloc[0].get("name",sym) if not row.empty else sym
        st.session_state.smc_scalp_result=smc_scalp_analyze(yf_ticker(sym,exch),name)
    r=st.session_state.get("smc_scalp_result")
    if r:
        side="BUY" if "BUY" in r.get("Signal","") else "SELL" if "SELL" in r.get("Signal","") else "WAIT"
        color="green" if side=="BUY" else "red" if side=="SELL" else "gold"
        st.markdown(f'<div class="panel"><span class="pill {color}">{r.get("Signal","WAIT")}</span> <span class="pill">Score {r.get("Score","0/6")}</span><br><br><b>{r.get("Symbol",sym)}</b> • {r.get("Name",sym)}<br><br><b>Entry:</b> {r.get("Entry") or "—"} &nbsp; <b>SL:</b> {r.get("SL") or "—"} &nbsp; <b>TP:</b> {r.get("TP") or "—"} &nbsp; <b>RR:</b> {r.get("RR") or "—"}</div>',unsafe_allow_html=True)
        cols=["4H Direction","4H Zone","5M Sweep","5M MSS","5M FVG","FVG Retest","Score","Signal","Entry","SL","TP","RR"]
        st.dataframe(pd.DataFrame([{k:r.get(k,"") for k in cols}]),use_container_width=True,hide_index=True)
        st.markdown('<div class="section">⚡ SMC Execution Checklist</div>',unsafe_allow_html=True)
        a,b,c,d,e,f=st.columns(6)
        items=[("4H DIRECTION",r["4H Direction"]),("4H ZONE",r["4H Zone"]),("LIQUIDITY SWEEP",r["5M Sweep"]),("MSS",r["5M MSS"]),("FVG",r["5M FVG"]),("FVG RETEST",r["FVG Retest"])]
        for col,(k,v) in zip([a,b,c,d,e,f],items): col.markdown(f'<div class="metric"><div class="k">{k}</div><div class="v" style="font-size:13px">{v}</div></div>',unsafe_allow_html=True)
        st.markdown('<div class="note"><b>Preferred setup:</b> BUY = 4H bullish + discount, then 5M sell-side liquidity sweep → bullish MSS → bullish FVG → FVG retest. SELL is the inverse. A 4/6 result is a watchlist candidate; 5/6 or 6/6 is stronger research confirmation. Manual chart confirmation remains required.</div>',unsafe_allow_html=True)
    else:
        st.info("Select a stock and run the separate SMC 4H→5M analysis.")

elif page=="CLASSIC PRICE ACTION":
    st.markdown('<div class="section">📐 CLASSIC PRICE ACTION DESK <small>Key Levels • Trendline S/R • Breakout/Breakdown • Price Action • Candle Close</small></div>',unsafe_allow_html=True)
    st.markdown('<div class="note"><b>Your established setup:</b> Key levels + trendline support/resistance + breakout/breakdown + price action + candle-close confirmation. This is kept separate from the VS FLOW SMC Core Setup so you can compare both lenses without mixing rules.</div>',unsafe_allow_html=True)
    stock_opts=sorted(set(CORE.keys()) | set(UNIV[UNIV["exchange"]=="NSE"]["symbol"].head(500).tolist()))
    default=st.session_state.get("selected","RELIANCE")
    sym=st.selectbox("Stock",stock_opts,index=stock_opts.index(default) if default in stock_opts else 0)
    if st.button("📐 ANALYSE CLASSIC SETUP",use_container_width=True):
        row=UNIV[UNIV["symbol"]==sym].head(1); exch=row.iloc[0]["exchange"] if not row.empty else "NSE"; name=row.iloc[0].get("name",sym) if not row.empty else sym
        r=classic_analyze(yf_ticker(sym,exch),name); st.session_state.classic_result=r
    r=st.session_state.get("classic_result")
    if r:
        side="BUY" if "BUY" in r.get("Signal","") else "SELL" if "SELL" in r.get("Signal","") else "WAIT"
        color="green" if side=="BUY" else "red" if side=="SELL" else "gold"
        st.markdown(f'<div class="panel"><span class="pill {color}">{r.get("Signal","WAIT")}</span> <span class="pill">Score {r.get("Score","0/6")}</span><br><br><b>{r.get("Symbol",sym)}</b> • {r.get("Name",sym)}<br><br><b>Entry:</b> {r.get("Entry") or "—"} &nbsp; <b>SL:</b> {r.get("SL") or "—"} &nbsp; <b>TP:</b> {r.get("TP") or "—"} &nbsp; <b>RR:</b> {r.get("RR") or "—"}</div>',unsafe_allow_html=True)
        cols=["Key Level","Trendline","Breakout/Breakdown","Price Action","Candle Close","Score","Signal","Entry","SL","TP","RR"]
        st.dataframe(pd.DataFrame([{k:r.get(k,"") for k in cols}]),use_container_width=True,hide_index=True)
        st.markdown('<div class="section">📋 Classic Setup Checklist</div>',unsafe_allow_html=True)
        a,b,c,d,e=st.columns(5)
        items=[("KEY LEVEL",r["Key Level"]),("TRENDLINE",r["Trendline"]),("BREAKOUT",r["Breakout/Breakdown"]),("PRICE ACTION",r["Price Action"]),("CANDLE CLOSE",r["Candle Close"])]
        for col,(k,v) in zip([a,b,c,d,e],items):
            col.markdown(f'<div class="metric"><div class="k">{k}</div><div class="v" style="font-size:14px">{v}</div></div>',unsafe_allow_html=True)
        st.markdown('<div class="note"><b>Rule:</b> Do not enter on a wick-only breakout. Prefer a confirmed candle close beyond the key level, then retest/continuation where applicable. Use the classic setup as a separate confirmation lens alongside—not instead of—the VS FLOW Core Setup.</div>',unsafe_allow_html=True)

elif page=="HERO-ZERO":
    st.markdown('<div class="section">💀 HERO-ZERO TRADE DESK <small>separate high-risk options scanner • cheap OTM premium only</small></div>',unsafe_allow_html=True)
    st.markdown('<div class="note"><b>Separate risk bucket:</b> Hero-Zero is not mixed with normal premium trades. It searches inexpensive OTM options with minimum liquidity/positioning filters. This is a high-risk research screen, not a guaranteed trade.</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([1.1,1.4,1.4])
    with c1: hz_kind=st.selectbox("Instrument",["Index","Stock"],key="hz_kind")
    with c2:
        if hz_kind=="Index":
            hz_symbol=st.selectbox("Underlying",["NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY","SENSEX","NIFTYNXT50"],key="hz_symbol")
        else:
            hz_opts=sorted(set(CORE.keys()) | set(UNIV[UNIV["exchange"]=="NSE"]["symbol"].head(500).tolist()))
            hz_symbol=st.selectbox("Stock",hz_opts,index=hz_opts.index(st.session_state.get("selected","RELIANCE")) if st.session_state.get("selected","RELIANCE") in hz_opts else 0,key="hz_stock")
    kind="Indices" if hz_kind=="Index" else "Equity"
    exps,err=nse_option_expiries(hz_symbol,kind)
    with c3:
        hz_exp=st.selectbox("Expiry",exps,key="hz_exp") if exps else st.text_input("Expiry (DD-MMM-YYYY)",key="hz_exp_text")
    raw_hz=st.text_area("Optional NSE JSON fallback",height=75,placeholder="Paste NSE option-chain JSON if live fetch is blocked",key="hz_json")
    b1,b2=st.columns(2)
    with b1: hz_fetch=st.button("💀 SCAN HERO-ZERO",use_container_width=True)
    with b2: hz_paste=st.button("📋 ANALYSE PASTED CHAIN",use_container_width=True)
    if hz_fetch and hz_exp:
        raw,e=nse_option_chain(hz_symbol,hz_exp,kind)
        if raw is not None:
            hzdf,hzmeta=option_rows(raw); st.session_state.hz_oc=(hzdf,hzmeta)
        else: st.error("NSE fetch failed. Use pasted JSON fallback. "+str(e))
    if hz_paste and raw_hz.strip():
        hzdf,hzmeta=parse_pasted_chain(raw_hz); st.session_state.hz_oc=(hzdf,hzmeta)
    if "hz_oc" in st.session_state:
        hzdf,hzmeta=st.session_state.hz_oc
        if not hzdf.empty:
            hzana=option_analysis(hzdf,hzmeta.get("spot")); cand=hero_zero_candidates(hzdf,hzana)
            m=st.columns(6)
            vals=[("SPOT",hzana["spot"]),("ATM",hzana["atm"]),("PCR",f'{hzana["pcr"]:.2f}'),("BIAS",hzana["bias"]),("CALL WALL",hzana["call_wall"]),("PUT WALL",hzana["put_wall"]) ]
            for col,(k,v) in zip(m,vals): col.markdown(f'<div class="metric"><div class="k">{k}</div><div class="v">{v}</div></div>',unsafe_allow_html=True)
            st.markdown('<div class="section">🎯 Best Hero-Zero Candidate</div>',unsafe_allow_html=True)
            if not cand.empty:
                top=cand.iloc[0]
                cls="green" if top["Side"]=="CALL" else "red"
                st.markdown(f'<div class="panel"><span class="pill {cls}">{top["Side"]} • {top["Strike"]:g} • HERO-ZERO</span> <span class="pill">Score {int(top["Score"])}/100</span><br><br><b>Premium:</b> ₹{top["Premium"]:.2f} &nbsp; <b>Entry:</b> ₹{top["Entry"]:.2f} &nbsp; <b>SL:</b> ₹{top["SL"]:.2f} &nbsp; <b>TP1:</b> ₹{top["TP1"]:.2f} &nbsp; <b>TP2:</b> ₹{top["TP2"]:.2f}<br><br><b>OI:</b> {int(top["OI"]):,} &nbsp; <b>Change OI:</b> {int(top["Change OI"]):+,} &nbsp; <b>Volume:</b> {int(top["Volume"]):,} &nbsp; <b>IV:</b> {top["IV"]:.2f}% &nbsp; <b>Distance:</b> {top["Distance %"]:.2f}%<br><br><b>RR:</b> {top["RR"]}</div>',unsafe_allow_html=True)
                st.markdown('<div class="section">💀 Hero-Zero Candidates</div>',unsafe_allow_html=True)
                st.dataframe(cand,use_container_width=True,hide_index=True)
            else:
                st.warning("No Hero-Zero candidate passed the premium, OTM distance and liquidity filters.")
            st.markdown('<div class="note"><b>Risk controls:</b> Hero-Zero can lose most/all of the premium rapidly because of theta, IV and gamma effects. Do not treat a low premium as low risk. Prefer underlying VS FLOW confirmation and never override the Core Setup because of an option-chain signal alone.</div>',unsafe_allow_html=True)
    else:
        st.info("Run the Hero-Zero scan or paste an NSE option-chain JSON to begin.")

elif page=="OPTIONS ANALYSIS":
    st.markdown('<div class="section">⛓️ Option Chain Analysis <small>OI • Change OI • PCR • Max Pain • Call/Put decision</small></div>',unsafe_allow_html=True)
    st.markdown('<div class="note">NSE option-chain data is fetched on demand. If NSE blocks a server request, paste the JSON downloaded/copied from the NSE Option Chain page. Signals are research outputs, not guaranteed trades.</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([1.2,1.2,1.4])
    with c1: oc_kind=st.selectbox("Instrument",["Index","Stock"])
    with c2:
        if oc_kind=="Index":
            oc_symbol=st.selectbox("Underlying",["NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY","NIFTYNXT50"])
        else:
            stock_opts=sorted(set(CORE.keys()) | set(UNIV[UNIV["exchange"]=="NSE"]["symbol"].head(500).tolist()))
            oc_symbol=st.selectbox("Stock",stock_opts,index=stock_opts.index(st.session_state.get("selected","RELIANCE")) if st.session_state.get("selected","RELIANCE") in stock_opts else 0)
    kind="Indices" if oc_kind=="Index" else "Equity"
    exps,err=nse_option_expiries(oc_symbol,kind)
    if exps:
        expiry=st.selectbox("Expiry",exps)
    else:
        expiry=st.text_input("Expiry (DD-MMM-YYYY)",value="")
        if err: st.warning("Expiry list unavailable. Enter expiry manually or use pasted NSE JSON.")
    raw_text=st.text_area("Optional: paste NSE option-chain JSON if live fetch is blocked",height=90,placeholder='Paste raw JSON from NSE option-chain API here...')
    b1,b2=st.columns(2)
    with b1: fetch=st.button("⚡ FETCH OPTION CHAIN",use_container_width=True)
    with b2: use_paste=st.button("📋 ANALYSE PASTED JSON",use_container_width=True)
    if fetch and expiry:
        raw,e=nse_option_chain(oc_symbol,expiry,kind)
        if raw is not None:
            df,meta=option_rows(raw); st.session_state.oc=(df,meta)
        else: st.error("NSE fetch failed. Use the paste-JSON fallback. "+str(e))
    if use_paste and raw_text.strip():
        df,meta=parse_pasted_chain(raw_text); st.session_state.oc=(df,meta)
    if "oc" in st.session_state:
        df,meta=st.session_state.oc
        if not df.empty:
            ana=option_analysis(df,meta.get("spot")); plan=trade_plan(df,ana)
            m=st.columns(7)
            vals=[("SPOT",ana["spot"]),("ATM",ana["atm"]),("PCR",f'{ana["pcr"]:.2f}'),("CALL OI",f'{ana["call_oi"]:,.0f}'),("PUT OI",f'{ana["put_oi"]:,.0f}'),("MAX PAIN",ana["max_pain"]),("BIAS",ana["bias"])]
            for col,(k,v) in zip(m,vals): col.markdown(f'<div class="metric"><div class="k">{k}</div><div class="v">{v}</div></div>',unsafe_allow_html=True)
            st.markdown('<div class="section">📊 Option Chain</div>',unsafe_allow_html=True)
            view=df.copy(); atm=ana["atm"]; view=view[(view["STRIKE"]>=atm-10*(view["STRIKE"].diff().abs().median() or 1))&(view["STRIKE"]<=atm+10*(view["STRIKE"].diff().abs().median() or 1))].copy()
            st.dataframe(view[["CE_OI","CE_CHG_OI","CE_VOL","CE_IV","CE_LTP","CE_CHG","STRIKE","PE_CHG","PE_LTP","PE_IV","PE_VOL","PE_CHG_OI","PE_OI"]],use_container_width=True,hide_index=True)
            x,y,z=st.columns(3)
            x.markdown(f'<div class="panel"><b>CALL WALL</b><h3>{ana["call_wall"]:,.0f}</h3><small>Highest CE OI = potential resistance</small></div>',unsafe_allow_html=True)
            y.markdown(f'<div class="panel"><b>PUT WALL</b><h3>{ana["put_wall"]:,.0f}</h3><small>Highest PE OI = potential support</small></div>',unsafe_allow_html=True)
            z.markdown(f'<div class="panel"><b>CHANGE OI</b><h3>CE {ana["call_chg_oi"]:+,.0f} | PE {ana["put_chg_oi"]:+,.0f}</h3><small>Fresh positioning clue</small></div>',unsafe_allow_html=True)
            st.markdown('<div class="section">🎯 VS FLOW Options Trade Plan</div>',unsafe_allow_html=True)
            if plan and plan.get("side")!="WAIT":
                color="green" if plan["side"]=="CALL" else "red"
                st.markdown(f'<div class="panel"><span class="pill {color}">{plan["side"]} • {plan["option"]}</span> <span class="pill">Confidence {ana["confidence"]}%</span> <span class="pill gold">{plan["class"]}</span><br><br><b>Entry:</b> ₹{plan["entry"]:.2f} &nbsp; <b>SL:</b> ₹{plan["sl"]:.2f} &nbsp; <b>TP1:</b> ₹{plan["tp1"]:.2f} &nbsp; <b>TP2:</b> ₹{plan["tp2"]:.2f}<br><br>{plan["reason"]}. Underlying spot ₹{ana["spot"]:,.2f}; support {ana["put_wall"]:,.0f}; resistance {ana["call_wall"]:,.0f}; max pain {ana["max_pain"]:,.0f}.</div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="panel"><span class="pill gold">WAIT</span> No clean directional edge from the current option-chain structure.</div>',unsafe_allow_html=True)
            st.markdown('<div class="note"><b>Hero-Zero rule:</b> very cheap OTM options can have extreme theta/IV/gamma risk. The label is a risk classification, not a recommendation to buy a zero-premium option. Confirm the underlying VS FLOW 4H→1H→15M→5M setup before execution.</div>',unsafe_allow_html=True)
        else:
            st.info("No option-chain rows loaded yet.")

elif page=="VS FLOW OB + TREND":
    ob_trend_page()

elif page=="VS FLOW SETUP":
    st.markdown('<div class="section">🔥 VS FLOW CORE SETUP <small>strict 4H → 1H → 15M → 5M • 4/5 actionable • 5/5 A+</small></div>',unsafe_allow_html=True)
    st.markdown('<div class="note">This is the actual VS FLOW Core Setup board: 4H Order Block → 1H Liquidity Sweep/BOS → 15M FVG → 5M Trigger. The optional liquidity sweep is the 5th point for A+.</div>',unsafe_allow_html=True)
    mode=st.radio("Universe",["My symbols","Top 100 India core","Top 100 from universe"],horizontal=True)
    if mode=="My symbols":
        raw=st.text_area("Symbols (one per line / comma separated)","RELIANCE\nTCS\nHDFCBANK\nICICIBANK\nSBIN")
        syms=[x for x in re.split(r"[\n,; ]+",raw.upper()) if x]
    elif mode=="Top 100 India core": syms=list(CORE)[:100]
    else: syms=UNIV["symbol"].drop_duplicates().head(100).tolist()
    limit=st.slider("Core scan limit",5,min(100,max(10,len(syms))),min(100,len(syms)))
    if st.button("🚀 SCAN NOW",use_container_width=True):
        rows=[]; bar=st.progress(0); chosen=syms[:limit]
        for i,sym in enumerate(chosen):
            row=UNIV[UNIV["symbol"]==sym].head(1); exch=row.iloc[0]["exchange"] if not row.empty else "NSE"
            ticker=yf_ticker(sym,exch); name=row.iloc[0].get("name",sym) if not row.empty else sym
            r=core_analyze(ticker,name); r["Symbol"]=sym; r["Exchange"]=exch; rows.append(r); bar.progress((i+1)/max(1,len(chosen)))
        bar.empty()
        st.session_state.core_scan=pd.DataFrame(rows)
    df=st.session_state.get("core_scan",pd.DataFrame())
    if not df.empty:
        hits=df[df["Score"].astype(str).str.startswith(("4/5","5/5"))].copy()
        a5=int((hits["Score"]=="5/5").sum())
        st.success(f"Scan complete • {len(df)} assets • {len(hits)} setup(s) • {a5} new 5/5 A+ alert(s)")
        if not hits.empty:
            st.success(f"{len(hits)} actionable setup(s) found • 4/5 is eligible for manual chart tally")
            cols=["Symbol","Name","4H OB","1H Sweep","1H BOS","15M FVG","5M Trigger","Score","Signal","Entry","SL","TP","RR","Chart Tally"]
            st.dataframe(hits[cols],use_container_width=True,hide_index=True)
            c1,c2=st.columns(2)
            with c1: st.download_button("⬇️ DOWNLOAD SETUPS CSV",hits.to_csv(index=False).encode(),file_name="VS_FLOW_CORE_SETUPS.csv",mime="text/csv",use_container_width=True)
            with c2: st.download_button("📋 COPY / SHARE SETUPS TXT",hits.to_csv(index=False,sep="|").encode(),file_name="VS_FLOW_CORE_SETUPS.txt",mime="text/plain",use_container_width=True)
        else: st.warning("No 4/5+ Core Setup in the latest scan.")
        with st.expander("Show all scanned assets"): st.dataframe(df,use_container_width=True,hide_index=True)
    st.markdown('<div class="panel"><b>VS FLOW Core Setup</b><br>1) 4H OB → 2) 1H Sweep/BOS → 3) 15M FVG → 4) 5M Trigger → 5) Liquidity alignment = A+.</div>',unsafe_allow_html=True)

st.markdown('<div style="margin-top:30px;border-top:1px solid #14384f;padding-top:12px;color:#668096;font-size:10px">VS FLOW INDIA V55 • All Indian Stocks + Smart Finder + Indices + Core + OB + Trend + SMC 4H→5M + Classic + Options + Hero-Zero + Strategy Lab • Built for vaibhav shirsat • Educational / research use only</div>',unsafe_allow_html=True)
