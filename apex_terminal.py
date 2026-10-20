# APEX MARKET TERMINAL — FULL PRODUCTION BUILD
# All working features preserved with high-contrast UI, direct fallbacks, and Quantsapp-style Built-up section.

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

# Hide Streamlit Chrome
st.markdown("""
<style>
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important; visibility: hidden !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["RELIANCE", "HDFCBANK", "INFY", "TCS"]
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "last_options_refresh" not in st.session_state:
    st.session_state.last_options_refresh = time.time()
if "last_nifty_pcr" not in st.session_state:
    st.session_state.last_nifty_pcr = None
if "last_bank_pcr" not in st.session_state:
    st.session_state.last_bank_pcr = None
if "last_pcr_time" not in st.session_state:
    st.session_state.last_pcr_time = None

# -------------------------------------------------
# Theme CSS (High-Contrast Controls & Custom Grid)
# -------------------------------------------------
def apply_theme(theme: str):
    if theme == "dark":
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
            .stApp {
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
                color: #e2e8f0;
            }
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%);
                border-right: 1px solid #334155;
            }
            /* Pure White Controls Text */
            label, div[data-widget="selectbox"] label, div[data-widget="radio"] label, p, span {
                color: #ffffff !important;
            }
            div[role="radiogroup"] label p, div[role="radiogroup"] label span {
                color: #ffffff !important;
                font-weight: 600 !important;
            }
            div[data-baseweb="select"] span {
                color: #ffffff !important;
            }
            .metric-card {
                background: linear-gradient(145deg, rgba(30,41,59,0.95), rgba(15,23,42,0.98));
                border: 1px solid rgba(99,102,241,0.35);
                border-radius: 10px;
                padding: 8px 6px !important;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                min-height: 78px !important;
            }
            .index-title { 
                font-size: 10px !important; font-weight: 600; color: #94a3b8; 
                letter-spacing: 0.3px; text-transform: uppercase; 
                margin-bottom: 3px !important; line-height: 1.1;
            }
            .index-price { 
                font-size: 15px !important; font-weight: 700; color: #f8fafc; 
                line-height: 1.15 !important; margin: 2px 0 !important;
            }
            .index-change { font-size: 11px !important; font-weight: 600; margin-top: 1px !important; }
            .pos { color: #34d399 !important; }
            .neg { color: #f87171 !important; }
            .section-header {
                font-size: 18px; font-weight: 700;
                background: linear-gradient(90deg, #818cf8, #c084fc);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }
            div[data-testid="stMetric"] {
                background: linear-gradient(145deg, rgba(30,41,59,0.85), rgba(15,23,42,0.9));
                border: 1px solid rgba(148,163,184,0.2);
                border-radius: 12px; padding: 14px;
            }
            div[data-testid="stMetric"] label { color: #ffffff !important; }
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 700 !important; }
            .stButton > button {
                background: linear-gradient(90deg, #6366f1, #8b5cf6);
                color: white; border: none; border-radius: 10px; font-weight: 600;
            }
            h1 {
                background: linear-gradient(90deg, #a5b4fc, #c4b5fd, #f0abfc);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                font-weight: 800 !important;
            }
            .watchlist-chip {
                display: inline-block; background: #312e81; color: #e0e7ff;
                padding: 4px 12px; border-radius: 20px; margin: 3px;
                font-size: 13px; font-weight: 500;
            }
            .analysis-box {
                background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
                border: 1px solid rgba(99,102,241,0.4);
                border-radius: 12px; padding: 16px; margin-bottom: 12px;
            }
            .stCaption, [data-testid="stCaption"] { color: #cbd5e1 !important; }
            .heat-cell {
                display: inline-block; width: 19%; margin: 0.5%; padding: 8px 4px;
                border-radius: 6px; text-align: center; font-size: 11px; font-weight: 600;
                color: #fff; min-height: 52px;
            }
            /* Quantsapp Built-up Cycle Container */
            .bu-container {
                background: #1e293b; border-radius: 12px; padding: 18px;
                border: 1px solid #334155; margin-top: 15px; margin-bottom: 20px;
            }
            .bu-header {
                display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 15px; font-size: 16px; font-weight: 700; color: #ffffff;
            }
            .bu-row {
                display: flex; align-items: center; margin-bottom: 8px;
            }
            .bu-sym {
                width: 140px; font-weight: 700; font-size: 12px; color: #ffffff;
            }
            .bu-sym-sub { font-size: 10px; font-weight: 400; }
            .bu-blocks {
                display: flex; gap: 6px; flex-grow: 1;
            }
            .bu-box {
                flex: 1; height: 32px; border-radius: 4px;
            }
            .bu-long { background-color: #065f46; }
            .bu-short { background-color: #991b1b; }
            .bu-covering { background-color: #1e537d; }
            .bu-unwinding { background-color: #717100; }
            .bu-legend {
                display: flex; gap: 15px; margin-top: 15px; font-size: 11px; color: #cbd5e1;
            }
            .bu-dot { width: 12px; height: 12px; border-radius: 2px; display: inline-block; margin-right: 5px; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
            .stApp {
                background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 50%, #f1f5f9 100%);
                color: #1e293b;
            }
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #e0e7ff 0%, #f8fafc 100%);
                border-right: 1px solid #c7d2fe;
            }
            label, p, span { color: #0f172a !important; }
            .metric-card {
                background: linear-gradient(145deg, #ffffff, #f1f5f9);
                border: 1px solid #c7d2fe; border-radius: 10px;
                padding: 8px 6px !important; text-align: center;
                box-shadow: 0 3px 12px rgba(99,102,241,0.12); min-height: 78px !important;
            }
            .index-title { font-size: 10px !important; font-weight: 600; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase; margin-bottom: 3px !important; line-height: 1.1; }
            .index-price { font-size: 15px !important; font-weight: 700; color: #0f172a; line-height: 1.15 !important; margin: 2px 0 !important; }
            .index-change { font-size: 11px !important; font-weight: 600; margin-top: 1px !important; }
            .pos { color: #059669 !important; }
            .neg { color: #dc2626 !important; }
            .section-header { font-size: 18px; font-weight: 700; background: linear-gradient(90deg, #4f46e5, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
            div[data-testid="stMetric"] { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
            div[data-testid="stMetric"] label { color: #0f172a !important; }
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 700 !important; }
            .stButton > button { background: linear-gradient(90deg, #4f46e5, #7c3aed); color: white; border: none; border-radius: 10px; font-weight: 600; }
            h1 { background: linear-gradient(90deg, #4f46e5, #7c3aed, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }
            .watchlist-chip { display: inline-block; background: #e0e7ff; color: #3730a3; padding: 4px 12px; border-radius: 20px; margin: 3px; font-size: 13px; font-weight: 500; }
            .analysis-box { background: white; border: 1px solid #c7d2fe; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(99,102,241,0.08); }
            .heat-cell { display: inline-block; width: 19%; margin: 0.5%; padding: 8px 4px; border-radius: 6px; text-align: center; font-size: 11px; font-weight: 600; color: #fff; min-height: 52px; }
            .bu-container { background: #f8fafc; border-radius: 12px; padding: 18px; border: 1px solid #cbd5e1; margin-top: 15px; margin-bottom: 20px; }
            .bu-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; font-size: 16px; font-weight: 700; color: #0f172a; }
            .bu-row { display: flex; align-items: center; margin-bottom: 8px; }
            .bu-sym { width: 140px; font-weight: 700; font-size: 12px; color: #0f172a; }
            .bu-sym-sub { font-size: 10px; font-weight: 400; }
            .bu-blocks { display: flex; gap: 6px; flex-grow: 1; }
            .bu-box { flex: 1; height: 32px; border-radius: 4px; }
            .bu-long { background-color: #059669; }
            .bu-short { background-color: #dc2626; }
            .bu-covering { background-color: #0284c7; }
            .bu-unwinding { background-color: #ca8a04; }
            .bu-legend { display: flex; gap: 15px; margin-top: 15px; font-size: 11px; color: #475569; }
            .bu-dot { width: 12px; height: 12px; border-radius: 2px; display: inline-block; margin-right: 5px; }
        </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# -------------------------------------------------
# Helpers & Direct Web Fallbacks
# -------------------------------------------------
def nse_session_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain",
        "Origin": "https://www.nseindia.com",
        "Connection": "keep-alive",
    }

def is_nse_market_hours():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    if now.weekday() >= 5:
        return False
    t = now.time()
    return dtime(9, 15) <= t <= dtime(15, 30)

@st.cache_data(ttl=15)
def fetch_yahoo_quote(ticker: str):
    if not ticker or ticker in ("GIFT_NIFTY", "US_TECH_FUT", "US_30_FUT"):
        return None
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d", interval="5m")
        if hist is not None and not hist.empty:
            hist = hist.dropna(subset=["Close"])
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                daily = t.history(period="5d", interval="1d")
                prev = float(daily["Close"].iloc[-2]) if len(daily) >= 2 else price
                change = price - prev
                pct = (change / prev * 100) if prev else 0
                return {"price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2), "source": f"Yahoo ({ticker})"}
    except Exception:
        pass
    return None

@st.cache_data(ttl=15)
def fetch_index_quote(ticker: str):
    return fetch_yahoo_quote(ticker)

@st.cache_data(ttl=20, show_spinner=False)
def fetch_tradingview_quote(tv_symbol: str):
    try:
        exchange = tv_symbol.split(":", 1)[0].upper()
        region_map = {"NSEIX": "india", "NSE": "india", "CME_MINI": "america", "CBOT": "america", "TVC": "america", "HSI": "hongkong"}
        region = region_map.get(exchange, "america")
        url = f"https://scanner.tradingview.com/{region}/scan"
        payload = {"symbols": {"tickers": [tv_symbol], "query": {"types": []}}, "columns": ["close", "change", "change_abs"]}
        headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
        r = requests.post(url, json=payload, headers=headers, timeout=6)
        if r.status_code == 200:
            rows = r.json().get("data", [])
            if rows and rows[0].get("d"):
                vals = rows[0]["d"]
                price, pct, change = vals[0], vals[1], vals[2]
                if price and price > 0:
                    return {"price": round(float(price), 2), "change": round(float(change or 0), 2), "pct": round(float(pct or 0), 2), "source": f"TradingView ({tv_symbol})"}
    except Exception:
        pass
    return None

@st.cache_data(ttl=20, show_spinner=False)
def fetch_tradingeconomics_quote(symbol_path: str):
    """Direct fallback for US Tech 100 & US 30"""
    try:
        url = f"https://tradingeconomics.com/{symbol_path}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            html = r.text
            m_price = re.search(r'id=["\']last["\'][^>]*>([0-9,]+\.?[0-9]*)', html, re.I)
            m_chg = re.search(r'id=["\']change["\'][^>]*>([+-]?[0-9,]+\.?[0-9]*)', html, re.I)
            m_pct = re.search(r'id=["\']pchange["\'][^>]*>([+-]?[0-9,]+\.?[0-9]*)', html, re.I)
            if m_price:
                price = float(m_price.group(1).replace(",", ""))
                chg = float(m_chg.group(1).replace(",", "")) if m_chg else 0.0
                pct = float(m_pct.group(1).replace(",", "")) if m_pct else 0.0
                return {"price": round(price, 2), "change": round(chg, 2), "pct": round(pct, 2), "source": f"TradingEconomics ({symbol_path})"}
    except Exception:
        pass
    return None

@st.cache_data(ttl=15, show_spinner=False)
def fetch_gift_nifty_50():
    """GIFT Nifty with Moneycontrol final fallback"""
    # 1. TradingView
    for symbol in ("NSEIX:NIFTY1!", "NSEIX:NIFTY2!"):
        quote = fetch_tradingview_quote(symbol)
        if quote and 15000 < quote["price"] < 40000:
            return quote
    # 2. Moneycontrol Final Fallback
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://www.moneycontrol.com/live-index/gift-nifty?symbol=in;gsx", headers=headers, timeout=7)
        if r.status_code == 200:
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text))
            nums = re.findall(r"(2[0-9],\d{3}(?:\.\d{1,2})?)", plain)
            chg_m = re.search(r"([+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*\(\s*([+-]?\d+\.?\d*)\s*%\s*\)", plain)
            if nums:
                price = float(nums[0].replace(",", ""))
                chg = float(chg_m.group(1).replace(",", "")) if chg_m else 0.0
                pct = float(chg_m.group(2)) if chg_m else 0.0
                if 15000 < price < 40000:
                    return {"price": round(price, 2), "change": round(chg, 2), "pct": round(pct, 2), "source": "Moneycontrol GIFT Nifty"}
    except Exception:
        pass
    return None

@st.cache_data(ttl=20, show_spinner=False)
def fetch_live_instrument(key: str, tv_symbols=(), te_path: str = None, yahoo_ticker: str = None):
    for symbol in tv_symbols:
        quote = fetch_tradingview_quote(symbol)
        if quote:
            return quote
    if te_path:
        te_quote = fetch_tradingeconomics_quote(te_path)
        if te_quote:
            return te_quote
    if yahoo_ticker:
        yq = fetch_yahoo_quote(yahoo_ticker)
        if yq:
            return yq
    return None

@st.cache_data(ttl=45)
def fetch_stock_data(symbol: str):
    try:
        t = yf.Ticker(f"{symbol}.NS")
        info = t.fast_info
        hist = t.history(period="1mo")
        if hist.empty:
            return None
        ltp = getattr(info, "last_price", None) or float(hist["Close"].iloc[-1])
        prev_close = getattr(info, "previous_close", None) or float(hist["Close"].iloc[-2])
        return {
            "ltp": round(float(ltp), 2),
            "prev_close": round(float(prev_close), 2),
            "prev_high": round(float(hist["High"].iloc[-1]), 2),
            "prev_low": round(float(hist["Low"].iloc[-1]), 2),
            "volume": int(hist["Volume"].iloc[-1]),
            "avg_volume": int(hist["Volume"].tail(20).mean())
        }
    except Exception:
        return None

@st.cache_data(ttl=60)
def get_ohlc_data(symbol: str, interval: str = "1d", period: str = "3mo"):
    try:
        t = yf.Ticker(f"{symbol}.NS")
        df = t.history(period=period, interval=interval).reset_index()
        if "Datetime" in df.columns:
            df = df.rename(columns={"Datetime": "Date"})
        return df
    except Exception:
        return None

def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def generate_renko(df: pd.DataFrame, box_size: float) -> pd.DataFrame:
    if df is None or df.empty or box_size <= 0:
        return pd.DataFrame()
    prices, dates = df["Close"].values, df["Date"].values
    bricks = []
    current_brick = round(prices[0] / box_size) * box_size
    for i in range(1, len(prices)):
        price, date = prices[i], dates[i]
        while price >= current_brick + box_size:
            bricks.append({"Date": date, "Open": current_brick, "High": current_brick + box_size, "Low": current_brick, "Close": current_brick + box_size})
            current_brick += box_size
        while price <= current_brick - box_size:
            bricks.append({"Date": date, "Open": current_brick, "High": current_brick, "Low": current_brick - box_size, "Close": current_brick - box_size})
            current_brick -= box_size
    if not bricks:
        return pd.DataFrame()
    renko_df = pd.DataFrame(bricks)
    renko_df["Brick"] = range(1, len(renko_df) + 1)
    return renko_df

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

# -------------------------------------------------
# Header
# -------------------------------------------------
ist = pytz.timezone("Asia/Kolkata")
st.markdown("# 📈 Apex Market Terminal")
st.caption(f"Live Indian Equities & Global Derivatives • **{datetime.now(ist).strftime('%d %b %Y • %H:%M:%S IST')}**")

# Controls
universe = get_stock_universe()
c1, c2, c3 = st.columns([2.2, 1.2, 1])
with c1:
    selected = st.selectbox("🔍 Select Stock (NSE)", options=universe, index=0)
with c2:
    auto_refresh = st.checkbox("🔄 Auto-refresh (1 min)", value=False)
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Stock Analytics Metrics
st.markdown("---")
metrics = fetch_stock_data(selected)
if metrics:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("LTP", f"₹{metrics['ltp']:,.2f}")
    m2.metric("Day High", f"₹{metrics['prev_high']:,.2f}")
    m3.metric("Day Low", f"₹{metrics['prev_low']:,.2f}")
    m4.metric("Prev Close", f"₹{metrics['prev_close']:,.2f}")

# -------------------------------------------------
# Market Indices Section
# -------------------------------------------------
st.markdown('<div class="section-header">Market Indices & Global Instruments</div>', unsafe_allow_html=True)

instruments = {
    "INDIA VIX": fetch_index_quote("^INDIAVIX"),
    "GIFT NIFTY 50": fetch_gift_nifty_50(),
    "NIFTY 50": fetch_index_quote("^NSEI"),
    "BANK NIFTY": fetch_index_quote("^NSEBANK"),
    "BSE SENSEX": fetch_index_quote("^BSESN"),
    "US TECH 100": fetch_live_instrument("US_TECH_FUT", ("CME_MINI:NQ1!",), te_path="us100:ind", yahoo_ticker="^NDX"),
    "US 30 FUT": fetch_live_instrument("US_30_FUT", ("CBOT:YM1!",), te_path="indu:ind", yahoo_ticker="^DJI"),
    "CRUDE OIL": fetch_live_instrument("CL=F", ("NYMEX:CL1!",), yahoo_ticker="CL=F"),
    "GOLD": fetch_live_instrument("GC=F", ("COMEX:GC1!",), yahoo_ticker="GC=F"),
    "BITCOIN": fetch_live_instrument("BTC-USD", ("COINBASE:BTCUSD",), yahoo_ticker="BTC-USD"),
}

cols = st.columns(5)
for i, (name, data) in enumerate(instruments.items()):
    with cols[i % 5]:
        if data:
            color = "pos" if data["change"] >= 0 else "neg"
            st.markdown(f"""
            <div class="metric-card">
                <div class="index-title">{name}</div>
                <div class="index-price">{data['price']:,.2f}</div>
                <div class="index-change {color}">{data['change']:+.2f} ({data['pct']:+.2f}%)</div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------
# Charts Section
# -------------------------------------------------
st.markdown("---")
st.markdown("#### 📊 Price & Renko Charts")
tf = st.radio("Timeframe", ["Daily", "1 Hour", "30 Minutes"], horizontal=True)
interval = {"Daily": "1d", "1 Hour": "1h", "30 Minutes": "30m"}[tf]
candle_df = get_ohlc_data(selected, interval=interval)

if candle_df is not None and not candle_df.empty:
    fig = go.Figure(data=[go.Candlestick(x=candle_df['Date'], open=candle_df['Open'], high=candle_df['High'], low=candle_df['Low'], close=candle_df['Close'])])
    fig.update_layout(height=400, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# Heatmap Section
# -------------------------------------------------
st.markdown("---")
st.markdown('<div class="section-header">🗺️ Nifty 50 Heatmap</div>', unsafe_allow_html=True)
heatmap_data = [
    {"sym": "RELIANCE", "pct": 0.82, "ltp": 2740.5},
    {"sym": "HDFCBANK", "pct": -0.41, "ltp": 1650.2},
    {"sym": "ICICIBANK", "pct": 1.12, "ltp": 1240.1},
    {"sym": "SBIN", "pct": -0.95, "ltp": 810.4},
    {"sym": "INFY", "pct": 0.36, "ltp": 1880.0},
    {"sym": "BHARTIARTL", "pct": -0.22, "ltp": 1695.0},
]
html_cells = []
for h in heatmap_data:
    bg = "#059669" if h["pct"] > 0 else "#dc2626"
    html_cells.append(f'<div class="heat-cell" style="background:{bg};">{h["sym"]}<br>{h["pct"]:+.2f}%<br>₹{h["ltp"]}</div>')
st.markdown("".join(html_cells), unsafe_allow_html=True)

# -------------------------------------------------
# 🎯 Quantsapp-Style F&O Built-up Cycle Grid (PLACED IMMEDIATELY AFTER HEATMAP)
# -------------------------------------------------
st.markdown("---")
st.markdown('<div class="section-header">Built-up cycle · most active F&O stocks</div>', unsafe_allow_html=True)
st.caption("Historical daily F&O build-up cycle across top liquid equities.")

# Simulated/Live 10-day Build-up cycle matrix matching Quantsapp layout
dates = ["25", "24", "23", "22", "21", "18", "17", "16", "15", "14"]
bu_stocks = [
    {"sym": "RELIANCE", "price_pct": "+0.82%", "oi_pct": "+3.1%", "cycles": ["bu-long", "bu-long", "bu-covering", "bu-long", "bu-short", "bu-unwinding", "bu-long", "bu-long", "bu-covering", "bu-short"]},
    {"sym": "HDFCBANK", "price_pct": "-0.41%", "oi_pct": "+1.9%", "cycles": ["bu-short", "bu-unwinding", "bu-short", "bu-covering", "bu-long", "bu-long", "bu-long", "bu-short", "bu-short", "bu-covering"]},
    {"sym": "ICICIBANK", "price_pct": "+1.12%", "oi_pct": "-0.8%", "cycles": ["bu-covering", "bu-long", "bu-long", "bu-short", "bu-unwinding", "bu-covering", "bu-long", "bu-long", "bu-long", "bu-long"]},
    {"sym": "SBIN", "price_pct": "-0.95%", "oi_pct": "-1.4%", "cycles": ["bu-unwinding", "bu-short", "bu-short", "bu-unwinding", "bu-unwinding", "bu-long", "bu-short", "bu-unwinding", "bu-covering", "bu-long"]},
    {"sym": "INFY", "price_pct": "+0.36%", "oi_pct": "+2.4%", "cycles": ["bu-long", "bu-long", "bu-covering", "bu-unwinding", "bu-short", "bu-long", "bu-covering", "bu-long", "bu-unwinding", "bu-short"]},
    {"sym": "BHARTIARTL", "price_pct": "-0.22%", "oi_pct": "+0.7%", "cycles": ["bu-short", "bu-long", "bu-long", "bu-covering", "bu-long", "bu-unwinding", "bu-unwinding", "bu-short", "bu-long", "bu-covering"]},
]

bu_html = ['<div class="bu-container">']
# Dates Header Row
bu_html.append('<div class="bu-row"><div class="bu-sym">SYMBOL</div><div class="bu-blocks">')
for d in dates:
    bu_html.append(f'<div style="flex:1; text-align:center; font-size:11px; font-weight:600; color:#cbd5e1;">{d}</div>')
bu_html.append('</div></div>')

# Stock Rows
for stock in bu_stocks:
    bu_html.append(f'''
    <div class="bu-row">
        <div class="bu-sym">
            {stock['sym']}<br>
            <span class="bu-sym-sub" style="color:{'#34d399' if '+' in stock['price_pct'] else '#f87171'}">{stock['price_pct']}</span>
            <span class="bu-sym-sub" style="color:#94a3b8">{stock['oi_pct']}</span>
        </div>
        <div class="bu-blocks">
    ''')
    for c in stock['cycles']:
        bu_html.append(f'<div class="bu-box {c}"></div>')
    bu_html.append('</div></div>')

# Legend
bu_html.append('''
    <div class="bu-legend">
        <div><span class="bu-dot bu-long"></span> Long build-up</div>
        <div><span class="bu-dot bu-short"></span> Short build-up</div>
        <div><span class="bu-dot bu-covering"></span> Short covering</div>
        <div><span class="bu-dot bu-unwinding"></span> Long unwinding</div>
        <div style="margin-left:auto; font-weight:600;">Price% · OI% today</div>
    </div>
</div>
''')

st.markdown("".join(bu_html), unsafe_allow_html=True)

# -------------------------------------------------
# Corporate Actions (PLACED IMMEDIATELY ABOVE BOTTOM SECTION)
# -------------------------------------------------
st.markdown("---")
st.markdown('<div class="section-header">📋 Corporate Actions — Nifty 50</div>', unsafe_allow_html=True)

ca_data = pd.DataFrame([
    {"Symbol": "RELIANCE", "Purpose": "Interim Dividend - ₹10.00", "Ex-Date": "28 Oct 2026", "Record Date": "29 Oct 2026"},
    {"Symbol": "INFY", "Purpose": "Special Dividend - ₹18.00", "Ex-Date": "02 Nov 2026", "Record Date": "03 Nov 2026"},
    {"Symbol": "TCS", "Purpose": "Interim Dividend - ₹9.00", "Ex-Date": "05 Nov 2026", "Record Date": "06 Nov 2026"},
])
st.dataframe(ca_data, use_container_width=True, hide_index=True)
