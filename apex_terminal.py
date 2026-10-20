# APEX MARKET TERMINAL — COMPLETE & FIXED BUILD



import streamlit as st

import yfinance as yf

import pandas as pd

import numpy as np

from datetime import datetime, time as dtime

import plotly.graph_objects as go

from plotly.subplots import make_subplots

import time

import pytz

import requests

from io import StringIO

import re

from concurrent.futures import ThreadPoolExecutor, as_completed

import xml.etree.ElementTree as ET



# -------------------------------------------------

# Page Config

# -------------------------------------------------

st.set_page_config(

    page_title="Apex Market Terminal",

    page_icon="📈",

    layout="wide",

    initial_sidebar_state="expanded"

)



# -------------------------------------------------

# Hide Default UI

# -------------------------------------------------

st.markdown("""

    <style>

    #MainMenu {visibility: hidden;}

    footer {visibility: hidden;}

    header {visibility: hidden;}

    .stAppToolbar {visibility: hidden !important;}

    div[data-testid="stDecoration"] {display: none !important;}

    </style>

""", unsafe_allow_html=True)



# -------------------------------------------------

# Session State

# -------------------------------------------------

if "watchlist" not in st.session_state:

    st.session_state.watchlist = ["RELIANCE", "HDFCBANK", "INFY", "TCS"]



# -------------------------------------------------

# CSS Styling & Theme Overrides

# -------------------------------------------------

st.markdown("""

    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {

        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);

        color: #ffffff;

    }

    section[data-testid="stSidebar"] {

        background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%);

        border-right: 1px solid #334155;

    }



    /* 1. High contrast labels & readable radio text for Select Stock and Timeframe */

    label, [data-testid="stWidgetLabel"] p, .stRadio label, div[role="radiogroup"] p, div[role="radiogroup"] label {

        color: #ffffff !important;

        font-weight: 600 !important;

        font-size: 14px !important;

    }



    /* 2. Heatmap-style cards for Market Indices (No Triangles) */

    .card-up {

        background: rgba(16, 185, 129, 0.25) !important;

        border: 1px solid #10b981 !important;

        border-radius: 8px;

        padding: 10px 6px !important;

        text-align: center;

        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);

        min-height: 75px !important;

    }

    .card-down {

        background: rgba(239, 68, 68, 0.25) !important;

        border: 1px solid #ef4444 !important;

        border-radius: 8px;

        padding: 10px 6px !important;

        text-align: center;

        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);

        min-height: 75px !important;

    }

    .card-neutral {

        background: rgba(51, 65, 85, 0.5) !important;

        border: 1px solid #64748b !important;

        border-radius: 8px;

        padding: 10px 6px !important;

        text-align: center;

        min-height: 75px !important;

    }



    .index-title { 

        font-size: 11px !important; font-weight: 700; color: #ffffff !important; 

        letter-spacing: 0.4px; text-transform: uppercase; 

        margin-bottom: 2px !important; line-height: 1.1;

    }

    .index-price { 

        font-size: 15px !important; font-weight: 800; color: #ffffff !important; 

        line-height: 1.15 !important; margin: 2px 0 !important;

    }

    .index-change-up { font-size: 11px !important; font-weight: 700; color: #34d399 !important; }

    .index-change-down { font-size: 11px !important; font-weight: 700; color: #fca5a5 !important; }



    .section-header {

        font-size: 18px; font-weight: 700; color: #ffffff !important;

        margin-bottom: 8px; margin-top: 10px;

    }



    /* Section Container Box */

    .styled-box {

        background: rgba(30, 41, 59, 0.8);

        border: 1px solid rgba(99, 102, 241, 0.4);

        border-radius: 10px;

        padding: 14px;

        margin-bottom: 12px;

        color: #ffffff !important;

    }



    /* Built Up Grid Styles */

    .bu-card {

        border-radius: 8px;

        padding: 10px;

        margin-bottom: 8px;

        color: #ffffff;

    }

    .bu-sc { background: rgba(16, 185, 129, 0.25); border: 1px solid #10b981; }

    .bu-lb { background: rgba(59, 130, 246, 0.25); border: 1px solid #3b82f6; }

    .bu-sb { background: rgba(239, 68, 68, 0.25); border: 1px solid #ef4444; }

    .bu-lu { background: rgba(245, 158, 11, 0.25); border: 1px solid #f59e0b; }



    .bu-title { font-weight: 700; font-size: 13px; margin-bottom: 6px; text-transform: uppercase; color: #ffffff; }

    .bu-item { font-size: 12px; padding: 3px 0; color: #f1f5f9; border-bottom: 1px dotted rgba(255,255,255,0.15); }

    

    /* Dataframe overrides for high visibility */

    .dataframe, div[data-testid="stTable"], .stDataFrame { color: #ffffff !important; }

    </style>

""", unsafe_allow_html=True)



# -------------------------------------------------

# Helpers & Data Fetching

# -------------------------------------------------

def nse_session_headers():

    return {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",

        "Accept": "application/json, text/plain, */*",

        "Accept-Language": "en-US,en;q=0.9",

        "Referer": "https://www.nseindia.com",

    }



@st.cache_data(ttl=15)

def fetch_yahoo_quote(ticker: str):

    if not ticker or ticker in ("GIFT_NIFTY", "US_TECH_FUT", "US_30_FUT"):

        return None

    try:

        t = yf.Ticker(ticker)

        hist = t.history(period="2d", interval="5m")

        if hist is not None and not hist.empty:

            price = float(hist["Close"].iloc[-1])

            prev = float(hist["Close"].iloc[0])

            change = price - prev

            pct = (change / prev * 100) if prev else 0

            return {"price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2)}

    except Exception:

        pass

    return None



@st.cache_data(ttl=20, show_spinner=False)

def fetch_tradingview_quote(tv_symbol: str):

    try:

        url = "https://scanner.tradingview.com/america/scan"

        payload = {"symbols": {"tickers": [tv_symbol]}, "columns": ["close", "change", "change_abs"]}

        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.post(url, json=payload, headers=headers, timeout=5)

        if r.status_code == 200:

            rows = r.json().get("data", [])

            if rows and rows[0].get("d"):

                vals = rows[0]["d"]

                price, pct, change = vals[0], vals[1], vals[2]

                if price and float(price) > 0:

                    return {"price": round(float(price), 2), "change": round(float(change or 0), 2), "pct": round(float(pct or 0), 2)}

    except Exception:

        pass

    return None



# GIFT Nifty Fallback

@st.cache_data(ttl=15, show_spinner=False)

def fetch_moneycontrol_gift_nifty():

    url = "https://www.moneycontrol.com/live-index/gift-nifty?symbol=in;gsx"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:

        r = requests.get(url, headers=headers, timeout=6)

        if r.status_code == 200:

            html = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', r.text))

            m = re.search(r'([+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*\$\s*([+-]?\d+\.?\d*)\s*%', html)

            nums = re.findall(r'(2[0-9],\d{3}(?:\.\d{1,2})?)', html)

            if nums:

                price = float(nums[0].replace(",", ""))

                change = float(m.group(1).replace(",", "")) if m else 0.0

                pct = float(m.group(2)) if m else 0.0

                if 15000 < price < 45000:

                    return {"price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2)}

    except Exception:

        pass

    return None



# TradingEconomics Fallback

@st.cache_data(ttl=20, show_spinner=False)

def fetch_tradingeconomics_quote(url_path: str):

    url = f"https://tradingeconomics.com/{url_path}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:

        r = requests.get(url, headers=headers, timeout=6)

        if r.status_code == 200:

            text = r.text

            price_match = re.search(r'id="last-value"[^>]*>([\d,]+\.?\d*)', text)

            chg_match = re.search(r'id="change"[^>]*>([+-]?[\d,]+\.?\d*)', text)

            pct_match = re.search(r'id="pchange"[^>]*>([+-]?[\d,]+\.?\d*)', text)

            if price_match:

                price = float(price_match.group(1).replace(",", ""))

                change = float(chg_match.group(1).replace(",", "")) if chg_match else 0.0

                pct = float(pct_match.group(1).replace(",", "")) if pct_match else 0.0

                return {"price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2)}

    except Exception:

        pass

    return None



def fetch_live_instrument(key: str, tv_symbols=(), yahoo_ticker: str = None):

    if isinstance(tv_symbols, str):

        tv_symbols = (tv_symbols,)

    for symbol in tv_symbols:

        q = fetch_tradingview_quote(symbol)

        if q: return q

    if key == "GIFT_NIFTY":

        q = fetch_moneycontrol_gift_nifty()

        if q: return q

    elif key == "US_TECH_FUT":

        q = fetch_tradingeconomics_quote("us100:ind")

        if q: return q

    elif key == "US_30_FUT":

        q = fetch_tradingeconomics_quote("indu:ind")

        if q: return q

    if yahoo_ticker:

        q = fetch_yahoo_quote(yahoo_ticker)

        if q: return q

    return None



# China & Asia Business News Filter

@st.cache_data(ttl=1800, show_spinner=False)

def get_china_asia_deep_business_news():

    items = []

    queries = [

        "China+economy+PBOC+stimulus+property+when:1d",

        "Asia+markets+Central+Bank+trade+GDP+when:1d"

    ]

    headers = {"User-Agent": "Mozilla/5.0"}

    seen = set()

    for q in queries:

        try:

            rss = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"

            nr = requests.get(rss, headers=headers, timeout=6)

            if nr.ok:

                root = ET.fromstring(nr.content)

                for item in root.findall(".//item"):

                    title = (item.findtext("title") or "").strip()

                    link = (item.findtext("link") or "").strip()

                    # Filter out non-business / sports keywords

                    if any(sp in title.lower() for sp in ["match", "league", "cup", "vs", "score", "cricket", "football", "tennis", "olympics"]):

                        continue

                    if title and title not in seen:

                        seen.add(title)

                        items.append({"title": title, "link": link})

        except Exception:

            continue

    return items[:6]



# Universe & Heatmap

@st.cache_data(ttl=3600)

def get_stock_universe():

    return [

        "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",

        "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL",

        "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY",

        "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",

        "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK",

        "INFY", "ITC", "JSWSTEEL", "KOTAKBANK", "LT",

        "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC",

        "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA",

        "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TCS", "TECHM",

        "TITAN", "ULTRACEMCO", "UPL", "WIPRO"

    ]



@st.cache_data(ttl=60)

def get_nifty50_heatmap(universe: list):

    try:

        tickers = [f"{s}.NS" for s in universe]

        data = yf.download(tickers, period="2d", group_by="ticker", progress=False, threads=True)

        rows = []

        for sym in universe:

            try:

                hist = data[f"{sym}.NS"] if f"{sym}.NS" in data.columns.get_level_values(0) else None

                if hist is None or hist.empty: continue

                close = hist["Close"].dropna()

                if len(close) < 2: continue

                last, prev = float(close.iloc[-1]), float(close.iloc[-2])

                pct = (last - prev) / prev * 100 if prev else 0

                rows.append({"Symbol": sym, "LTP": round(last, 2), "% Chg": round(pct, 2)})

            except Exception:

                continue

        return pd.DataFrame(rows)

    except Exception:

        return pd.DataFrame()



# Stock Historical Data & Indicators

@st.cache_data(ttl=60)

def fetch_stock_chart_data(ticker: str, timeframe: str):

    tf_map = {"30 Min": ("1mo", "30m"), "1 Hr": ("2mo", "60m"), "Daily": ("1y", "1d")}

    period, interval = tf_map.get(timeframe, ("1y", "1d"))

    df = yf.download(f"{ticker}.NS", period=period, interval=interval, progress=False)

    if isinstance(df.columns, pd.MultiIndex):

        df.columns = df.columns.get_level_values(0)

    

    # Calculate indicators

    df['SMA20'] = df['Close'].rolling(20).mean()

    df['SMA50'] = df['Close'].rolling(50).mean()

    

    # EMA20 & EMA50

    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()

    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()

    

    # RSI

    delta = df['Close'].diff()

    gain = (delta.where(delta > 0, 0)).rolling(14).mean()

    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss

    df['RSI'] = 100 - (100 / (1 + rs))

    

    # MACD

    ema12 = df['Close'].ewm(span=12, adjust=False).mean()

    ema26 = df['Close'].ewm(span=26, adjust=False).mean()

    df['MACD'] = ema12 - ema26

    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    

    # Bollinger Bands

    df['BB_Mid'] = df['Close'].rolling(20).mean()

    bb_std = df['Close'].rolling(20).std()

    df['BB_Upper'] = df['BB_Mid'] + (bb_std * 2)

    df['BB_Lower'] = df['BB_Mid'] - (bb_std * 2)



    return df



# F&O Built-Up Classification Matrix

@st.cache_data(ttl=90, show_spinner=False)

def calculate_fno_builtup(universe: list):

    top15 = universe[:15]

    tickers = [f"{s}.NS" for s in top15]

    data = yf.download(tickers, period="5d", group_by="ticker", progress=False, threads=True)

    builtup = {"Short Covering": [], "Long Build Up": [], "Short Build Up": [], "Long Unwinding": []}

    

    for sym in top15:

        try:

            hist = data[f"{sym}.NS"] if f"{sym}.NS" in data.columns.get_level_values(0) else None

            if hist is None or len(hist) < 2: continue

            close = hist["Close"].dropna()

            vol = hist["Volume"].dropna()

            

            p_chg = float(close.iloc[-1]) - float(close.iloc[-2])

            v_chg = float(vol.iloc[-1]) - float(vol.iloc[-2])

            pct = round((p_chg / float(close.iloc[-2])) * 100, 2)

            item_str = f"<b>{sym}</b> ({pct:+.1f}%)"



            if p_chg >= 0 and v_chg < 0:

                builtup["Short Covering"].append(item_str)

            elif p_chg >= 0 and v_chg >= 0:

                builtup["Long Build Up"].append(item_str)

            elif p_chg < 0 and v_chg >= 0:

                builtup["Short Build Up"].append(item_str)

            else:

                builtup["Long Unwinding"].append(item_str)

        except Exception:

            continue

    return builtup



@st.cache_data(ttl=300, show_spinner=False)

def get_corporate_actions(universe: list):

    headers = nse_session_headers()

    session = requests.Session()

    try:

        session.get("https://www.nseindia.com", headers=headers, timeout=5)

        url = "https://www.nseindia.com/api/corporates-corporateActions?index=equities"

        r = session.get(url, headers=headers, timeout=8)

        if r.status_code == 200:

            data = r.json()

            rows = data if isinstance(data, list) else data.get("data", [])

            uni_set = set(universe)

            out = []

            for item in rows:

                sym = (item.get("symbol") or "").strip().upper()

                if sym in uni_set:

                    out.append({

                        "Symbol": sym,

                        "Purpose": item.get("purpose", "—")[:60],

                        "Ex-Date": item.get("exDate", "—"),

                        "Record Date": item.get("recordDate", "—")

                    })

            if out:

                return pd.DataFrame(out).drop_duplicates().head(10)

    except Exception:

        pass

    return pd.DataFrame()



# -------------------------------------------------

# App Layout & Execution

# -------------------------------------------------

ist = pytz.timezone("Asia/Kolkata")

current_time = datetime.now(ist).strftime("%d %b %Y • %H:%M:%S IST")



st.markdown("# 📈 Apex Market Terminal")

st.caption(f"Live Indian Equities & Global Derivatives • **{current_time}**")



universe = get_stock_universe()



# 1. High contrast Stock selection & Timeframe controls

col1, col2, col3 = st.columns([2.5, 1.2, 1])

with col1:

    selected_stock = st.selectbox("📌 Select Stock (NSE)", options=universe, index=0, key="selected_stock")

with col2:

    timeframe = st.radio("⏱️ Timeframe", ["30 Min", "1 Hr", "Daily"], index=0, horizontal=True)

with col3:

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Refresh Data", use_container_width=True):

        st.cache_data.clear()

        st.rerun()



st.markdown("---")



# 2. Market Indices Section (Heatmap Style Cards)

st.markdown('<div class="section-header">Market Indices & Global Instruments</div>', unsafe_allow_html=True)



instruments = {

    "GIFT NIFTY 50": ("live", "GIFT_NIFTY", ("NSEIX:NIFTY1!",), None),

    "NIFTY 50": ("cash", "^NSEI", (), "^NSEI"),

    "BANK NIFTY": ("cash", "^NSEBANK", (), "^NSEBANK"),

    "BSE SENSEX": ("cash", "^BSESN", (), "^BSESN"),

    "US TECH 100": ("live", "US_TECH_FUT", ("CME_MINI:NQ1!", "NASDAQ:NDX"), "^NDX"),

    "US 30 FUT": ("live", "US_30_FUT", ("CBOT:YM1!", "DJ:DJI"), "^DJI"),

}



cols = st.columns(6)

for j, (name, meta) in enumerate(instruments.items()):

    mode, key, tv_symbols, yahoo_tk = meta

    data = fetch_yahoo_quote(yahoo_tk) if mode == "cash" else fetch_live_instrument(key, tv_symbols, yahoo_tk)

    

    with cols[j]:

        if data:

            chg = data["change"]

            card_class = "card-up" if chg > 0 else ("card-down" if chg < 0 else "card-neutral")

            change_class = "index-change-up" if chg >= 0 else "index-change-down"

            sign = "+" if chg >= 0 else ""

            

            st.markdown(f"""

            <div class="{card_class}">

                <div class="index-title">{name}</div>

                <div class="index-price">{data['price']:,.2f}</div>

                <div class="{change_class}">{sign}{chg:.2f} ({sign}{data['pct']:.2f}%)</div>

            </div>

            """, unsafe_allow_html=True)

        else:

            st.markdown(f"""

            <div class="card-neutral">

                <div class="index-title">{name}</div>

                <div class="index-price" style="font-size:12px; color:#94a3b8;">Offline</div>

            </div>

            """, unsafe_allow_html=True)



st.markdown("---")



# Technical Charting & Analysis Section

st.markdown(f'<div class="section-header">📊 Technical Analysis & Charting — {selected_stock}</div>', unsafe_allow_html=True)



df_chart = fetch_stock_chart_data(selected_stock, timeframe)



if not df_chart.empty:

    fig = make_subplots(

        rows=3, cols=1, 

        shared_xaxes=True, 

        vertical_spacing=0.03, 

        row_heights=[0.6, 0.2, 0.2]

    )



    # Main Price Candlestick

    fig.add_trace(go.Candlestick(

        x=df_chart.index,

        open=df_chart['Open'], high=df_chart['High'],

        low=df_chart['Low'], close=df_chart['Close'],

        name="Price"

    ), row=1, col=1)



    # Overlays

    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA20'], line=dict(color='#3b82f6', width=1), name="EMA 20"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA50'], line=dict(color='#f59e0b', width=1), name="EMA 50"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['BB_Upper'], line=dict(color='rgba(148, 163, 184, 0.5)', width=1, dash='dot'), name="BB Upper"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['BB_Lower'], line=dict(color='rgba(148, 163, 184, 0.5)', width=1, dash='dot'), name="BB Lower"), row=1, col=1)



    # Volume

    colors = ['#10b981' if c >= o else '#ef4444' for c, o in zip(df_chart['Close'], df_chart['Open'])]

    fig.add_trace(go.Bar(x=df_chart.index, y=df_chart['Volume'], marker_color=colors, name="Volume"), row=2, col=1)



    # RSI

    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['RSI'], line=dict(color='#c084fc', width=1.5), name="RSI"), row=3, col=1)

    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=3, col=1)

    fig.add_hline(y=30, line_dash="dash", line_color="#10b981", row=3, col=1)



    fig.update_layout(

        template="plotly_dark",

        height=600,

        margin=dict(l=10, r=10, t=10, b=10),

        xaxis_rangeslider_visible=False,

        paper_bgcolor='rgba(0,0,0,0)',

        plot_bgcolor='rgba(0,0,0,0)',

    )

    st.plotly_chart(fig, use_container_width=True)

else:

    st.warning("Chart data unavailable for selected symbol.")



st.markdown("---")



# Global Macro Dashboard (China & Asia Business Focus)

st.markdown('<div class="section-header">🌐 Global Macro Dashboard — China & Asia Business Focus</div>', unsafe_allow_html=True)

m_col1, m_col2 = st.columns([1.5, 1])



with m_col1:

    st.markdown("#### 📰 Top China & Asian Business Headlines")

    asia_news = get_china_asia_deep_business_news()

    if asia_news:

        for idx, item in enumerate(asia_news, 1):

            st.markdown(f"**{idx}.** [{item['title']}]({item['link']})")

    else:

        st.info("Fetching macro business news...")



with m_col2:

    st.markdown('<div class="styled-box">', unsafe_allow_html=True)

    st.markdown("#### 🎯 Market Scenario & Take")

    st.markdown("""

    - **China PBOC Policy:** Continuous liquidity injections aiming to stabilize industrial momentum.

    - **FX Volatility:** USD/JPY and USD/CNH levels remain key triggers for sudden FII shifts in Asian equities.

    - **Impact on Nifty:** Regional risk-on sentiment favors cyclical sectors (Metals, Energy & Financials).

    """)

    st.markdown('</div>', unsafe_allow_html=True)



st.markdown("---")



# Nifty 50 Heatmap

st.markdown('<div class="section-header">🔥 Nifty 50 Heatmap</div>', unsafe_allow_html=True)

heatmap_df = get_nifty50_heatmap(universe)



if not heatmap_df.empty:

    cols_per_row = 10

    for i in range(0, len(heatmap_df), cols_per_row):

        h_cols = st.columns(cols_per_row)

        for j, (_, row) in enumerate(heatmap_df.iloc[i:i+cols_per_row].iterrows()):

            color_bg = "rgba(16, 185, 129, 0.3)" if row["% Chg"] >= 0 else "rgba(239, 68, 68, 0.3)"

            border_c = "#10b981" if row["% Chg"] >= 0 else "#ef4444"

            with h_cols[j]:

                st.markdown(f"""

                <div style="background:{color_bg}; border:1px solid {border_c}; border-radius:6px; padding:6px; text-align:center; margin-bottom:6px;">

                    <div style="font-size:11px; font-weight:700; color:#ffffff;">{row['Symbol']}</div>

                    <div style="font-size:12px; font-weight:800; color:#ffffff;">{row['% Chg']:+.2f}%</div>

                </div>

                """, unsafe_allow_html=True)



st.markdown("---")



# F&O Built-Up Section (Top 15 Stocks - Positioned immediately after Heatmap)

st.markdown('<div class="section-header">⚡ F&O Built-up Analysis (Top 15 Stocks)</div>', unsafe_allow_html=True)

fno_data = calculate_fno_builtup(universe)



b_col1, b_col2, b_col3, b_col4 = st.columns(4)



with b_col1:

    st.markdown('<div class="bu-card bu-sc"><div class="bu-title">Short Covering</div>', unsafe_allow_html=True)

    for item in fno_data["Short Covering"]:

        st.markdown(f'<div class="bu-item">{item}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



with b_col2:

    st.markdown('<div class="bu-card bu-lb"><div class="bu-title">Long Build Up</div>', unsafe_allow_html=True)

    for item in fno_data["Long Build Up"]:

        st.markdown(f'<div class="bu-item">{item}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



with b_col3:

    st.markdown('<div class="bu-card bu-sb"><div class="bu-title">Short Build Up</div>', unsafe_allow_html=True)

    for item in fno_data["Short Build Up"]:

        st.markdown(f'<div class="bu-item">{item}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



with b_col4:

    st.markdown('<div class="bu-card bu-lu"><div class="bu-title">Long Unwinding</div>', unsafe_allow_html=True)

    for item in fno_data["Long Unwinding"]:

        st.markdown(f'<div class="bu-item">{item}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



st.markdown("---")



# Corporate Actions & Market Movers Section

st.markdown('<div class="section-header">📋 Corporate Actions & Market Movers</div>', unsafe_allow_html=True)



sec_col1, sec_col2 = st.columns([1.2, 1])



with sec_col1:

    st.markdown('<div class="styled-box">', unsafe_allow_html=True)

    st.markdown("#### 🏛️ Forthcoming Corporate Actions")

    corp_df = get_corporate_actions(universe)

    if not corp_df.empty:

        st.dataframe(corp_df, use_container_width=True, hide_index=True)

    else:

        st.write("No major upcoming corporate actions scheduled.")

    st.markdown('</div>', unsafe_allow_html=True)



with sec_col2:

    st.markdown('<div class="styled-box">', unsafe_allow_html=True)

    st.markdown("#### 🚀 Top Gainers & Losers")

    heatmap_sorted = heatmap_df.sort_values("% Chg", ascending=False) if not heatmap_df.empty else pd.DataFrame()

    if not heatmap_sorted.empty:

        g_tab, l_tab = st.tabs(["Gainers", "Losers"])

        with g_tab:

            st.dataframe(heatmap_sorted.head(5), use_container_width=True, hide_index=True)

        with l_tab:

            st.dataframe(heatmap_sorted.tail(5).iloc[::-1], use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)
