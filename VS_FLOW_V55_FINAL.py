from pathlib import Path
import json, math
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
    "Scanners": ["VS FLOW Scanner", "VS FLOW OB + Trend", "Breakout / Breakdown", "Reversal Scanner", "Chart Patterns", "Candlestick Patterns", "Technical Scanner", "Fundamental Scanner", "Potential Multibagger"],
    "Institutional": ["FII / DII", "Options", "IPO / Listings", "Earnings / Events"],
    "Tools": ["Chart", "Watchlist", "Risk Calculator"]
}

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

# ----------------------------- UI STATE -----------------------------
if "page" not in st.session_state: st.session_state.page="Dashboard"
if "asset" not in st.session_state: st.session_state.asset="RELIANCE.NS"
if "scan" not in st.session_state: st.session_state.scan=pd.DataFrame()

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
st.caption("VS FLOW INDIA V1 • NSE + BSE architecture • SMC • Breakout • Reversal • ATH/ATL • Penny • Candlestick • Technical • Fundamental • Potential Multibagger • Options • FII/DII")
st.caption("⚠️ Scanner outputs are research signals/shortlists, not guaranteed predictions. Full NSE/BSE coverage requires a reliable exchange/security-master and market-data feed.")
