from pathlib import Path
import json, math, io
import requests
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="VS FLOW INDIA", page_icon="🇮🇳", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 10% 0%,rgba(14,165,233,.13),transparent 30%),radial-gradient(circle at 90% 5%,rgba(124,58,237,.12),transparent 28%),#060b13;color:#e5eef9}
.block-container{max-width:1800px;padding:1rem 1.2rem 2.5rem}
.vsf-title{font-size:42px;font-weight:950;letter-spacing:4px;line-height:1;background:linear-gradient(90deg,#fff,#7dd3fc,#a78bfa,#22d3ee);-webkit-background-clip:text;color:transparent}
.vsf-sub{font-size:11px;font-weight:800;letter-spacing:2px;opacity:.62;margin-top:7px}
.line{height:2px;margin:14px 0 18px;background:linear-gradient(90deg,#22d3ee,#6366f1,#a855f7,transparent);border-radius:99px}
.card{border:1px solid rgba(148,163,184,.15);border-radius:16px;padding:14px 16px;background:linear-gradient(145deg,rgba(20,35,55,.85),rgba(8,16,29,.82));box-shadow:0 10px 30px rgba(0,0,0,.2);min-height:98px}
.kpi{font-size:25px;font-weight:900;margin-top:6px}.muted{font-size:11px;opacity:.62}
.green{border-left:4px solid #22c55e}.red{border-left:4px solid #ef4444}.cyan{border-left:4px solid #06b6d4}.gold{border-left:4px solid #f59e0b}.purple{border-left:4px solid #a855f7}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#07101c,#0c1421,#07101c);border-right:1px solid rgba(148,163,184,.13)}
button{border-radius:9px!important} button[kind="primary"]{background:linear-gradient(90deg,#0ea5e9,#7c3aed)!important;border:0!important}
div[data-testid="stDataFrame"]{border:1px solid rgba(148,163,184,.15);border-radius:12px;overflow:hidden}
[data-testid="stMetric"]{background:rgba(15,23,42,.45);border:1px solid rgba(148,163,184,.10);padding:9px 11px;border-radius:12px}
</style>
""", unsafe_allow_html=True)

# ----------------------------- INDIAN UNIVERSE -----------------------------
INDEXES = {
    "NIFTY 50":"^NSEI", "BANK NIFTY":"^NSEBANK", "NIFTY IT":"^CNXIT", "NIFTY PHARMA":"^CNXPHARMA",
    "NIFTY AUTO":"^CNXAUTO", "NIFTY FMCG":"^CNXFMCG", "NIFTY METAL":"^CNXMETAL"
}
CORE = {
"RELIANCE.NS":"Reliance Industries","HDFCBANK.NS":"HDFC Bank","ICICIBANK.NS":"ICICI Bank","SBIN.NS":"State Bank of India","TCS.NS":"TCS","INFY.NS":"Infosys","AXISBANK.NS":"Axis Bank","KOTAKBANK.NS":"Kotak Mahindra Bank","LT.NS":"Larsen & Toubro","TATAMOTORS.NS":"Tata Motors","BHARTIARTL.NS":"Bharti Airtel","ITC.NS":"ITC","MARUTI.NS":"Maruti Suzuki","M&M.NS":"Mahindra & Mahindra","BAJFINANCE.NS":"Bajaj Finance","BAJAJFINSV.NS":"Bajaj Finserv","HCLTECH.NS":"HCL Technologies","WIPRO.NS":"Wipro","SUNPHARMA.NS":"Sun Pharma","ADANIENT.NS":"Adani Enterprises","ADANIPORTS.NS":"Adani Ports","COALINDIA.NS":"Coal India","POWERGRID.NS":"Power Grid","NTPC.NS":"NTPC","ONGC.NS":"ONGC","TATASTEEL.NS":"Tata Steel","JSWSTEEL.NS":"JSW Steel","HINDALCO.NS":"Hindalco","ULTRACEMCO.NS":"UltraTech Cement","ASIANPAINT.NS":"Asian Paints","HINDUNILVR.NS":"Hindustan Unilever","NESTLEIND.NS":"Nestle India","TITAN.NS":"Titan","TECHM.NS":"Tech Mahindra","DRREDDY.NS":"Dr Reddy's","CIPLA.NS":"Cipla","EICHERMOT.NS":"Eicher Motors","HEROMOTOCO.NS":"Hero MotoCorp","APOLLOHOSP.NS":"Apollo Hospitals","BEL.NS":"Bharat Electronics","HAL.NS":"Hindustan Aeronautics","IRCTC.NS":"IRCTC","TRENT.NS":"Trent","JIOFIN.NS":"Jio Financial","INDUSINDBK.NS":"IndusInd Bank","BANKBARODA.NS":"Bank of Baroda","PNB.NS":"Punjab National Bank","CANBK.NS":"Canara Bank","IDFCFIRSTB.NS":"IDFC First Bank"
}
BSE_CORE = {k.replace('.NS','.BO'):v for k,v in list(CORE.items())[:25]}
ALL = {**INDEXES, **CORE, **BSE_CORE}

SECTIONS = {
    "Market Overview": ["Dashboard", "Market Pulse", "Indices"],
    "Stock Research": ["All Stocks", "Gainers / Losers", "Most Active", "ATH / ATL", "52W High / Low", "Penny Stocks"],
    "Smart Scanner": ["Smart Stock Finder", "🔥 Multibagger Hunter"],
    "Scanners": ["VS FLOW Scalper", "VS FLOW Scanner", "VS FLOW OB + Trend", "VS FLOW EARLY", "Breakout / Breakdown", "Reversal Scanner", "Chart Patterns", "Candlestick Patterns", "Technical Scanner", "Fundamental Scanner", "Potential Multibagger"],
    "Institutional": ["FII / DII", "Options", "IPO / Listings", "Earnings / Events"],
    "Tools": ["Chart", "Watchlist", "Risk Calculator"]
}



# ----------------------------- VS FLOW SCALPER V1 -----------------------------
def vsflow_scalper_v1(symbol):
    """Price-action-first scalp radar. EMA/VWAP are filters, not entry triggers.
    Score: trend, VWAP, liquidity sweep, displacement, first pullback, RR room.
    5M is the scanner timeframe; 1M confirmation remains manual.
    """
    x=get_data(symbol,"5m","5d")
    base={"Symbol":symbol,"Name":ALL.get(symbol,"Custom"),"Bias":"WAIT","Score":"0/6","Status":"🔴 NO TRADE","Trigger":"WAIT","EMA":"WAIT","VWAP":"WAIT","Liquidity":"WAIT","Displacement":"WAIT","Pullback":"WAIT","Entry":"","SL":"","TP":"","RR":""}
    if x.empty or len(x)<60:
        base["Status"]="⚪ NO DATA"; return base
    x=x.copy(); c=x.Close.astype(float); h=x.High.astype(float); l=x.Low.astype(float); o=x.Open.astype(float); v=x.Volume.astype(float)
    e9=c.ewm(span=9,adjust=False).mean(); e20=c.ewm(span=20,adjust=False).mean()
    tp=(h+l+c)/3; volsum=v.replace(0,1).cumsum(); vwap=(tp*v).cumsum()/volsum
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1); atr=tr.rolling(14).mean()
    body=(c-o).abs(); med=float(body.tail(30).median()) or 1e-9; a=float(atr.iloc[-1]) if pd.notna(atr.iloc[-1]) else float((h-l).tail(14).mean())
    price=float(c.iloc[-1]); side="BUY" if e9.iloc[-1]>e20.iloc[-1] and e9.iloc[-1]>e9.iloc[-4] and e20.iloc[-1]>=e20.iloc[-4] else "SELL" if e9.iloc[-1]<e20.iloc[-1] and e9.iloc[-1]<e9.iloc[-4] and e20.iloc[-1]<=e20.iloc[-4] else "WAIT"
    score=0; reasons=[]
    ema_ok=side in ("BUY","SELL"); score+=ema_ok; base["EMA"]=f"{side} • 9/20 slope" if ema_ok else "WAIT"
    vwap_ok=(side=="BUY" and price>float(vwap.iloc[-1])) or (side=="SELL" and price<float(vwap.iloc[-1])); score+=vwap_ok; base["VWAP"]="ALIGNED" if vwap_ok else "NOT ALIGNED"
    n=10; prev_hi=float(h.iloc[-n-1:-1].max()); prev_lo=float(l.iloc[-n-1:-1].min()); last=x.iloc[-1]
    sweep=(side=="BUY" and float(last.Low)<prev_lo and price>prev_lo) or (side=="SELL" and float(last.High)>prev_hi and price<prev_hi); score+=sweep; base["Liquidity"]="SSL SWEPT" if sweep and side=="BUY" else "BSL SWEPT" if sweep else "WAIT"
    disp=(side=="BUY" and float(last.Close)>float(last.Open) and float(body.iloc[-1])>=1.25*med and float(last.Close)>=float(last.High)-0.25*max(float(last.High-last.Low),1e-9)) or (side=="SELL" and float(last.Close)<float(last.Open) and float(body.iloc[-1])>=1.25*med and float(last.Close)<=float(last.Low)+0.25*max(float(last.High-last.Low),1e-9)); score+=disp; base["Displacement"]="STRONG" if disp else "WAIT"
    # First pullback: price recently expanded, then returned toward 9 EMA without invalidating the trend.
    recent=x.tail(8); touch=((recent.Low<=e9.tail(8)) & (recent.High>=e9.tail(8))).any(); not_extended=(abs(price-float(e9.iloc[-1]))<=max(a*0.75, price*0.0015)); pull=ema_ok and touch and not_extended and ((side=="BUY" and price>=float(e20.iloc[-1])) or (side=="SELL" and price<=float(e20.iloc[-1]))); score+=pull; base["Pullback"]="FIRST PULLBACK" if pull else "WAIT"
    risk=max(a*0.7, price*0.001); sl=price-risk if side=="BUY" else price+risk; tp2=price+2*risk if side=="BUY" else price-2*risk
    room=score>=4 and risk>0; score+=room; base["RR"]="1:2 ROOM" if room else "WAIT"
    base["Bias"]=side; base["Score"]=f"{int(score)}/6"
    if score>=5 and disp and pull:
        base["Status"]="🟢 A+ SCALP"; base["Trigger"]="CONFIRM ON 1M → ENTRY"
    elif score>=4:
        base["Status"]="🟡 WATCH"; base["Trigger"]="WAIT FOR 1M CONFIRMATION"
    else:
        base["Status"]="🔴 NO TRADE"; base["Trigger"]="WAIT"
    if score>=4:
        base.update({"Entry":round(price,4),"SL":round(sl,4),"TP":round(tp2,4)})
    return base

# ----------------------------- VS FLOW EARLY UNIVERSE -----------------------------
# Dedicated early-ignition universe: 100 stocks + 7 major indices from the current VS FLOW OB + TREND radar universe.
EARLY_STOCKS = {
    "JSWSTEEL": "JSW Steel",
    "KOTAKBANK": "Kotak Mahindra Bank",
    "GAIL": "GAIL (India) Limited",
    "PNB": "Punjab National Bank",
    "ETERNAL": "ETERNAL LIMITED",
    "HDFCAMC": "HDFC Asset Management Company Limited",
    "HDFCBANK": "HDFC Bank",
    "MAXHEALTH": "Max Healthcare",
    "DMART": "Avenue Supermarts",
    "BAJAJ-AUTO": "Bajaj Auto",
    "BANKBARODA": "Bank of Baroda",
    "CANBK": "Canara Bank",
    "DRREDDY": "Dr Reddy's Laboratories",
    "HYUNDAI": "Hyundai Motor India Limited",
    "JINDALSTEL": "JINDAL STEEL LIMITED",
    "POWERGRID": "Power Grid",
    "SBILIFE": "SBI Life Insurance",
    "SHREECEM": "SHREE CEMENT LIMITED",
    "UNIONBANK": "Union Bank of India",
    "ZYDUSLIFE": "Zydus Lifesciences",
    "ADANIGREEN": "Adani Green Energy Limited",
    "ASIANPAINT": "Asian Paints",
    "CGPOWER": "CG Power and Industrial Solutions Limited",
    "CIPLA": "Cipla",
    "HDFCLIFE": "HDFC Life Insurance",
    "HINDUNILVR": "Hindustan Unilever",
    "ITC": "ITC",
    "IOC": "Indian Oil",
    "IRFC": "IRFC",
    "JIOFIN": "Jio Financial Services",
    "ONGC": "ONGC",
    "ENRIN": "Siemens Energy India Limited",
    "TATASTEEL": "Tata Steel",
    "ULTRACEMCO": "UltraTech Cement",
    "VBL": "Varun Beverages",
    "NTPC": "NTPC",
    "M&M": "Mahindra & Mahindra",
    "TATACONSUM": "TATA CONSUMER PRODUCTS LIMITED",
    "BOSCHLTD": "Bosch Limited",
    "HINDZINC": "Hindustan Zinc",
    "LODHA": "Lodha Developers Limited",
    "TECHM": "Tech Mahindra",
    "TITAN": "Titan Company",
    "TORNTPHARM": "Torrent Pharmaceuticals",
    "ABB": "ABB India",
    "BAJFINANCE": "Bajaj Finance",
    "BHARTIARTL": "Bharti Airtel",
    "EICHERMOT": "Eicher Motors",
    "INDHOTEL": "Indian Hotels",
    "MAZDOCK": "Mazagon Dock Shipbuilders Limited",
    "TCS": "Tata Consultancy Services",
    "BPCL": "Bharat Petroleum",
    "HCLTECH": "HCL Technologies",
    "ICICIBANK": "ICICI Bank",
    "RELIANCE": "Reliance Industries",
    "TVSMOTOR": "TVS Motor",
    "APOLLOHOSP": "Apollo Hospitals",
    "BAJAJHLDNG": "Bajaj Holdings & Investment Limited",
    "BEL": "Bharat Electronics",
    "RECLTD": "REC Limited",
    "SIEMENS": "Siemens India",
    "ADANIENT": "Adani Enterprises",
    "LT": "Larsen & Toubro",
    "PIDILITIND": "Pidilite Industries",
    "SBIN": "State Bank of India",
    "SUNPHARMA": "Sun Pharmaceutical",
    "GRASIM": "Grasim Industries Limited",
    "DIVISLAB": "Divi's Laboratories",
    "HAL": "Hindustan Aeronautics",
    "BRITANNIA": "Britannia Industries",
    "GODREJCP": "Godrej Consumer Products",
    "MARUTI": "Maruti Suzuki",
    "TRENT": "Trent",
    "WIPRO": "Wipro",
    "CUMMINSIND": "Cummins India Limited",
    "MUTHOOTFIN": "Muthoot Finance Limited",
    "VEDL": "Vedanta",
    "INDIGO": "InterGlobe Aviation",
    "NESTLEIND": "Nestle India",
    "SHRIRAMFIN": "Shriram Finance",
    "COALINDIA": "Coal India",
    "ADANIENSOL": "Adani Energy Solutions Limited",
    "CHOLAFIN": "Cholamandalam Investment and Finance Company Limited",
    "DLF": "DLF",
    "INFY": "Infosys",
    "LTM": "LTM Limited",
    "MOTHERSON": "Samvardhana Motherson",
    "TATACAP": "Tata Capital Limited",
    "AXISBANK": "Axis Bank",
    "HINDALCO": "Hindalco",
    "TATAPOWER": "Tata Power",
    "UNITDSPR": "United Spirits Limited",
    "BAJAJFINSV": "Bajaj Finserv",
    "SOLARINDS": "Solar Industries India Limited",
    "ADANIPOWER": "Adani Power",
    "AMBUJACEM": "Ambuja Cements Limited",
    "PFC": "Power Finance Corporation Limited",
    "TMPV": "Tata Motors Passenger Vehicles Limited",
    "ADANIPORTS": "Adani Ports",
    "TMCV": "Tata Motors Limited"
}
EARLY_INDEXES = {
    "^NSMIDCP": "NIFTY NEXT 50",
    "^CNXFIN": "FINNIFTY",
    "^CNX100": "NIFTY 100",
    "^NSEBANK": "BANK NIFTY",
    "^NSEI": "NIFTY 50",
    "^BSESN": "SENSEX",
    "BSEBANK": "BANKEX"
}
EARLY_UNIVERSE = list(EARLY_STOCKS.keys()) + list(EARLY_INDEXES.keys())
EARLY_ALL = {**EARLY_STOCKS, **EARLY_INDEXES}

# ----------------------------- DATA -----------------------------
def clean(x):
    if x is None or x.empty: return pd.DataFrame()
    if isinstance(x.columns,pd.MultiIndex): x.columns=x.columns.get_level_values(0)
    cols=[c for c in ["Open","High","Low","Close","Volume"] if c in x.columns]
    return x[cols].dropna()

@st.cache_data(ttl=120, show_spinner=False)
def get_data(symbol, interval="1d", period="1y"):
    try:
        return clean(yf.download(symbol,interval=interval,period=period,progress=False,auto_adjust=False,threads=False))
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def daily_row(symbol):
    x=get_data(symbol,"1d","1y")
    if len(x)<20:return None
    c=x.Close.astype(float); v=x.Volume.astype(float)
    p=float(c.iloc[-1]); prev=float(c.iloc[-2]); hi=float(c.max()); lo=float(c.min()); v20=float(v.tail(20).mean())
    sma20=float(c.tail(20).mean()); sma50=float(c.tail(50).mean()) if len(c)>=50 else sma20
    return {"Symbol":symbol,"Name":ALL.get(symbol,symbol),"LTP":p,"Change %":(p/prev-1)*100,"52W High":hi,"52W Low":lo,"Vol":float(v.iloc[-1]),"Avg Vol 20":v20,"SMA20":sma20,"SMA50":sma50,"From High %":(p/hi-1)*100,"From Low %":(p/lo-1)*100}

# ----------------------------- VS FLOW CORE -----------------------------
def resample_4h(x):
    if x.empty:return x
    return x.resample("4h").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()

def structure(x,n=5):
    if len(x)<n*2+3:return "WAIT"
    hi=x.High.iloc[-n-1:-1].max(); lo=x.Low.iloc[-n-1:-1].min(); last=x.iloc[-1]
    if last.Close>hi:return "BULL BOS"
    if last.Close<lo:return "BEAR BOS"
    return "WAIT"

def liquidity_sweep(x,n=5):
    if len(x)<n+3:return "WAIT"
    hi=x.High.iloc[-n-1:-1].max(); lo=x.Low.iloc[-n-1:-1].min(); last=x.iloc[-1]
    if last.High>hi and last.Close<hi:return "BSL SWEPT"
    if last.Low<lo and last.Close>lo:return "SSL SWEPT"
    return "WAIT"

def order_block(x):
    if len(x)<25:return None
    for i in range(len(x)-2,max(2,len(x)-30),-1):
        cur=x.iloc[i]; prev=x.iloc[i-1]; rng=max(float(cur.High-cur.Low),1e-9); body=abs(float(cur.Close-cur.Open))
        if body/rng<.55:continue
        if cur.Close>cur.Open and prev.Close<prev.Open and cur.Close>prev.High:
            return {"side":"BUY","type":"BULL OB","low":float(prev.Low),"high":float(prev.Open)}
        if cur.Close<cur.Open and prev.Close>prev.Open and cur.Close<prev.Low:
            return {"side":"SELL","type":"BEAR OB","low":float(prev.Open),"high":float(prev.High)}
    return None

def fvg(x):
    if len(x)<5:return None
    for i in range(len(x)-1,1,-1):
        a,b,c=x.iloc[i-2],x.iloc[i-1],x.iloc[i]
        if c.Low>a.High:return {"side":"BUY","type":"BULL FVG","low":float(a.High),"high":float(c.Low)}
        if c.High<a.Low:return {"side":"SELL","type":"BEAR FVG","low":float(c.High),"high":float(a.Low)}
    return None

def vsflow(symbol):
    h1=get_data(symbol,"1h","6mo"); m15=get_data(symbol,"15m","60d"); m5=get_data(symbol,"5m","30d")
    base={"Symbol":symbol,"Name":ALL.get(symbol,symbol),"4H OB":"WAIT","1H Sweep":"WAIT","1H BOS":"WAIT","15M FVG":"WAIT","5M Trigger":"WAIT","Score":"0/5","Signal":"WAIT"}
    if h1.empty or m15.empty or m5.empty:return base
    ob=order_block(resample_4h(h1));
    if not ob:return base
    side=ob["side"]; sw=liquidity_sweep(h1); bos=structure(h1); fv=fvg(m15); tr=structure(m5)
    core=[True,(side=="BUY" and bos=="BULL BOS") or (side=="SELL" and bos=="BEAR BOS"),bool(fv and fv["side"]==side),(side=="BUY" and tr=="BULL BOS") or (side=="SELL" and tr=="BEAR BOS")]
    bonus=(side=="BUY" and sw=="SSL SWEPT") or (side=="SELL" and sw=="BSL SWEPT")
    score=sum(core)+(1 if bonus else 0)
    base.update({"4H OB":ob["type"],"1H Sweep":sw,"1H BOS":bos,"15M FVG":fv["type"] if fv else "WAIT","5M Trigger":("5M BULL BOS" if tr=="BULL BOS" else "5M BEAR BOS" if tr=="BEAR BOS" else "WAIT"),"Score":f"{score}/5","Signal":("A+ BUY" if score==5 and side=="BUY" else "A+ SELL" if score==5 else "SETUP BUY" if score==4 and side=="BUY" else "SETUP SELL" if score==4 else "WAIT")})
    return base

# ----------------------------- VS FLOW OB + TREND SCANNER -----------------------------
def atr14(x):
    if len(x)<15:return 0.0
    h=x.High.astype(float); l=x.Low.astype(float); c=x.Close.astype(float)
    prev=c.shift(1)
    tr=pd.concat([(h-l),(h-prev).abs(),(l-prev).abs()],axis=1).max(axis=1)
    return float(tr.rolling(14).mean().iloc[-1])

def active_ob(symbol, interval, period, lookback=120, x_override=None):
    x=x_override if x_override is not None else get_data(symbol,interval,period)
    if len(x)<30:return []
    x=x.tail(lookback).copy()
    found=[]
    for i in range(len(x)-2,1,-1):
        cur=x.iloc[i]; prev=x.iloc[i-1]
        rng=max(float(cur.High-cur.Low),1e-9); body=abs(float(cur.Close-cur.Open))
        if body/rng<0.55:continue
        if cur.Close>cur.Open and prev.Close<prev.Open and cur.Close>prev.High:
            low=float(prev.Low); high=float(prev.Open); side='BULL OB'
        elif cur.Close<cur.Open and prev.Close>prev.Open and cur.Close<prev.Low:
            low=float(prev.Open); high=float(prev.High); side='BEAR OB'
        else:continue
        if low>high: low,high=high,low
        # Active OB = not decisively invalidated after formation.
        later=x.iloc[i+1:]
        invalid=False
        if side=='BULL OB' and len(later) and float(later.Low.min())<low: invalid=True
        if side=='BEAR OB' and len(later) and float(later.High.max())>high: invalid=True
        if invalid:continue
        found.append({'type':side,'low':low,'high':high,'index':x.index[i]})
        if len(found)>=8:break
    return found

def ob_distance_status(price, ob, atr):
    if not ob:return 'NONE',None
    lo,hi=ob['low'],ob['high']
    if lo<=price<=hi:return 'TOUCHING',0.0
    dist=min(abs(price-lo),abs(price-hi))
    ratio=dist/atr if atr>0 else 99
    if ratio<=0.5:return 'NEAR',ratio
    if ratio<=1.0:return 'APPROACHING',ratio
    return 'FAR',ratio

def ob_trend_scan(symbol):
    d=get_data(symbol,'1d','3y'); w=get_data(symbol,'1wk','5y'); m=get_data(symbol,'1mo','10y'); h1=get_data(symbol,'1h','6mo')
    if min(len(d),len(w),len(m),len(h1))<30:return None
    h4=resample_4h(h1)
    if len(h4)<30:return None
    p=float(d.Close.iloc[-1])
    def trend(x):
        if len(x)<50:return 'WAIT'
        c=x.Close.astype(float); e20=c.ewm(span=20,adjust=False).mean().iloc[-1]; e50=c.ewm(span=50,adjust=False).mean().iloc[-1]; last=float(c.iloc[-1])
        return 'BULLISH' if last>e20 and e20>e50 else 'BEARISH' if last<e20 and e20<e50 else 'MIXED'
    trends={'1M':trend(m),'1W':trend(w),'1D':trend(d),'4H':trend(h4),'1H':trend(h1)}
    series={'1M':(m,'10y'),'1W':(w,'5y'),'1D':(d,'3y'),'4H':(h4,None),'1H':(h1,'6mo')}
    bull=[]; bear=[]; details={}
    for tf,(x,_) in series.items():
        obs=active_ob(symbol,tf if tf in ['1M','1W','1D','1H'] else '1h',_ or '6mo',x_override=x)
        a=atr14(x)
        bo=[o for o in obs if o['type']=='BULL OB']; so=[o for o in obs if o['type']=='BEAR OB']
        for side,arr in [('Bull',bo),('Bear',so)]:
            if arr:
                best=min(arr,key=lambda o:0 if o['low']<=p<=o['high'] else min(abs(p-o['low']),abs(p-o['high'])))
                status,ratio=ob_distance_status(p,best,a)
                rec={'tf':tf,'low':best['low'],'high':best['high'],'status':status,'atr_dist':ratio}
                (bull if side=='Bull' else bear).append(rec)
                details[f'{side} {tf}']=rec
    def pick(arr):
        if not arr:return None
        rank={'TOUCHING':0,'NEAR':1,'APPROACHING':2,'FAR':3}
        return sorted(arr,key=lambda z:(rank.get(z['status'],9), z['atr_dist'] if z['atr_dist'] is not None else 99))[0]
    bob=pick(bull); sob=pick(bear)
    bull_score=sum(v=='BULLISH' for v in trends.values()); bear_score=sum(v=='BEARISH' for v in trends.values())
    hi=float(d.High.tail(60).max()); lo=float(d.Low.tail(60).min()); mid=lo+(hi-lo)*0.5
    location='DISCOUNT' if p<lo+(hi-lo)*0.45 else 'PREMIUM' if p>lo+(hi-lo)*0.55 else 'EQUILIBRIUM'
    bgood=bob and bob['status'] in ('TOUCHING','NEAR','APPROACHING')
    sgood=sob and sob['status'] in ('TOUCHING','NEAR','APPROACHING')
    if bull_score>=3 and bgood and location=='DISCOUNT': status='🟢 BUY WATCH'
    elif bear_score>=3 and sgood and location=='PREMIUM': status='🔴 SELL WATCH'
    elif bob and bob['status']=='TOUCHING': status='🟢 BULL OB TOUCH'
    elif sob and sob['status']=='TOUCHING': status='🔴 BEAR OB TOUCH'
    elif bob and bob['status'] in ('NEAR','APPROACHING'): status='🟡 BULL OB NEAR'
    elif sob and sob['status'] in ('NEAR','APPROACHING'): status='🟡 BEAR OB NEAR'
    else: status='⚪ WAIT'
    def zone(rec): return f"{rec['low']:.2f}-{rec['high']:.2f}" if rec else 'NONE'
    def dist(rec): return '-' if not rec or rec['atr_dist'] is None else ('0 ATR' if rec['atr_dist']==0 else f"{rec['atr_dist']:.2f} ATR")
    return {
        'Symbol':symbol,'Name':ALL.get(symbol,symbol),'LTP':round(p,2),
        '1M':trends['1M'],'1W':trends['1W'],'1D':trends['1D'],'4H':trends['4H'],'1H':trends['1H'],
        'Location':location,'Bull OB TF':bob['tf'] if bob else 'NONE','Bull OB':zone(bob),'Bull OB Dist':dist(bob),
        'Bear OB TF':sob['tf'] if sob else 'NONE','Bear OB':zone(sob),'Bear OB Dist':dist(sob),
        'Status':status,'Bull Trend Score':f'{bull_score}/5','Bear Trend Score':f'{bear_score}/5'
    }

# ----------------------------- VS FLOW EARLY ENGINE -----------------------------
def _ema_state(x):
    if len(x)<55:return "WAIT"
    c=x.Close.astype(float); e20=c.ewm(span=20,adjust=False).mean(); e50=c.ewm(span=50,adjust=False).mean(); p=float(c.iloc[-1])
    if p>float(e20.iloc[-1])>float(e50.iloc[-1]): return "BULL"
    if p<float(e20.iloc[-1])<float(e50.iloc[-1]): return "BEAR"
    return "MIXED"

def _recent_mss(x,n=5,lookback=4):
    if len(x)<n+lookback+3:return "WAIT",99
    for age in range(0,lookback):
        j=len(x)-1-age
        if j<=n:return "WAIT",99
        last=x.iloc[j]; prior=x.iloc[j-n:j]
        hi=float(prior.High.max()); lo=float(prior.Low.min())
        if float(last.Close)>hi:return "BULL",age
        if float(last.Close)<lo:return "BEAR",age
    return "WAIT",99

def _displacement(x,lookback=4):
    if len(x)<25:return "WAIT",0.0
    h=x.High.astype(float); l=x.Low.astype(float); c=x.Close.astype(float); o=x.Open.astype(float)
    tr=(h-l).rolling(20).median().iloc[-1]
    if not tr or pd.isna(tr):return "WAIT",0.0
    for age in range(min(lookback,len(x)-1)):
        b=x.iloc[-1-age]; rng=max(float(b.High-b.Low),1e-9); body=abs(float(b.Close-b.Open))
        if body/rng>=0.60 and rng>=1.35*float(tr):
            return ("BULL" if b.Close>b.Open else "BEAR"), float(rng/tr)
    return "WAIT",0.0

def _recent_sweep(x,n=5,lookback=4):
    if len(x)<n+lookback+3:return "WAIT",99
    for age in range(0,lookback):
        j=len(x)-1-age
        if j<=n:return "WAIT",99
        last=x.iloc[j]; prior=x.iloc[j-n:j]
        hi=float(prior.High.max()); lo=float(prior.Low.min())
        if float(last.High)>hi and float(last.Close)<hi:return "BEAR",age
        if float(last.Low)<lo and float(last.Close)>lo:return "BULL",age
    return "WAIT",99

def _recent_fvg(x,lookback=5):
    if len(x)<6:return "WAIT"
    for age in range(0,lookback):
        i=len(x)-1-age
        if i<2:break
        a,b,c=x.iloc[i-2],x.iloc[i-1],x.iloc[i]
        if float(c.Low)>float(a.High):return "BULL"
        if float(c.High)<float(a.Low):return "BEAR"
    return "WAIT"

def _volume_impulse(x):
    if len(x)<25 or "Volume" not in x.columns:return 0.0
    v=x.Volume.astype(float); avg=float(v.tail(20).iloc[:-1].mean()) if len(v)>20 else float(v.mean())
    return float(v.iloc[-1]/avg) if avg>0 else 0.0

def _early_tf(x):
    mss,mss_age=_recent_mss(x); sweep,sweep_age=_recent_sweep(x); disp,disp_mult=_displacement(x); fvg_side=_recent_fvg(x); ema=_ema_state(x)
    return {"ema":ema,"mss":mss,"mss_age":mss_age,"sweep":sweep,"sweep_age":sweep_age,"disp":disp,"disp_mult":disp_mult,"fvg":fvg_side,"vol":_volume_impulse(x)}

def _compression_state(x, lookback=20):
    """Pre-ignition detector: identifies range/ATR compression before expansion."""
    if len(x) < max(30, lookback + 10):
        return {"state":"WAIT","score":0,"range_ratio":99.0,"atr_ratio":99.0}
    h=x.High.astype(float); l=x.Low.astype(float); c=x.Close.astype(float)
    recent_range=float(h.tail(5).max()-l.tail(5).min())
    base_range=float(h.tail(lookback).max()-l.tail(lookback).min())
    atr_fast=float((h-l).tail(5).mean())
    atr_base=float((h-l).tail(20).mean())
    range_ratio=recent_range/base_range if base_range>0 else 99.0
    atr_ratio=atr_fast/atr_base if atr_base>0 else 99.0
    score=(1 if range_ratio<=0.55 else 0)+(1 if atr_ratio<=0.80 else 0)
    state="TIGHT" if score==2 else "COILING" if score==1 else "NORMAL"
    return {"state":state,"score":score,"range_ratio":range_ratio,"atr_ratio":atr_ratio}

def _liquidity_cluster(x, lookback=20):
    """Simple structural liquidity map around repeated swing highs/lows."""
    if len(x)<lookback+5:return {"high":False,"low":False,"score":0}
    h=x.High.astype(float).tail(lookback); l=x.Low.astype(float).tail(lookback)
    atr=max(float((x.High.astype(float)-x.Low.astype(float)).tail(14).mean()),1e-9)
    high_tol=0.20*atr; low_tol=0.20*atr
    hv=sorted(h.tolist(),reverse=True); lv=sorted(l.tolist())
    high_cluster=any(abs(hv[i]-hv[j])<=high_tol for i in range(min(6,len(hv))) for j in range(i+1,min(6,len(hv))))
    low_cluster=any(abs(lv[i]-lv[j])<=low_tol for i in range(min(6,len(lv))) for j in range(i+1,min(6,len(lv))))
    return {"high":high_cluster,"low":low_cluster,"score":int(high_cluster)+int(low_cluster)}

def _ob_precontext(symbol, h1):
    """Reuse the existing OB engine to classify the nearest active 4H/1D zone."""
    try:
        d=get_data(symbol,"1d","2y")
        h4=resample_4h(h1)
        p=float(h1.Close.iloc[-1]); atr=atr14(h4)
        bull4=active_ob(symbol,"1h","6mo",x_override=h4)
        bear4=bull4
        bull=[o for o in bull4 if o["type"]=="BULL OB"]
        bear=[o for o in bear4 if o["type"]=="BEAR OB"]
        def pick(arr):
            if not arr:return None
            return min(arr,key=lambda o: min(abs(p-o["low"]),abs(p-o["high"])))
        bo=pick(bull); so=pick(bear)
        bs,_=ob_distance_status(p,bo,atr); ss,_=ob_distance_status(p,so,atr)
        return {"bull":bs,"bear":ss,"bull_zone":bo,"bear_zone":so}
    except Exception:
        return {"bull":"NONE","bear":"NONE","bull_zone":None,"bear_zone":None}

def _origin_ob_scan(x, side, max_candidates=8):
    """Score an OB by its origin sequence: liquidity -> displacement -> structure break -> FVG -> freshness."""
    if x is None or len(x) < 40:
        return {"score":0,"grade":"NONE","zone":None,"touches":99,"liquidity":False,"displacement":False,"bos":False,"fvg":False,"fresh":False}
    obs=active_ob("__OVERRIDE__","1h","6mo",lookback=min(180,len(x)),x_override=x)
    candidates=[o for o in obs if o["type"]==side][:max_candidates]
    best=None
    for o in candidates:
        try: idx=x.index.get_loc(o["index"])
        except Exception: continue
        pre=x.iloc[max(0,idx-12):idx]
        post=x.iloc[idx+1:min(len(x),idx+9)]
        if len(post)<3: continue
        # Liquidity: the OB candle takes a nearby prior swing extreme and closes back inside.
        liquidity=False
        if len(pre)>=5:
            cur=x.iloc[idx]
            if side=="BULL OB":
                prior_low=float(pre.Low.min()); liquidity=float(cur.Low)<=prior_low and float(cur.Close)>prior_low
            else:
                prior_high=float(pre.High.max()); liquidity=float(cur.High)>=prior_high and float(cur.Close)<prior_high
        # Displacement: a strong directional candle leaves the zone with expansion.
        ranges=(x.High.astype(float)-x.Low.astype(float)).rolling(20).median()
        base=float(ranges.iloc[idx]) if idx < len(ranges) and pd.notna(ranges.iloc[idx]) else float((x.High-x.Low).tail(20).median())
        base=max(base,1e-9)
        displacement=False
        for _,b in post.iterrows():
            rng=max(float(b.High-b.Low),1e-9); body=abs(float(b.Close-b.Open))
            if body/rng>=0.60 and rng>=1.30*base:
                if (side=="BULL OB" and b.Close>b.Open) or (side=="BEAR OB" and b.Close<b.Open):
                    displacement=True; break
        # Structure break after the OB.
        bos=False
        if len(pre)>=5:
            pre_hi=float(pre.High.tail(5).max()); pre_lo=float(pre.Low.tail(5).min())
            if side=="BULL OB": bos=bool(float(post.Close.max())>pre_hi)
            else: bos=bool(float(post.Close.min())<pre_lo)
        # FVG created in the impulse window.
        fvg=False
        pp=x.iloc[max(0,idx):min(len(x),idx+9)]
        for i in range(2,len(pp)):
            a,b,c=pp.iloc[i-2],pp.iloc[i-1],pp.iloc[i]
            if side=="BULL OB" and float(c.Low)>float(a.High): fvg=True; break
            if side=="BEAR OB" and float(c.High)<float(a.Low): fvg=True; break
        # Count later touches of the OB zone (exclude the formation candle).
        touches=0
        lo,hi=o["low"],o["high"]
        for _,b in x.iloc[idx+1:].iterrows():
            if float(b.High)>=lo and float(b.Low)<=hi: touches+=1
        fresh=touches<=1
        score=(2 if liquidity else 0)+(2 if displacement else 0)+(2 if bos else 0)+(1 if fvg else 0)+(1 if fresh else 0)+(1 if idx>=len(x)-40 else 0)
        grade="A+" if score>=8 else "A" if score>=7 else "B" if score>=5 else "C"
        rec={"score":score,"grade":grade,"zone":o,"touches":touches,"liquidity":liquidity,"displacement":displacement,"bos":bos,"fvg":fvg,"fresh":fresh}
        if best is None or (rec["score"], rec["fresh"], -rec["touches"]) > (best["score"], best["fresh"], -best["touches"]): best=rec
    return best or {"score":0,"grade":"NONE","zone":None,"touches":99,"liquidity":False,"displacement":False,"bos":False,"fvg":False,"fresh":False}

def _candle_confirmation(x):
    """Small confirmation layer; never a standalone entry trigger."""
    if len(x)<3:return "None"
    a=x.iloc[-2]; b=x.iloc[-1]
    body=max(abs(float(b.Close-b.Open)),1e-9); rng=max(float(b.High-b.Low),1e-9)
    upper=float(b.High-max(b.Open,b.Close)); lower=float(min(b.Open,b.Close)-b.Low)
    if b.Close>b.Open and a.Close<a.Open and b.Close>=a.Open and b.Open<=a.Close:return "Bullish Engulfing"
    if b.Close<b.Open and a.Close>a.Open and b.Open>=a.Close and b.Close<=a.Open:return "Bearish Engulfing"
    if lower>body*2 and upper<body*0.7:return "Hammer"
    if upper>body*2 and lower<body*0.7:return "Shooting Star"
    if body/rng<0.10:return "Doji"
    return "None"

def _early_score(direction, d, h4, h1, m15, m5):
    side=direction; score=0; reasons=[]
    # HTF alignment: two points each. Early engine is not allowed to fight both HTFs.
    for label,tf in [("1D",d),("4H",h4)]:
        if tf["ema"]==side: score+=2; reasons.append(f"{label} {side}")
        elif tf["ema"]==("BEAR" if side=="BULL" else "BULL"): score-=1
    # 1H ignition is the heart of the early engine.
    if h1["mss"]==side and h1["mss_age"]<=3: score+=2; reasons.append(f"1H MSS {side}")
    if h1["sweep"]==side and h1["sweep_age"]<=3: score+=1; reasons.append("1H liquidity sweep")
    if h1["disp"]==side: score+=1; reasons.append("1H displacement")
    # 15M confirms that the ignition is propagating down.
    if m15["mss"]==side and m15["mss_age"]<=4: score+=1; reasons.append("15M MSS")
    if m15["fvg"]==side: score+=1; reasons.append("15M FVG")
    if m15["disp"]==side or m15["vol"]>=1.5: score+=1; reasons.append("15M impulse")
    # 5M is the trigger, not the bias generator.
    if m5["mss"]==side and m5["mss_age"]<=6: score+=1; reasons.append("5M trigger")
    if m5["disp"]==side: score+=1; reasons.append("5M displacement")
    return score,reasons

def _early_scan_one(symbol, d, h1, m15, m5):
    if min(len(d),len(h1),len(m15),len(m5))<40:return None
    h4=resample_4h(h1)
    if len(h4)<30:return None
    d0=_early_tf(d); h40=_early_tf(h4); h10=_early_tf(h1); m150=_early_tf(m15); m50=_early_tf(m5)
    comp=_compression_state(h1)
    liq=_liquidity_cluster(h1)
    obc=_ob_precontext(symbol,h1)
    bull_origin=_origin_ob_scan(h4,"BULL OB")
    bear_origin=_origin_ob_scan(h4,"BEAR OB")
    candle=_candle_confirmation(m15)
    bull_score,bull_reasons=_early_score("BULL",d0,h40,h10,m150,m50)
    bear_score,bear_reasons=_early_score("BEAR",d0,h40,h10,m150,m50)
    # Pre-ignition bonus: balance/compression + nearby liquidity + directional OB context.
    if comp["score"]>=1:
        bull_score += 1; bear_score += 1
    if liq["low"]: bull_score += 1
    if liq["high"]: bear_score += 1
    if obc["bull"] in ("TOUCHING","NEAR","APPROACHING"): bull_score += 1
    if obc["bear"] in ("TOUCHING","NEAR","APPROACHING"): bear_score += 1
    if bull_origin["grade"] in ("A+","A"): bull_score += 2; bull_reasons.append(f"4H Origin OB {bull_origin["grade"]}")
    elif bull_origin["grade"]=="B": bull_score += 1; bull_reasons.append("4H Origin OB B")
    if bear_origin["grade"] in ("A+","A"): bear_score += 2; bear_reasons.append(f"4H Origin OB {bear_origin["grade"]}")
    elif bear_origin["grade"]=="B": bear_score += 1; bear_reasons.append("4H Origin OB B")
    if candle=="Bullish Engulfing": bull_score += 1; bull_reasons.append("15M Bullish Engulfing")
    if candle=="Bearish Engulfing": bear_score += 1; bear_reasons.append("15M Bearish Engulfing")
    if bull_score>=bear_score: direction="BUY"; score=bull_score; reasons=bull_reasons
    else: direction="SELL"; score=bear_score; reasons=bear_reasons
    # Freshness gate: a stale trend is not an EARLY signal.
    fresh=(h10["mss_age"]<=3 and h10["mss"]==direction) or (m150["mss_age"]<=4 and m150["mss"]==direction)
    trigger=(m50["mss"]==direction and m50["mss_age"]<=6)
    if score>=9 and fresh and trigger: status=f"🚀 EARLY {direction}"
    elif score>=7 and fresh: status=f"🟢 WATCH {direction}" if direction=="BUY" else f"🔴 WATCH {direction}"
    elif comp["score"]>=1 and ((direction=="BUY" and (liq["low"] or obc["bull"] in ("TOUCHING","NEAR","APPROACHING"))) or (direction=="SELL" and (liq["high"] or obc["bear"] in ("TOUCHING","NEAR","APPROACHING")))):
        status=f"🟡 PRE-IGNITION {direction}"
    else: status="⚪ WAIT"
    p=float(m5.Close.iloc[-1])
    atr=atr14(m5)
    # Anti-chase: if the latest impulse has already travelled >1.5 ATR from its local origin, downgrade it.
    recent_hi=float(m5.High.tail(8).max()); recent_lo=float(m5.Low.tail(8).min())
    chase="NO" if atr<=0 else ("YES" if (direction=="BUY" and p>recent_lo+1.5*atr) or (direction=="SELL" and p<recent_hi-1.5*atr) else "NO")
    return {
        "Symbol":symbol,"Name":EARLY_ALL.get(symbol,ALL.get(symbol,symbol)),"LTP":round(p,2),"Direction":direction,
        "Score":f"{min(score,20)}/20","Status":status,"1D":d0["ema"],"4H":h40["ema"],"1H MSS":f"{h10['mss']} ({h10['mss_age']}b)" if h10['mss']!="WAIT" else "WAIT",
        "1H Sweep":f"{h10['sweep']} ({h10['sweep_age']}b)" if h10['sweep']!="WAIT" else "WAIT","15M MSS":f"{m150['mss']} ({m150['mss_age']}b)" if m150['mss']!="WAIT" else "WAIT",
        "15M FVG":m150["fvg"],"5M Trigger":f"{m50['mss']} ({m50['mss_age']}b)" if m50['mss']!="WAIT" else "WAIT","5M FVG":m50["fvg"],
        "Vol x":round(max(m150["vol"],m50["vol"]),2),"Chase":chase,
        "Compression":comp["state"],"Liquidity":("SSL" if liq["low"] else "") + (" + BSL" if liq["high"] else ""),
        "Bull OB":obc["bull"],"Bear OB":obc["bear"],
        "4H Bull Origin OB":bull_origin["grade"],"4H Bull OB Score":f"{bull_origin["score"]}/10","4H Bull OB Touches":bull_origin["touches"],
        "4H Bear Origin OB":bear_origin["grade"],"4H Bear OB Score":f"{bear_origin["score"]}/10","4H Bear OB Touches":bear_origin["touches"],
        "15M Candle":candle,
        "Why":", ".join(reasons[:8])
    }

def _early_stage1(symbol):
    d=get_data(symbol,"1d","2y"); h1=get_data(symbol,"1h","6mo")
    if d.empty or h1.empty:return None
    h4=resample_4h(h1)
    if len(d)<60 or len(h4)<30:return None
    dt=_early_tf(d); ht=_early_tf(h4); h1t=_early_tf(h1)
    bull=0; bear=0
    bull += 2 if dt["ema"]=="BULL" else -1 if dt["ema"]=="BEAR" else 0
    bull += 2 if ht["ema"]=="BULL" else -1 if ht["ema"]=="BEAR" else 0
    bear += 2 if dt["ema"]=="BEAR" else -1 if dt["ema"]=="BULL" else 0
    bear += 2 if ht["ema"]=="BEAR" else -1 if ht["ema"]=="BULL" else 0
    if h1t["mss"]=="BULL" and h1t["mss_age"]<=5:bull+=2
    if h1t["mss"]=="BEAR" and h1t["mss_age"]<=5:bear+=2
    # Pre-ignition candidates are allowed into the deep scan even before MSS exists.
    # This is intentionally a watchlist gate, never a trade trigger.
    if h1t["disp"]=="BULL":bull+=1
    if h1t["disp"]=="BEAR":bear+=1
    if h1t["sweep"]=="BULL" and h1t["sweep_age"]<=5:bull+=1
    if h1t["sweep"]=="BEAR" and h1t["sweep_age"]<=5:bear+=1
    return max(bull,bear), ("BUY" if bull>=bear else "SELL"), d, h1

@st.cache_data(ttl=60,show_spinner=False)
def run_early_engine(symbols):
    stage1=[]
    for s in symbols:
        r=_early_stage1(s)
        if r: stage1.append((s,*r))
    # Deep intraday scan only on the strongest 35 pre-candidates to keep the 100+ universe responsive.
    stage1=sorted(stage1,key=lambda z:z[1],reverse=True)
    candidates=stage1[:35]
    rows=[]
    for s,pre_score,pre_side,d,h1 in candidates:
        m15=get_data(s,"15m","20d"); m5=get_data(s,"5m","5d")
        if m15.empty or m5.empty:continue
        r=_early_scan_one(s,d,h1,m15,m5)
        if r: rows.append(r)
    df=pd.DataFrame(rows)
    if df.empty:return df
    rank={"🚀 EARLY BUY":0,"🚀 EARLY SELL":0,"🟢 WATCH BUY":1,"🔴 WATCH SELL":1,"🟡 PRE-IGNITION BUY":2,"🟡 PRE-IGNITION SELL":2,"⚪ WAIT":9}
    df["__rank"]=df.Status.map(rank).fillna(9)
    df=df.sort_values(["__rank","Score","Vol x"],ascending=[True,False,False]).drop(columns="__rank")
    return df

# ----------------------------- TECHNICAL SCANNERS -----------------------------
def market_table(symbols):
    rows=[]
    for s in symbols:
        r=daily_row(s)
        if r:rows.append(r)
    return pd.DataFrame(rows)

def candle_pattern(x):
    if len(x)<3:return "None"
    a=x.iloc[-2]; b=x.iloc[-1]
    body=abs(float(b.Close-b.Open)); rng=max(float(b.High-b.Low),1e-9); upper=float(b.High-max(b.Open,b.Close)); lower=float(min(b.Open,b.Close)-b.Low)
    if body/rng<.1:return "Doji"
    if lower>body*2 and upper<body*.7:return "Hammer"
    if upper>body*2 and lower<body*.7:return "Shooting Star"
    if b.Close>b.Open and a.Close<a.Open and b.Close>=a.Open and b.Open<=a.Close:return "Bullish Engulfing"
    if b.Close<b.Open and a.Close>a.Open and b.Open>=a.Close and b.Close<=a.Open:return "Bearish Engulfing"
    return "None"

def scan_category(symbols, category):
    rows=[]
    for s in symbols:
        x=get_data(s,"1d","1y")
        if len(x)<50:continue
        c=x.Close.astype(float); v=x.Volume.astype(float); p=float(c.iloc[-1]); hi=float(c.max()); lo=float(c.min()); sma20=float(c.tail(20).mean()); sma50=float(c.tail(50).mean()); avg=float(v.tail(20).mean()); vol=float(v.iloc[-1])
        ch=(p/float(c.iloc[-2])-1)*100
        pat=candle_pattern(x)
        if category=="Gainers": ok=ch>0
        elif category=="Losers": ok=ch<0
        elif category=="Most Active": ok=vol>avg*1.5
        elif category=="ATH": ok=p>=hi*.995
        elif category=="ATL": ok=p<=lo*1.005
        elif category=="52W High": ok=p>=hi*.95
        elif category=="52W Low": ok=p<=lo*1.05
        elif category=="Penny": ok=p<50
        elif category=="Breakout": ok=p>float(c.iloc[-21:-1].max()) and vol>avg*1.2
        elif category=="Breakdown": ok=p<float(c.iloc[-21:-1].min()) and vol>avg*1.2
        elif category=="Reversal Bull": ok=(p>sma20 and float(c.iloc[-2])<=sma20)
        elif category=="Reversal Bear": ok=(p<sma20 and float(c.iloc[-2])>=sma20)
        elif category=="Bull Trend": ok=p>sma20>sma50
        elif category=="Bear Trend": ok=p<sma20<sma50
        elif category=="Candlestick": ok=pat!="None"
        elif category=="Potential Multibagger": ok=(p>sma50 and float(c.iloc[-1])/float(c.iloc[-60])>1.15 and vol>avg*.8)
        else: ok=True
        if ok:rows.append({"Symbol":s,"Name":ALL.get(s,s),"LTP":round(p,2),"Change %":round(ch,2),"Volume":int(vol),"52W High":round(hi,2),"52W Low":round(lo,2),"SMA20":round(sma20,2),"SMA50":round(sma50,2),"Pattern":pat})
    return pd.DataFrame(rows)


# ----------------------------- SMART STOCK FINDER -----------------------------
NIFTY500_OFFICIAL_URL = "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv"
NIFTY500_FALLBACK_URL = "https://raw.githubusercontent.com/ganeshbiyer/Nse_Historical_Data/main/nifty500_symbols.csv"

@st.cache_data(ttl=86400, show_spinner=False)
def get_nifty500_universe():
    """Load the Nifty 500 universe; prefer official NSE, then a maintained fallback."""
    frames = []
    for url in (NIFTY500_OFFICIAL_URL, NIFTY500_FALLBACK_URL):
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=12)
            r.raise_for_status()
            df = pd.read_csv(io.BytesIO(r.content))
            sym_col = next((c for c in df.columns if str(c).strip().lower() in ("symbol","ticker")), None)
            name_col = next((c for c in df.columns if str(c).strip().lower() in ("company name","companyname","name")), None)
            if sym_col:
                out = {}
                for _, row in df.iterrows():
                    raw = str(row[sym_col]).strip()
                    if not raw or raw.lower()=="nan": continue
                    # Keep equity symbols only; Yahoo NSE suffix.
                    if raw.endswith((".NS",".BO")): sym = raw
                    else: sym = raw + ".NS"
                    name = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else raw
                    out[sym] = name
                if len(out) >= 450:
                    return dict(list(out.items())[:500])
        except Exception:
            continue
    # Safe fallback so the app never crashes if the universe source is unavailable.
    return dict(CORE)

def _rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return (100 - (100 / (1 + rs))).fillna(50)

@st.cache_data(ttl=300, show_spinner=False)
def smart_finder_scan(direction="BOTH", min_score=65, min_vol_ratio=1.2,
                      max_high_dist=12.0, rsi_min=42.0, rsi_max=68.0,
                      scan_count=500, symbol_filter=""):
    universe = get_nifty500_universe()
    if symbol_filter.strip():
        q = symbol_filter.strip().lower()
        universe = {s:n for s,n in universe.items() if q in s.lower() or q in n.lower()}
    symbols = list(universe)[:int(scan_count)]
    rows = []

    # Batch downloads reduce Yahoo requests and make a 500-stock scan practical.
    for start in range(0, len(symbols), 50):
        batch = symbols[start:start+50]
        try:
            raw = yf.download(batch, period="1y", interval="1d", progress=False,
                               auto_adjust=False, threads=True, group_by="ticker")
        except Exception:
            continue
        for sym in batch:
            try:
                if len(batch) == 1:
                    x = clean(raw)
                else:
                    if sym not in raw.columns.get_level_values(0):
                        continue
                    x = clean(raw[sym])
                if len(x) < 220:
                    continue

                c = x.Close.astype(float)
                v = x.Volume.astype(float)
                p = float(c.iloc[-1])
                ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
                ema50 = float(c.ewm(span=50, adjust=False).mean().iloc[-1])
                ema200 = float(c.ewm(span=200, adjust=False).mean().iloc[-1])
                rsi = float(_rsi(c).iloc[-1])
                vol20 = float(v.tail(20).mean())
                vol_ratio = float(v.iloc[-1] / vol20) if vol20 > 0 else 0.0
                hi52 = float(c.tail(252).max())
                high_dist = max(0.0, (hi52-p)/hi52*100) if hi52 > 0 else 999.0

                bullish = p > ema20 > ema50
                bearish = p < ema20 < ema50
                above200 = p > ema200
                below200 = p < ema200
                rsi_ok = rsi_min <= rsi <= rsi_max
                vol_ok = vol_ratio >= min_vol_ratio
                high_ok = high_dist <= max_high_dist

                if direction == "BULLISH":
                    trend_ok, ema_ok = bullish, above200
                elif direction == "BEARISH":
                    trend_ok, ema_ok = bearish, below200
                else:
                    # BOTH: score whichever directional trend is present.
                    trend_ok = bullish or bearish
                    ema_ok = above200 if bullish else below200 if bearish else False

                score = (20 if trend_ok else 0) + (20 if ema_ok else 0) + \
                        (20 if rsi_ok else 0) + (20 if vol_ok else 0) + \
                        (10 if high_ok else 0)

                if score < float(min_score):
                    continue

                bias = "BULLISH" if bullish and above200 else "BEARISH" if bearish and below200 else "MIXED"
                reasons = []
                if trend_ok: reasons.append("EMA20 > EMA50" if bias=="BULLISH" else "EMA20 < EMA50")
                if ema_ok: reasons.append("Above EMA200" if bias=="BULLISH" else "Below EMA200")
                if rsi_ok: reasons.append("Healthy RSI")
                if vol_ok: reasons.append("Volume expansion")
                if high_ok: reasons.append("Near 52W high")
                rows.append({
                    "Symbol": sym.replace(".NS",""),
                    "Name": universe.get(sym, sym.replace(".NS","")),
                    "Exchange": "NSE",
                    "Score": int(score),
                    "Trend": bias,
                    "RSI": round(rsi,1),
                    "Vol×20D": round(vol_ratio,2),
                    "52W High Dist %": round(high_dist,2),
                    "Price": round(p,2),
                    "Reasons": "; ".join(reasons)
                })
            except Exception:
                continue

    if not rows:
        return pd.DataFrame(columns=["Symbol","Name","Exchange","Score","Trend","RSI","Vol×20D","52W High Dist %","Price","Reasons"])

    df = pd.DataFrame(rows)
    # Quality ranking — never alphabetical.
    df = df.sort_values(["Score","Vol×20D","52W High Dist %","RSI"],
                        ascending=[False,False,True,True]).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df)+1))
    return df


# ----------------------------- MULTIBAGGER HUNTER -----------------------------
MULTIBAGGER_QUERY_STRICT = """Market Capitalization > 1000 AND YOY Quarterly sales growth > 0 AND YOY Quarterly profit growth > 0 AND Sales growth 3Years > 15 AND Sales growth 5Years > 15 AND Profit growth 3Years > 15 AND Profit growth 5Years > 15 AND EPS growth 3Years > 15 AND EPS growth 5Years > 15 AND PEG Ratio < 1 AND PEG Ratio > 0 AND Dividend yield > 1 AND Average return on capital employed 3Years > 30 AND Average return on equity 3Years > 20 AND Return on capital employed > Average return on capital employed 3Years AND OPM > 12 AND OPM last year > 12 AND Promoter holding > 50 AND Debt to equity < 0.75 AND Interest Coverage Ratio > 5 AND Pledged percentage == 0 AND Free cash flow 3years > 0 AND Piotroski score > 6 AND Price to Earning < Industry PE"""
MULTIBAGGER_QUERY_EARLY = """Market Capitalization > 1000 AND YOY Quarterly sales growth > 0 AND YOY Quarterly profit growth > 0 AND Sales growth 3Years > 15 AND Sales growth 5Years > 15 AND Profit growth 3Years > 15 AND Profit growth 5Years > 15 AND EPS growth 3Years > 15 AND EPS growth 5Years > 15 AND PEG Ratio < 1 AND PEG Ratio > 0 AND Average return on capital employed 3Years > 30 AND Average return on equity 3Years > 20 AND Return on capital employed > Average return on capital employed 3Years AND OPM > 12 AND OPM last year > 12 AND Promoter holding > 50 AND Debt to equity < 0.75 AND Interest Coverage Ratio > 5 AND Pledged percentage == 0 AND Free cash flow 3years > 0 AND Piotroski score > 6 AND Price to Earning < Industry PE"""

def _screener_symbol_map(html):
    # Extract NSE symbols from company links; avoids guessing tickers from company names.
    import re
    found = {}
    for href, text in re.findall(r'href=["\'](?:https?://www\.screener\.in)?/company/([A-Z0-9&._-]+)(?:/[^"\']*)?["\'][^>]*>(.*?)</a>', html, flags=re.I|re.S):
        name = re.sub('<[^>]+>', '', text).strip()
        found[href.upper()] = name
    return found

@st.cache_data(ttl=900, show_spinner=False)
def multibagger_hunter(mode="STRICT", min_score=70, symbol_filter=""):
    query = MULTIBAGGER_QUERY_STRICT if mode == "STRICT" else MULTIBAGGER_QUERY_EARLY
    try:
        import requests, io
        url = "https://www.screener.in/screen/raw/"
        r = requests.get(url, params={"query": query}, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        html = r.text
        # Raw screen exposes the same company/result table as the signed-out screen.
        tables = pd.read_html(io.StringIO(html))
        if not tables:
            return pd.DataFrame(), "Screener returned no result table."
        rawdf = tables[0].copy()
        if rawdf.empty:
            return pd.DataFrame(), "No companies passed the fundamental formula."
        symmap = _screener_symbol_map(html)
        name_col = next((c for c in rawdf.columns if str(c).strip().lower() in ["name","company"]), rawdf.columns[1] if len(rawdf.columns)>1 else rawdf.columns[0])
        rows=[]
        universe = get_nifty500_universe()
        nse_by_name={str(v).strip().lower():k.replace('.NS','') for k,v in universe.items()}
        allowed=set(k.replace('.NS','').upper() for k in universe)
        for _, row in rawdf.iterrows():
            nm=str(row.get(name_col,"" )).strip()
            # Prefer exact symbol extracted from the company URL; fallback to name match in Nifty 500.
            sym = next((x for x,n in symmap.items() if n.strip().lower()==nm.lower()), None)
            if not sym:
                sym=nse_by_name.get(nm.lower(),"")
            if not sym or sym.upper() not in allowed:
                continue
            if symbol_filter.strip() and symbol_filter.lower() not in (sym+" "+nm).lower():
                continue
            def num(col, default=0.0):
                try: return float(str(row.get(col, default)).replace(',','').replace('%',''))
                except Exception: return default
            # Quality score uses fields exposed in the public screen table; the hard query
            # itself enforces the deeper PEG/debt/coverage/cash-flow/Piotroski gates.
            score=0
            score += 15 if num("Qtr Sales Var %") >= 15 else 10
            score += 15 if num("Qtr Profit Var %") >= 15 else 10
            score += 20 if num("ROCE %") >= 35 else 15
            score += 15 if num("Prom. Hold. %") >= 60 else 10
            score += 10 if num("Div Yld %") >= 2 else 7
            pe=num("P/E", 999); indpe=num("Ind PE", 0)
            score += 15 if indpe > 0 and pe > 0 and pe < indpe else 8
            score += 10 if num("Mar Cap Rs.Cr.") >= 5000 else 7
            if score < min_score: continue
            out={"Symbol":sym.upper(),"Company":nm,"Fundamental Score":score}
            for c in ["Mar Cap Rs.Cr.","P/E","Div Yld %","Qtr Profit Var %","Qtr Sales Var %","ROCE %","Prom. Hold. %","Ind PE"]:
                if c in rawdf.columns: out[c]=row.get(c)
            out["Nifty 500"]="YES"
            out["Mode"]=mode
            rows.append(out)
        if not rows:
            return pd.DataFrame(), "Formula passed, but no Nifty 500 company cleared the final quality score."
        df=pd.DataFrame(rows).sort_values(["Fundamental Score","Qtr Profit Var %","Qtr Sales Var %"], ascending=[False,False,False], na_position="last").reset_index(drop=True)
        df.insert(0,"Rank",range(1,len(df)+1))
        return df, ""
    except Exception as e:
        return pd.DataFrame(), f"Fundamental engine error: {e}"

# ----------------------------- UI STATE -----------------------------
if "page" not in st.session_state: st.session_state.page="Dashboard"
if "asset" not in st.session_state: st.session_state.asset="RELIANCE.NS"
if "scan" not in st.session_state: st.session_state.scan=pd.DataFrame()
if "smart_finder" not in st.session_state: st.session_state.smart_finder=pd.DataFrame()
if "early_scan" not in st.session_state: st.session_state.early_scan=pd.DataFrame()

with st.sidebar:
    st.markdown("# 🇮🇳 VS FLOW INDIA")
    st.caption("SCAN • ANALYSE • DISCOVER • TEST")
    for section,items in SECTIONS.items():
        st.markdown(f"**{section}**")
        for item in items:
            if st.button(item,key="nav_"+item,use_container_width=True): st.session_state.page=item; st.rerun()
    st.divider()
    st.caption("NSE + BSE architecture • live data provider can be upgraded later")

# ----------------------------- HEADER -----------------------------
st.markdown('<div style="display:flex;justify-content:space-between;align-items:end;gap:20px;flex-wrap:wrap"><div><div class="vsf-title">VS FLOW INDIA 🇮🇳</div><div class="vsf-sub">ALL-IN-ONE INDIAN MARKET INTELLIGENCE • SMC • SCANNERS • PRICE ACTION • FUNDAMENTALS</div></div><div class="card cyan" style="min-height:auto;padding:10px 14px">🟢 ENGINE READY<br><span class="muted">NSE • BSE • INDEX • STOCKS</span></div></div>',unsafe_allow_html=True)
st.markdown('<div class="line"></div>',unsafe_allow_html=True)

# ----------------------------- DASHBOARD -----------------------------
if st.session_state.page=="Dashboard":
    st.subheader("Market Command Center")
    syms=list(INDEXES.values()); df=market_table(syms)
    cols=st.columns(6)
    for c,s in zip(cols,syms[:6]):
        r=daily_row(s)
        if r:c.markdown(f'<div class="card {"green" if r["Change %"]>=0 else "red"}"><b>{r["Name"]}</b><div class="kpi">{r["LTP"]:,.2f}</div><span class="muted">{r["Change %"]:+.2f}% today</span></div>',unsafe_allow_html=True)
    st.markdown("### 🔥 Quick Market Screens")
    buttons=["Gainers","Losers","Most Active","52W High","52W Low","Penny","Breakout","Breakdown","Reversal Bull","Reversal Bear","Candlestick","Potential Multibagger"]
    for i in range(0,len(buttons),4):
        cc=st.columns(4)
        for c,b in zip(cc,buttons[i:i+4]):
            if c.button(b,key="dash_"+b,use_container_width=True):st.session_state.page=b;st.rerun()
    st.markdown("### 📊 Indian Market Snapshot")
    stockdf=market_table(list(CORE.keys())[:25])
    if not stockdf.empty:
        a,b,c=st.columns(3)
        with a:st.markdown('<div class="card green"><b>Top Gainers</b></div>',unsafe_allow_html=True);st.dataframe(stockdf.nlargest(5,"Change %")[["Symbol","LTP","Change %"]],hide_index=True,use_container_width=True)
        with b:st.markdown('<div class="card red"><b>Top Losers</b></div>',unsafe_allow_html=True);st.dataframe(stockdf.nsmallest(5,"Change %")[["Symbol","LTP","Change %"]],hide_index=True,use_container_width=True)
        with c:st.markdown('<div class="card gold"><b>Near 52W High</b></div>',unsafe_allow_html=True);st.dataframe(stockdf.nlargest(5,"LTP")[["Symbol","LTP","52W High"]],hide_index=True,use_container_width=True)


# ----------------------------- SMART STOCK FINDER -----------------------------
elif st.session_state.page=="Smart Stock Finder":
    st.subheader("🎯 Smart Stock Finder")
    st.caption("Nifty 500 research shortlist • Trend + EMA200 + RSI + Volume expansion + 52W location. Not a buy/sell guarantee.")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        exchange = st.selectbox("Exchange", ["NSE"], index=0)
    with c2:
        direction = st.selectbox("Direction", ["BOTH","BULLISH","BEARISH"], index=0)
    with c3:
        min_score = st.slider("Minimum score", 0, 100, 65, 5)
    with c4:
        scan_count = st.selectbox("Scan universe", [50,100,250,500], index=3)

    d1,d2,d3,d4 = st.columns(4)
    with d1: min_vol_ratio = st.slider("Min Volume / 20D", 0.50, 3.00, 1.20, 0.05)
    with d2: max_high_dist = st.slider("Max distance from 52W high %", 1.0, 30.0, 12.0, 1.0)
    with d3: rsi_min = st.slider("RSI min", 20, 60, 42, 1)
    with d4: rsi_max = st.slider("RSI max", 50, 90, 68, 1)

    symbol_filter = st.text_input("Optional symbol/company filter", placeholder="e.g. BANK, TATA, RELIANCE").strip()

    st.info(f"Universe: Nifty 500 • Scan: top {scan_count} • Ranking: Score ↓ → Volume expansion ↓ → 52W distance ↑")

    if st.button("🎯 FIND BEST STOCKS NOW", type="primary", use_container_width=True):
        with st.spinner(f"Scanning up to {scan_count} Nifty stocks..."):
            st.session_state.smart_finder = smart_finder_scan(
                direction, min_score, min_vol_ratio, max_high_dist,
                rsi_min, rsi_max, scan_count, symbol_filter
            )

    if "smart_finder" not in st.session_state:
        st.session_state.smart_finder = pd.DataFrame()

    if not st.session_state.smart_finder.empty:
        df = st.session_state.smart_finder.copy()
        st.success(f"{len(df)} candidates found • sorted by research quality, not alphabetically")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download Finder CSV", df.to_csv(index=False).encode(),
                           "smart_stock_finder_top500.csv", "text/csv",
                           use_container_width=True)
    else:
        st.caption("Run the finder to generate the ranked shortlist.")


# ----------------------------- MULTIBAGGER HUNTER UI -----------------------------
elif st.session_state.page=="🔥 Multibagger Hunter":
    st.subheader("🔥 Multibagger Hunter")
    st.caption("Fundamental-first Nifty 500 discovery engine • high-quality candidates, not guaranteed multibaggers.")
    a,b,c=st.columns(3)
    with a: mode=st.selectbox("Strategy", ["STRICT","EARLY"], help="STRICT keeps dividend yield >1%. EARLY removes that gate to avoid missing reinvesting growth companies.")
    with b: min_mb_score=st.slider("Minimum quality score", 0, 100, 70, 5)
    with c: mb_filter=st.text_input("Optional symbol/company", placeholder="e.g. TATA, BEL, TRENT").strip()
    st.info("Formula: growth + EPS + ROCE/ROE + margins + cash flow + valuation + promoter quality + balance-sheet strength → then intersect with Nifty 500.")
    if st.button("🔥 FIND MULTIBAGGER CANDIDATES", type="primary", use_container_width=True):
        with st.spinner("Running fundamental screen and matching Nifty 500..."):
            st.session_state.multibagger_result, st.session_state.multibagger_error = multibagger_hunter(mode,min_mb_score,mb_filter)
    if "multibagger_result" not in st.session_state: st.session_state.multibagger_result=pd.DataFrame()
    if "multibagger_error" not in st.session_state: st.session_state.multibagger_error=""
    if st.session_state.multibagger_error: st.error(st.session_state.multibagger_error)
    if not st.session_state.multibagger_result.empty:
        df=st.session_state.multibagger_result
        st.success(f"{len(df)} Nifty 500 candidates found • ranked by fundamental quality")
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("⬇️ Download Multibagger CSV",df.to_csv(index=False).encode(),"vs_flow_multibagger_hunter.csv","text/csv",use_container_width=True)
    else:
        st.caption("Run the hunter to generate the ranked shortlist.")

# ----------------------------- MARKET / STOCK SCREENS -----------------------------
elif st.session_state.page in ["Gainers","Losers","Most Active","ATH","ATL","52W High","52W Low","Penny","Breakout","Breakdown","Reversal Bull","Reversal Bear","Candlestick","Potential Multibagger","Bull Trend","Bear Trend"]:
    labels={"Gainers":"Top Gainers","Losers":"Top Losers","Most Active":"Most Active Stocks","ATH":"All Time High Candidates","ATL":"All Time Low Candidates","52W High":"52 Week High","52W Low":"52 Week Low","Penny":"Penny Stocks","Breakout":"Breakout Scanner","Breakdown":"Breakdown Scanner","Reversal Bull":"Bullish Reversal Scanner","Reversal Bear":"Bearish Reversal Scanner","Candlestick":"Candlestick Pattern Scanner","Potential Multibagger":"Potential Multibagger Candidates"}
    st.subheader("🔎 "+labels.get(st.session_state.page,st.session_state.page))
    universe=st.multiselect("Universe",options=list(CORE.keys())+list(BSE_CORE.keys()),default=list(CORE.keys()),max_selections=120)
    if st.button("🚀 RUN SCANNER",type="primary",use_container_width=True):
        st.session_state.scan=scan_category(universe,st.session_state.page)
    if not st.session_state.scan.empty:
        st.dataframe(st.session_state.scan.sort_values("Change %",ascending=False),use_container_width=True,hide_index=True)
        st.download_button("⬇️ Download CSV",st.session_state.scan.to_csv(index=False).encode(),"vs_flow_india_scan.csv","text/csv",use_container_width=True)
    else:st.info("Select universe → Run Scanner")
    if st.session_state.page=="Potential Multibagger":st.caption("This is a research shortlist, not a prediction or guarantee. Fundamental validation should be added before treating any candidate as investment-worthy.")

# ----------------------------- VS FLOW OB + TREND SCANNER -----------------------------
elif st.session_state.page=="VS FLOW OB + Trend":
    st.subheader("🔥 VS FLOW OB + TREND SCANNER")
    st.caption("Separate filter: 1M → 1W → 1D → 4H → 1H ACTIVE OB + Trend + Premium/Discount. OB proximity is the primary filter.")
    universe=st.multiselect("Stocks to scan",list(CORE.keys())+list(BSE_CORE.keys()),default=list(CORE.keys())[:20],max_selections=120)
    if st.button("🚀 SCAN OB + TREND",type="primary",use_container_width=True):
        rows=[]
        for s in universe:
            r=ob_trend_scan(s)
            if r: rows.append(r)
        st.session_state.scan=pd.DataFrame(rows)
    if not st.session_state.scan.empty:
        df=st.session_state.scan.copy()
        c1,c2,c3=st.columns(3)
        with c1: st.metric("BUY WATCH",int(df.Status.eq("🟢 BUY WATCH").sum()))
        with c2: st.metric("SELL WATCH",int(df.Status.eq("🔴 SELL WATCH").sum()))
        with c3: st.metric("OB TOUCH / NEAR",int(df.Status.str.contains("OB TOUCH|OB NEAR",regex=True).sum()))
        order={"🟢 BUY WATCH":0,"🔴 SELL WATCH":0,"🟢 BULL OB TOUCH":1,"🔴 BEAR OB TOUCH":1,"🟡 BULL OB NEAR":2,"🟡 BEAR OB NEAR":2,"⚪ WAIT":9}
        df["__rank"]=df.Status.map(order).fillna(9)
        df=df.sort_values(["__rank","Bull Trend Score","Bear Trend Score"],ascending=[True,False,False]).drop(columns=["__rank"])
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("⬇️ Download OB + Trend CSV",df.to_csv(index=False).encode(),"vs_flow_ob_trend.csv","text/csv",use_container_width=True)
    else: st.info("Select universe → Run OB + Trend Scanner")

# ----------------------------- VS FLOW EARLY SCANNER -----------------------------
elif st.session_state.page=="VS FLOW EARLY":
    st.subheader("⚡ VS FLOW EARLY — PRE-IGNITION + TREND IGNITION SCANNER")
    st.caption("Pre-ignition + Origin OB engine • Compression → Liquidity → Fresh 4H Origin OB → Sweep → Displacement → 1H MSS → 15M confirmation → first pullback → 5M trigger. Candles are confirmation only. Independent of Core Setup.")
    a,b,c,d=st.columns(4)
    with a: st.metric("UNIVERSE",len(EARLY_UNIVERSE))
    with b: st.metric("EARLY BUY",int(st.session_state.early_scan.Status.eq("🚀 EARLY BUY").sum()) if not st.session_state.early_scan.empty else 0)
    with c: st.metric("EARLY SELL",int(st.session_state.early_scan.Status.eq("🚀 EARLY SELL").sum()) if not st.session_state.early_scan.empty else 0)
    with d: st.metric("PRE-IGNITION",int(st.session_state.early_scan.Status.str.contains("PRE-IGNITION").sum()) if not st.session_state.early_scan.empty else 0)
    if st.button("🚀 RUN VS FLOW EARLY — DEEP SCAN",type="primary",use_container_width=True):
        with st.spinner("Scanning 100 stocks + 7 indices: HTF bias → ignition → confirmation → trigger..."):
            st.session_state.early_scan=run_early_engine(EARLY_UNIVERSE)
    if not st.session_state.early_scan.empty:
        df=st.session_state.early_scan.copy()
        f1,f2,f3,f4=st.columns(4)
        with f1: view=st.selectbox("Filter",["ALL","EARLY BUY","EARLY SELL","WATCH BUY","WATCH SELL","PRE-IGNITION BUY","PRE-IGNITION SELL","NO CHASE"])
        with f2: min_score=st.slider("Minimum score",0,20,7)
        with f3: only_fresh=st.checkbox("Fresh ignition only",True)
        with f4: only_no_chase=st.checkbox("No-chase only",False)
        if view!="ALL":
            df=df[df.Status.str.contains(view,regex=False)]
        df=df[df.Score.str.split('/').str[0].astype(int)>=min_score]
        if only_fresh: df=df[df.Status.str.contains("EARLY|WATCH")]
        if only_no_chase: df=df[df.Chase=="NO"]
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("⬇️ Download VS FLOW EARLY CSV",df.to_csv(index=False).encode(),"vs_flow_early.csv","text/csv",use_container_width=True)
        st.info("Execution rule: PRE-IGNITION is watch-only. A+ Origin OB = liquidity + displacement + BOS/CHoCH + FVG + freshness. Candlestick patterns (including Shooting Star) are confirmation only, never standalone entries. EARLY requires fresh 1H/15M structure plus 5M trigger. Never chase. Before any trade, manually confirm 1M, 1W, 1D, 4H, 1H, 15M and 5M; Core Setup remains the higher-confidence confirmation engine.")
    else:
        st.info("Run the Deep Scan. The engine first ranks the full 107-instrument universe on 1D/4H/1H, then performs the expensive 15M/5M deep scan only on the strongest 35 candidates.")


# ----------------------------- VS FLOW SCALPER -----------------------------
elif st.session_state.page=="VS FLOW Scalper":
    st.subheader("⚡ VS FLOW SCALPER V1")
    st.caption("5M radar • EMA 9/20 trend filter • VWAP • liquidity sweep • displacement • first pullback • manual 1M confirmation")
    universe=st.multiselect("Stocks / indices to scan",list(ALL.keys()),default=list(CORE.keys())[:25],max_selections=120)
    if st.button("⚡ RUN SCALPER RADAR",type="primary",use_container_width=True):
        st.session_state.scalper_scan=pd.DataFrame([vsflow_scalper_v1(x) for x in universe])
    df=st.session_state.get("scalper_scan",pd.DataFrame())
    if not df.empty:
        a,b,c=st.columns(3); a.metric("A+ SCALP",int(df.Status.eq("🟢 A+ SCALP").sum())); b.metric("WATCH",int(df.Status.eq("🟡 WATCH").sum())); c.metric("NO TRADE",int(df.Status.eq("🔴 NO TRADE").sum()))
        st.dataframe(df.sort_values(["Status","Score"],ascending=[True,False]),use_container_width=True,hide_index=True)
        st.download_button("⬇️ DOWNLOAD SCALPER RADAR",df.to_csv(index=False).encode(),"vs_flow_scalper_india.csv","text/csv",use_container_width=True)
    else: st.info("Select universe → Run Scalper Radar")

# ----------------------------- VS FLOW SCANNER -----------------------------
elif st.session_state.page=="VS FLOW Scanner":
    st.subheader("⚡ VS FLOW SMC Scanner")
    st.caption("Core = 4H OB + 1H BOS/CHoCH + 15M FVG + 5M Trigger. 1H liquidity sweep is an optional bonus → 5/5 A+.")
    universe=st.multiselect("Stocks to scan",list(CORE.keys())+list(BSE_CORE.keys()),default=list(CORE.keys())[:15])
    if st.button("🚀 SCAN VS FLOW",type="primary",use_container_width=True):
        rows=[]
        for s in universe:
            rows.append(vsflow(s))
        st.session_state.scan=pd.DataFrame(rows)
    if not st.session_state.scan.empty:
        df=st.session_state.scan; hits=df[df.Score.isin(["4/5","5/5"])].copy()
        if hits.empty:st.warning("No 4/5+ setup right now.")
        else:
            st.success(f"{len(hits)} setup(s) • 4/5 = chart review • 5/5 = A+ engine alignment")
            st.dataframe(hits,use_container_width=True,hide_index=True)
            st.download_button("⬇️ Download VS FLOW setups",hits.to_csv(index=False).encode(),"vs_flow_india_setups.csv","text/csv",use_container_width=True)

# ----------------------------- CHART / ASSET -----------------------------
elif st.session_state.page in ["Chart","All Stocks","Indices"]:
    st.subheader("📈 Chart & Asset Intelligence")
    q=st.text_input("Search stock / index",value=st.session_state.asset)
    matches=[s for s in ALL if q.lower() in s.lower() or ALL[s].lower().find(q.lower())>=0]
    if matches: st.session_state.asset=st.selectbox("Select",matches,format_func=lambda s:f"{ALL[s]} • {s}")
    s=st.session_state.asset
    x=get_data(s,"1d","1y")
    if x.empty:st.error("No data available for this symbol.")
    else:
        r=daily_row(s)
        if r:
            a,b,c,d=st.columns(4);a.metric("LTP",f"₹{r['LTP']:,.2f}" if s.endswith((".NS",".BO")) else f"{r['LTP']:,.2f}");b.metric("1D",f"{r['Change %']:+.2f}%");c.metric("52W High",f"{r['52W High']:,.2f}");d.metric("52W Low",f"{r['52W Low']:,.2f}")
        fig=go.Figure(go.Candlestick(x=x.index,open=x.Open,high=x.High,low=x.Low,close=x.Close,name=s))
        fig.update_layout(template="plotly_dark",height=600,xaxis_rangeslider_visible=False,margin=dict(l=10,r=10,t=25,b=10))
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("### ⚡ VS FLOW Check")
        st.dataframe(pd.DataFrame([vsflow(s)]),use_container_width=True,hide_index=True)

# ----------------------------- SPECIAL MODULES -----------------------------
elif st.session_state.page=="Breakout / Breakdown":
    st.session_state.page="Breakout";st.rerun()
elif st.session_state.page=="Reversal Scanner":
    st.session_state.page="Reversal Bull";st.rerun()
elif st.session_state.page=="Chart Patterns":
    st.subheader("📐 Chart Pattern Scanner")
    st.info("V1 UI is ready. Next engine layer: Double Top/Bottom, H&S, Triangle, Flag, Pennant, Cup & Handle, Rounding Top/Bottom, Wedges and pattern strength scoring.")
elif st.session_state.page=="Candlestick Patterns":
    st.session_state.page="Candlestick";st.rerun()
elif st.session_state.page=="Technical Scanner":
    st.subheader("📊 Technical Scanner")
    st.info("V1 foundation: trend, SMA20/50, volume, 52W position and price action. Next layer can add RSI, MACD, ADX, ATR, VWAP, Ichimoku and multi-timeframe scoring.")
elif st.session_state.page=="Fundamental Scanner":
    st.subheader("🏦 Fundamental Scanner")
    st.info("Next data layer: market cap, P/E, P/B, ROE, ROCE, debt/equity, sales growth, profit growth, EPS, promoter holding and FII/DII changes.")
elif st.session_state.page=="FII / DII":
    st.subheader("🏛️ FII / DII Activity")
    st.info("Module reserved for daily cash/derivatives institutional flow and historical trend charts.")
elif st.session_state.page=="Options":
    st.subheader("🔢 Options & Option Chain")
    st.info("Module reserved for OI, change OI, volume, IV, PCR, max pain and strike-wise activity.")
elif st.session_state.page=="IPO / Listings":
    st.subheader("🚀 IPO / Listings")
    st.info("Module reserved for upcoming IPOs, SME IPOs, listing calendar and issue statistics.")
elif st.session_state.page=="Earnings / Events":
    st.subheader("📰 Earnings / Corporate Events")
    st.info("Module reserved for earnings, dividends, splits, bonuses, rights and major corporate actions.")
elif st.session_state.page=="Market Pulse":
    st.subheader("🌡️ Market Pulse")
    st.info("Next layer: advances/declines, volume breadth, sector rotation, volatility and market-wide heatmap.")
elif st.session_state.page=="Watchlist":
    st.subheader("⭐ Watchlist")
    st.info("Watchlist manager will be connected to the scanner and alert engine in V2.")
elif st.session_state.page=="Risk Calculator":
    st.subheader("🛡️ Risk Calculator")
    a,b,c=st.columns(3);account=a.number_input("Account size",1000.0,100000000.0,100000.0,1000.0);risk=b.number_input("Risk %",0.1,5.0,.5,.1);rr=c.number_input("RR",1.0,10.0,2.0,.5)
    entry=st.number_input("Entry",0.0);sl=st.number_input("Stop Loss",0.0);dist=abs(entry-sl);risk_money=account*risk/100
    st.metric("Max loss",f"₹{risk_money:,.2f}"); st.metric("Target profit",f"₹{risk_money*rr:,.2f}"); st.info("Position size = risk budget ÷ stop distance, adjusted for lot/contract multiplier.")

st.markdown("---")
st.caption("VS FLOW INDIA V1 • Core Setup + OB + Trend + VS FLOW EARLY • NSE + BSE architecture • SMC • Breakout • Reversal • ATH/ATL • Penny • Candlestick • Technical • Fundamental • Potential Multibagger • Options • FII/DII")
st.caption("⚠️ Scanner outputs are research signals/shortlists, not guaranteed predictions. Full NSE/BSE coverage requires a reliable exchange/security-master and market-data feed.")
