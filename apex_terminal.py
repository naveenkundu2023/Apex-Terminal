APEX MARKET TERMINAL — UPDATED BUILD 2026-10-20Complete Python Code with all requested features & fixes.import streamlit as st
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
import xml.etree.ElementTree as ET-------------------------------------------------Page Config-------------------------------------------------st.set_page_config(
page_title="Apex Market Terminal",
page_icon="📈",
layout="wide",
initial_sidebar_state="expanded"
)-------------------------------------------------Hide Manage app button & Default Streamlit Styles-------------------------------------------------st.markdown("""""", unsafe_allow_html=True)-------------------------------------------------Session State Initialisation-------------------------------------------------if "watchlist" not in st.session_state:
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
st.session_state.last_pcr_time = None-------------------------------------------------Theme CSS & UI Customizations-------------------------------------------------def apply_theme(theme: str):
if theme == "dark":
st.markdown("""

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
div[data-testid="stMetric"] label { color: #818cf8 !important; font-weight: 600 !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-weight: 700 !important; }        /* High visibility for select labels & radios */
        label, div[data-testid="stMarkdownContainer"] p, .stRadio label {
            color: #818cf8 !important;
            font-weight: 600 !important;
        }
        
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
        /* Buildup matrix styles */
        .buildup-table {
            width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;
        }
        .buildup-table th, .buildup-table td {
            padding: 6px; text-align: center; border: 1px solid #334155;
        }
        .buildup-table th { background-color: #1e1b4b; color: #818cf8; }
        .dot-long-buildup { color: #34d399; font-size: 16px; }
        .dot-short-buildup { color: #f87171; font-size: 16px; }
        .dot-short-covering { color: #60a5fa; font-size: 16px; }
        .dot-long-unwinding { color: #fbbf24; font-size: 16px; }
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
        .metric-card {
            background: linear-gradient(145deg, #ffffff, #f1f5f9);
            border: 1px solid #c7d2fe;
            border-radius: 10px;
            padding: 8px 6px !important;
            text-align: center;
            box-shadow: 0 3px 12px rgba(99,102,241,0.12);
            min-height: 78px !important;
        }
        .index-title { 
            font-size: 10px !important; font-weight: 600; color: #64748b; 
            letter-spacing: 0.3px; text-transform: uppercase; 
            margin-bottom: 3px !important; line-height: 1.1;
        }
        .index-price { 
            font-size: 15px !important; font-weight: 700; color: #0f172a; 
            line-height: 1.15 !important; margin: 2px 0 !important;
        }
        .index-change { font-size: 11px !important; font-weight: 600; margin-top: 1px !important; }
        .pos { color: #059669 !important; }
        .neg { color: #dc2626 !important; }
        .section-header {
            font-size: 18px; font-weight: 700;
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        div[data-testid="stMetric"] {
            background: white; border: 1px solid #e2e8f0;
            border-radius: 12px; padding: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        div[data-testid="stMetric"] label { color: #4f46e5 !important; font-weight: 600 !important; }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 700 !important; }
        
        label, div[data-testid="stMarkdownContainer"] p, .stRadio label {
            color: #4f46e5 !important;
            font-weight: 600 !important;
        }
        
        .stButton > button {
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
            color: white; border: none; border-radius: 10px; font-weight: 600;
        }
        h1 {
            background: linear-gradient(90deg, #4f46e5, #7c3aed, #a855f7);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
        }
        .watchlist-chip {
            display: inline-block; background: #e0e7ff; color: #3730a3;
            padding: 4px 12px; border-radius: 20px; margin: 3px;
            font-size: 13px; font-weight: 500;
        }
        .analysis-box {
            background: white; border: 1px solid #c7d2fe;
            border-radius: 12px; padding: 16px; margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(99,102,241,0.08);
        }
        .heat-cell {
            display: inline-block; width: 19%; margin: 0.5%; padding: 8px 4px;
            border-radius: 6px; text-align: center; font-size: 11px; font-weight: 600;
            color: #fff; min-height: 52px;
        }
        .buildup-table {
            width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;
        }
        .buildup-table th, .buildup-table td {
            padding: 6px; text-align: center; border: 1px solid #cbd5e1;
        }
        .buildup-table th { background-color: #e0e7ff; color: #4f46e5; }
        .dot-long-buildup { color: #059669; font-size: 16px; }
        .dot-short-buildup { color: #dc2626; font-size: 16px; }
        .dot-short-covering { color: #2563eb; font-size: 16px; }
        .dot-long-unwinding { color: #d97706; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)
apply_theme(st.session_state.theme)-------------------------------------------------Helpers & Scrapers-------------------------------------------------def nse_session_headers():
return {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
"Accept": "application/json, text/plain, /",
"Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
"Referer": "https://www.nseindia.com/option-chain",
"Origin": "https://www.nseindia.com",
"Connection": "keep-alive",
}def is_nse_market_hours():
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
if now.weekday() >= 5:
return False
t = now.time()
return dtime(9, 15) <= t <= dtime(15, 30)@st.cache_data(ttl=15)
def fetch_yahoo_quote(ticker: str):
if not ticker or ticker in ("GIFT_NIFTY", "US_TECH_FUT", "US_30_FUT"):
return None
try:
t = yf.Ticker(ticker)
hist = None
for period, interval in [("5d", "5m"), ("5d", "1m"), ("5d", None), ("1d", None)]:
try:
if interval:
hist = t.history(period=period, interval=interval, prepost=True)
else:
hist = t.history(period=period)
if hist is not None and not hist.empty:
break
except Exception:
continue
if hist is not None and not hist.empty:
hist = hist.dropna(subset=["Close"])
if not hist.empty:
price = float(hist["Close"].iloc[-1])
try:
daily = t.history(period="5d", interval="1d")
if daily is not None and not daily.empty and len(daily) >= 2:
prev = float(daily["Close"].iloc[-2])
elif len(hist) > 1:
prev = float(hist["Close"].iloc[-2])
else:
prev = price
except Exception:
prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
change = price - prev
pct = (change / prev * 100) if prev else 0
return {
"price": round(price, 2),
"change": round(change, 2),
"pct": round(pct, 2),
"source": f"Yahoo Finance ({ticker})"
}
info = t.fast_info
price = getattr(info, "last_price", None) or getattr(info, "regular_market_price", None)
prev = getattr(info, "previous_close", None) or price
if price is not None:
change = float(price) - float(prev)
pct = (change / float(prev) * 100) if prev else 0
return {
"price": round(float(price), 2),
"change": round(change, 2),
"pct": round(pct, 2),
"source": f"Yahoo Finance ({ticker})"
}
except Exception:
pass
return None@st.cache_data(ttl=15)
def fetch_index_quote(ticker: str):
return fetch_yahoo_quote(ticker)@st.cache_data(ttl=20, show_spinner=False)
def fetch_tradingview_quote(tv_symbol: str):
try:
exchange = tv_symbol.split(":", 1)[0].upper()
region_map = {
"NSEIX": "india", "NSE": "india", "MCX": "india", "BSE": "india",
"COMEX": "america", "NYMEX": "america", "ICEEUR": "america", "DJ": "america",
"NASDAQ": "america", "TVC": "america", "NYSE": "america", "CME": "america",
"CBOT": "america", "CME_MINI": "america",
"COINBASE": "crypto", "BINANCE": "crypto",
"FX_IDC": "forex", "OANDA": "forex",
"HSI": "hongkong", "TSE": "japan", "SSE": "china", "KRX": "korea", "ASX": "australia"
}
region = region_map.get(exchange, "america")
url = f"https://scanner.tradingview.com/{region}/scan"
payload = {"symbols": {"tickers": [tv_symbol], "query": {"types": []}},
"columns": ["close", "change", "change_abs"]}
headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json",
"Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/"}
r = requests.post(url, json=payload, headers=headers, timeout=6)
if r.status_code != 200:
return None
rows = r.json().get("data", [])
if not rows or not rows[0].get("d"):
return None
vals = rows[0]["d"]
price = vals[0]
pct = vals[1]
change = vals[2]
if price is None or float(price) <= 0:
return None
if change is None and pct is not None:
change = float(price) * float(pct) / 100
if pct is None and change is not None:
pct = (float(change) / (float(price) - float(change)) * 100) if float(price) != float(change) else 0
return {"price": round(float(price), 2), "change": round(float(change or 0), 2),
"pct": round(float(pct or 0), 2), "source": f"TradingView ({tv_symbol})"}
except Exception:
return None@st.cache_data(ttl=30, show_spinner=False)
def fetch_tradingeconomics_quote(symbol: str):
"""Scrapes TradingEconomics fallback for US tech 100, US 30, etc."""
try:
url = f"https://tradingeconomics.com/{symbol}"
headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36"
}
r = requests.get(url, headers=headers, timeout=6)
if r.status_code != 200:
return None
html = r.text
m_price = re.search(r'id=["']market-last["'][^>]>(.?)<', html)
m_chg = re.search(r'id=["']market-change["'][^>]>(.?)<', html)
m_pct = re.search(r'id=["']market-pchange["'][^>]>(.?)<', html)    if m_price:
        price = float(re.sub(r"[^0-9.]", "", m_price.group(1)))
        change = float(re.sub(r"[^0-9.+-]", "", m_chg.group(1))) if m_chg else 0.0
        pct = float(re.sub(r"[^0-9.+-]", "", m_pct.group(1))) if m_pct else 0.0
        return {
            "price": round(price, 2),
            "change": round(change, 2),
            "pct": round(pct, 2),
            "source": f"TradingEconomics ({symbol})"
        }
except Exception:
    pass
return None
@st.cache_data(ttl=30, show_spinner=False)
def fetch_investing_quote(slug: str):
try:
url = "https://www.investing.com/" + slug
headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
"Accept-Language": "en-US,en;q=0.9",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8",
}
r = requests.get(url, headers=headers, timeout=6)
if r.status_code != 200:
return None
html = r.text    def extract(pattern):
        m = re.search(pattern, html, flags=re.I | re.S)
        return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else None

    price_text = extract(r'data-test=["\']instrument-price-last["\'][^>]*>(.*?)</')
    change_text = extract(r'data-test=["\']instrument-price-change["\'][^>]*>(.*?)</')
    pct_text = extract(r'data-test=["\']instrument-price-change-percent["\'][^>]*>(.*?)</')
    if not price_text:
        m = re.search(r'["\']last["\']\s*:\s*["\']?([0-9,]+\.?[0-9]*)', html, flags=re.I)
        price_text = m.group(1) if m else None
    if not price_text:
        return None

    def number(value):
        if not value:
            return None
        cleaned = re.sub(r"[^0-9.+-]", "", value.replace(",", ""))
        try:
            return float(cleaned) if cleaned not in ("", "+", "-") else None
        except ValueError:
            return None

    price = number(price_text)
    change = number(change_text) or 0.0
    pct = number(pct_text) or 0.0
    if price is None or price <= 0:
        return None
    return {
        "price": round(price, 2),
        "change": round(change, 2),
        "pct": round(pct, 2),
        "source": f"Investing.com ({slug})"
    }
except Exception:
    return None
INVESTING_SLUGS = {
"GIFT_NIFTY": "indices/sgx-nifty",
"US_TECH_FUT": "indices/nq-100-futures",
"US_30_FUT": "indices/us-30-futures",
"CL=F": "commodities/crude-oil",
"BZ=F": "commodities/brent-oil",
"NG=F": "commodities/natural-gas",
"GC=F": "commodities/gold",
"SI=F": "commodities/silver",
"HG=F": "commodities/copper",
"INR=X": "currencies/usd-inr",
"BTC-USD": "crypto/bitcoin",
"DX-Y.NYB": "indices/usdollar-index",
"^TNX": "rates-bonds/u.s.-10-year-bond-yield",
"^TYX": "rates-bonds/u.s.-30-year-bond-yield",
"^HSI": "indices/hang-sen-40",
"^N225": "indices/japan-ni225",
"000001.SS": "indices/shanghai-composite",
"^KS11": "indices/kospi",
"^AXJO": "indices/asx-200",
"^NDX": "indices/nq-100",
"^DJI": "indices/us-30",
"^IXIC": "indices/nasdaq-composite",
}YAHOO_FALLBACK = {
"GIFT_NIFTY": None,
"US_TECH_FUT": "^NDX",
"US_30_FUT": "^DJI",
"CL=F": "CL=F",
"BZ=F": "BZ=F",
"NG=F": "NG=F",
"GC=F": "GC=F",
"SI=F": "SI=F",
"HG=F": "HG=F",
"INR=X": "INR=X",
"BTC-USD": "BTC-USD",
"DX-Y.NYB": "DX-Y.NYB",
"^TNX": "^TNX",
"^TYX": "^TYX",
"^HSI": "^HSI",
"^N225": "^N225",
"000001.SS": "000001.SS",
"^KS11": "^KS11",
"^AXJO": "^AXJO",
"^NDX": "^NDX",
"^DJI": "^DJI",
"^IXIC": "^IXIC",
}@st.cache_data(ttl=20, show_spinner=False)
def fetch_live_instrument(key: str, tv_symbols=(), investing_key: str = None, yahoo_ticker: str = None, te_symbol: str = None):
if isinstance(tv_symbols, str):
tv_symbols = (tv_symbols,)
# 1) TradingView
for symbol in tv_symbols:
quote = fetch_tradingview_quote(symbol)
if quote:
return quote
# 2) TradingEconomics Fallback (if applicable)
if te_symbol:
te_q = fetch_tradingeconomics_quote(te_symbol)
if te_q:
return te_q
# 3) Investing.com
slug_key = investing_key or key
slug = INVESTING_SLUGS.get(slug_key)
if slug:
inv = fetch_investing_quote(slug)
if inv:
return inv
# 4) Yahoo Finance
y_ticker = yahoo_ticker or YAHOO_FALLBACK.get(key) or YAHOO_FALLBACK.get(slug_key)
if y_ticker:
yq = fetch_yahoo_quote(y_ticker)
if yq:
return yq
return None@st.cache_data(ttl=15, show_spinner=False)
def fetch_gift_nifty_50():
headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
"Referer": "https://www.moneycontrol.com/",
}
# 1) Moneycontrol Fallback direct link
try:
r = requests.get(
"https://www.moneycontrol.com/live-index/gift-nifty?symbol=in;gsx",
headers=headers,
timeout=8,
)
if r.status_code == 200:
plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text))
chg_m = re.search(
r"([+-]?\d{1,3}(?:,\d{3})(?:.\d+)?)\s$\s*([+-]?\d+\.?\d*)\s*\%\s*$",
plain,
)
prev_m = re.search(r"Previous\sClose\s([\d,]+.?\d*)", plain, re.I)
nums = re.findall(r"(2[0-9],\d{3}(?:.\d{1,2})?)", plain)
if nums:
price = float(nums[0].replace(",", ""))
change = pct = 0.0
if chg_m:
change = float(chg_m.group(1).replace(",", ""))
pct = float(chg_m.group(2))
elif prev_m:
prev = float(prev_m.group(1).replace(",", ""))
change = price - prev
pct = (change / prev * 100) if prev else 0
if 15000 < price < 40000:
return {
"price": round(price, 2),
"change": round(change, 2),
"pct": round(pct, 2),
"source": "Moneycontrol GIFT Nifty",
}
except Exception:
pass# 2) Upstox
try:
    r = requests.get("https://upstox.com/gift-nifty/", headers=headers, timeout=8)
    if r.status_code == 200:
        plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text))
        m = re.search(
            r"(2[0-9],\d{3}\.\d{2})\s+([+-]?\d{1,3}(?:,\d{3})*\.?\d*)\s*\(\s*([+-]?\d+\.?\d*)\s*\%\s*\)",
            plain,
        )
        if m:
            price = float(m.group(1).replace(",", ""))
            change = float(m.group(2).replace(",", ""))
            pct = float(m.group(3))
            if 15000 < price < 40000:
                return {
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "pct": round(pct, 2),
                    "source": "Upstox GIFT Nifty",
                }
except Exception:
    pass

# 3) TradingView
for symbol in ("NSEIX:NIFTY1!", "NSEIX:NIFTY2!", "NSEIX:GIFTNIFTY1!", "NSEIX:GIFTNIFTY"):
    quote = fetch_tradingview_quote(symbol)
    if quote and 15000 < quote["price"] < 40000:
        quote["source"] = f"TradingView ({symbol})"
        return quote

return None
@st.cache_data(ttl=45)
def fetch_stock_data(symbol: str):
try:
t = yf.Ticker(f"{symbol}.NS")
info = t.fast_info
hist = t.history(period="1mo")
if hist.empty:
return None
ltp = getattr(info, "last_price", None) or getattr(info, "regular_market_price", None) or float(hist["Close"].iloc[-1])
prev_close = getattr(info, "previous_close", None) or (float(hist["Close"].iloc[-2]) if len(hist) > 1 else ltp)
day_high = getattr(info, "day_high", None) or float(hist["High"].iloc[-1])
day_low = getattr(info, "day_low", None) or float(hist["Low"].iloc[-1])
volume = getattr(info, "last_volume", None) or getattr(info, "regular_market_volume", None) or int(hist["Volume"].iloc[-1])
avg_vol = int(hist["Volume"].tail(20).mean()) if len(hist) >= 5 else volume
return {
"ltp": round(float(ltp), 2),
"prev_close": round(float(prev_close), 2),
"prev_high": round(float(day_high), 2),
"prev_low": round(float(day_low), 2),
"volume": int(volume),
"avg_volume": avg_vol
}
except Exception:
return None@st.cache_data(ttl=60)
def get_ohlc_data(symbol: str, interval: str = "1d", period: str = "3mo"):
try:
t = yf.Ticker(f"{symbol}.NS")
if interval in ["30m", "1h"]:
period = "1mo" if interval == "1h" else "5d"
df = t.history(period=period, interval=interval)
if df.empty:
return None
df = df.reset_index()
if "Datetime" in df.columns:
df = df.rename(columns={"Datetime": "Date"})
return df
except Exception:
return None@st.cache_data(ttl=90)
def get_daily_atr(symbol: str, atr_period: int = 14, lookback_days: int = 30):
try:
t = yf.Ticker(f"{symbol}.NS")
df = t.history(period="2mo", interval="1d")
if df.empty or len(df) < atr_period + 5:
return None
high, low, close = df["High"], df["Low"], df["Close"]
tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
atr = tr.rolling(window=atr_period).mean()
recent = atr.dropna().tail(lookback_days)
return float(recent.mean()) if not recent.empty else None
except Exception:
return Nonedef calculate_ema(series: pd.Series, span: int) -> pd.Series:
return series.ewm(span=span, adjust=False).mean()def generate_renko(df: pd.DataFrame, box_size: float) -> pd.DataFrame:
if df is None or df.empty or box_size <= 0:
return pd.DataFrame()
prices = df["Close"].values
dates = df["Date"].values
bricks = []
current_brick = round(prices[0] / box_size) * box_size
for i in range(1, len(prices)):
price, date = prices[i], dates[i]
while price >= current_brick + box_size:
bricks.append({"Date": date, "Open": current_brick, "High": current_brick + box_size,
"Low": current_brick, "Close": current_brick + box_size})
current_brick += box_size
while price <= current_brick - box_size:
bricks.append({"Date": date, "Open": current_brick, "High": current_brick,
"Low": current_brick - box_size, "Close": current_brick - box_size})
current_brick -= box_size
if not bricks:
return pd.DataFrame()
renko_df = pd.DataFrame(bricks)
renko_df["Brick"] = range(1, len(renko_df) + 1)
return renko_df@st.cache_data(ttl=3600)
def get_stock_universe():
headers = nse_session_headers()
urls = [
"https://archives.nseindia.com/content/indices/ind_nifty50list.csv",
"https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv",
]
for url in urls:
try:
session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=8)
r = session.get(url, headers=headers, timeout=10)
if r.status_code == 200 and "Symbol" in r.text:
df = pd.read_csv(StringIO(r.text))
symbols = df["Symbol"].str.strip().tolist()
if len(symbols) >= 45:
return sorted(symbols)
except Exception:
continue
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
]NIFTY50_WEIGHT = {
"HDFCBANK": 12.8, "ICICIBANK": 8.4, "RELIANCE": 8.0, "BHARTIARTL": 5.0, "INFY": 4.8,
"SBIN": 4.0, "ITC": 3.6, "TCS": 3.5, "AXISBANK": 3.2, "KOTAKBANK": 2.8, "LT": 2.7,
"BAJFINANCE": 2.5, "HINDUNILVR": 2.3, "M&M": 2.2, "TATAMOTORS": 1.9, "SUNPHARMA": 1.8,
"MARUTI": 1.8, "HCLTECH": 1.7, "NTPC": 1.6, "TITAN": 1.5, "ULTRACEMCO": 1.4,
"POWERGRID": 1.4, "TATASTEEL": 1.3, "ONGC": 1.2, "JSWSTEEL": 1.2, "BEL": 1.2,
"ASIANPAINT": 1.1, "ADANIPORTS": 1.1, "BAJAJFINSV": 1.0, "COALINDIA": 1.0,
"INDUSINDBK": 0.9, "GRASIM": 0.9, "TATACONSUM": 0.8, "NESTLEIND": 0.8, "WIPRO": 0.8,
"TECHM": 0.7, "HINDALCO": 0.7, "DRREDDY": 0.7, "CIPLA": 0.7, "EICHERMOT": 0.6,
"APOLLOHOSP": 0.6, "DIVISLAB": 0.6, "SBILIFE": 0.6, "HDFCLIFE": 0.6, "BRITANNIA": 0.5,
"HEROMOTOCO": 0.5, "BAJAJ-AUTO": 0.5, "ADANIENT": 0.5, "UPL": 0.3
}@st.cache_data(ttl=60)
def get_index_analytics(ticker: str):
try:
t = yf.Ticker(ticker)
hist = t.history(period="10d")
if hist.empty or len(hist) < 5:
return None
last5 = hist.tail(5)
current = float(hist["Close"].iloc[-1])
prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current
day_high = float(hist["High"].iloc[-1])
day_low = float(hist["Low"].iloc[-1])
avg_5d = float(last5["Close"].mean())
high_5d = float(last5["High"].max())
low_5d = float(last5["Low"].min())
last5 = last5.copy()
last5["TP"] = (last5["High"] + last5["Low"] + last5["Close"]) / 3
vwap_5d = float((last5["TP"] * last5["Volume"]).sum() / last5["Volume"].sum()) if last5["Volume"].sum() > 0 else avg_5d
change = current - prev_close
pct = (change / prev_close) * 100 if prev_close else 0
return {
"current": round(current, 2),
"prev_close": round(prev_close, 2),
"day_high": round(day_high, 2),
"day_low": round(day_low, 2),
"avg_5d": round(avg_5d, 2),
"high_5d": round(high_5d, 2),
"low_5d": round(low_5d, 2),
"vwap_5d": round(vwap_5d, 2),
"change": round(change, 2),
"pct": round(pct, 2),
"above_vwap": current > vwap_5d
}
except Exception:
return None@st.cache_data(ttl=45, show_spinner=False)
def get_option_sentiment(symbol: str = "NIFTY"):
sym = symbol.upper().replace(" ", "")
nse_symbol = "NIFTY" if sym in ["NIFTY", "NIFTY50"] else "BANKNIFTY"
out = {"pcr": None, "max_pain": None, "atm_iv": None, "source": None}headers = nse_session_headers()
url = f"https://www.nseindia.com/api/option-chain-indices?symbol={nse_symbol}"
session = requests.Session()
try:
    session.get("https://www.nseindia.com", headers=headers, timeout=6)
    session.get("https://www.nseindia.com/option-chain", headers=headers, timeout=6)
    response = session.get(url, headers=headers, timeout=8)
    if response.status_code == 200:
        data = response.json()
        records = data.get("records", {})
        ce_oi = pe_oi = 0
        for item in records.get("data", []):
            ce = item.get("CE") or {}
            pe = item.get("PE") or {}
            ce_oi += int(ce.get("openInterest") or 0)
            pe_oi += int(pe.get("openInterest") or 0)
        if ce_oi > 0 and pe_oi > 0:
            pcr = pe_oi / ce_oi
            if 0.05 < pcr < 10:
                out["pcr"] = round(pcr, 3)
                out["source"] = "NSE"
                return out
except Exception:
    pass
finally:
    try:
        session.close()
    except Exception:
        pass
return out
@st.cache_data(ttl=60)
def get_market_breadth(universe: list):
try:
tickers = [f"{s}.NS" for s in universe]
data = yf.download(tickers, period="2d", group_by="ticker", progress=False, threads=True)
bullish = 0
bearish = 0
for sym in universe:
try:
hist = data if len(universe) == 1 else (data[f"{sym}.NS"] if f"{sym}.NS" in data.columns.get_level_values(0) else None)
if hist is None or hist.empty or len(hist) < 2:
continue
last = float(hist["Close"].iloc[-1])
prev = float(hist["Close"].iloc[-2])
if last > prev:
bullish += 1
elif last < prev:
bearish += 1
except Exception:
continue
return bullish, bearish
except Exception:
return 0, 0@st.cache_data(ttl=60)
def get_stock_summary_analytics(symbol: str):
try:
t = yf.Ticker(f"{symbol}.NS")
hist = t.history(period="10d")
if hist.empty or len(hist) < 5:
return None
last5 = hist.tail(5)
current = float(hist["Close"].iloc[-1])
prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current
day_high = float(hist["High"].iloc[-1])
day_low = float(hist["Low"].iloc[-1])
avg_5d = float(last5["Close"].mean())
high_5d = float(last5["High"].max())
low_5d = float(last5["Low"].min())
last5 = last5.copy()
last5["TP"] = (last5["High"] + last5["Low"] + last5["Close"]) / 3
vwap_5d = float((last5["TP"] * last5["Volume"]).sum() / last5["Volume"].sum()) if last5["Volume"].sum() > 0 else avg_5d
change = current - prev_close
pct = (change / prev_close) * 100 if prev_close else 0
bias = "BULLISH" if current > vwap_5d and current > avg_5d else "BEARISH" if current < vwap_5d and current < avg_5d else "NEUTRAL"
return {
"current": round(current, 2),
"prev_close": round(prev_close, 2),
"day_high": round(day_high, 2),
"day_low": round(day_low, 2),
"avg_5d": round(avg_5d, 2),
"high_5d": round(high_5d, 2),
"low_5d": round(low_5d, 2),
"vwap_5d": round(vwap_5d, 2),
"change": round(change, 2),
"pct": round(pct, 2),
"above_vwap": current > vwap_5d,
"bias": bias
}
except Exception:
return None---------- Nifty 50 Heatmap ----------@st.cache_data(ttl=90, show_spinner=False)
def get_nifty50_heatmap(universe: list):
try:
tickers = [f"{s}.NS" for s in universe]
data = yf.download(tickers, period="5d", group_by="ticker", progress=False, threads=True)
rows = []
for sym in universe:
try:
hist = data if len(universe) == 1 else (data[f"{sym}.NS"] if f"{sym}.NS" in data.columns.get_level_values(0) else None)
if hist is None or hist.empty:
continue
close = hist["Close"].dropna()
if len(close) < 2:
continue
last, prev = float(close.iloc[-1]), float(close.iloc[-2])
pct = (last - prev) / prev * 100 if prev else 0
rows.append({"Symbol": sym, "LTP": round(last, 2), "% Chg": round(pct, 2)})
except Exception:
continue
return pd.DataFrame(rows)
except Exception:
return pd.DataFrame()---------- FnO Top 15 Built Up Section ----------@st.cache_data(ttl=120, show_spinner=False)
def get_fno_buildup_data():
"""Fetches past 5 sessions price & volume changes for top FnO stocks to build Quantsapp style dot matrix."""
fno_top_15 = [
"RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
"SBIN", "BHARTIARTL", "AXISBANK", "KOTAKBANK", "LT",
"TATAMOTORS", "M&M", "BAJFINANCE", "MARUTI", "TATASTEEL"
]
tickers = [f"{s}.NS" for s in fno_top_15]
try:
data = yf.download(tickers, period="10d", group_by="ticker", progress=False, threads=True)
date_cols = []
# get last 5 dates
sample_sym = tickers[0]
if sample_sym in data.columns.get_level_values(0):
df_sample = data[sample_sym].dropna(subset=["Close"])
date_cols = [d.strftime("%d %b") for d in df_sample.tail(5).index]    results = []
    for sym in fno_top_15:
        t_data = data[f"{sym}.NS"].dropna(subset=["Close"]).tail(6)
        if len(t_data) < 5:
            continue
        buildups = []
        closes = t_data["Close"].values
        volumes = t_data["Volume"].values
        
        # calculate daily buildup types
        for i in range(1, len(closes)):
            price_chg = closes[i] - closes[i-1]
            vol_chg = volumes[i] - volumes[i-1]
            
            if price_chg > 0 and vol_chg > 0:
                buildup = "LB" # Long Buildup
            elif price_chg < 0 and vol_chg > 0:
                buildup = "SB" # Short Buildup
            elif price_chg > 0 and vol_chg < 0:
                buildup = "SC" # Short Covering
            else:
                buildup = "LU" # Long Unwinding
            buildups.append(buildup)
        
        results.append({"Symbol": sym, "Buildups": buildups})
    return results, date_cols
except Exception:
    return [], []
---------- Corporate Actions ----------@st.cache_data(ttl=300, show_spinner=False)
def get_corporate_actions(universe: list):
headers = nse_session_headers()
session = requests.Session()
try:
session.get("https://www.nseindia.com", headers=headers, timeout=6)
url = "https://www.nseindia.com/api/corporates-corporateActions?index=equities"
r = session.get(url, headers=headers, timeout=10)
if r.status_code != 200:
return pd.DataFrame()
data = r.json()
rows = data if isinstance(data, list) else (data.get("data") or [])
uni_set = set(s.upper() for s in universe)
out = []
for item in rows:
sym = (item.get("symbol") or "").strip().upper()
if not sym or (uni_set and sym not in uni_set):
continue
out.append({
"Symbol": sym,
"Purpose": (item.get("purpose") or "—")[:80],
"Ex-Date": item.get("exDate") or "—",
"Record Date": item.get("recordDate") or "—",
})
if not out:
return pd.DataFrame()
return pd.DataFrame(out).drop_duplicates().head(20)
except Exception:
return pd.DataFrame()
finally:
session.close()-------------------------------------------------Sidebar-------------------------------------------------with st.sidebar:
st.markdown("### ⚙️ Controls")
theme_choice = st.radio("Theme", ["🌙 Dark", "☀️ Light"], index=0 if st.session_state.theme == "dark" else 1, horizontal=True)
new_theme = "dark" if "Dark" in theme_choice else "light"
if new_theme != st.session_state.theme:
st.session_state.theme = new_theme
st.rerun()
st.markdown("---")
st.markdown("### ⭐ Watchlist")
if "selected" in st.session_state:
c1, c2 = st.columns(2)
with c1:
if st.button("➕ Add", use_container_width=True):
if st.session_state.selected not in st.session_state.watchlist:
st.session_state.watchlist.append(st.session_state.selected)
st.success(f"Added {st.session_state.selected}")
with c2:
if st.button("➖ Remove", use_container_width=True):
if st.session_state.selected in st.session_state.watchlist:
st.session_state.watchlist.remove(st.session_state.selected)
st.info(f"Removed {st.session_state.selected}")
if st.session_state.watchlist:
chips = " ".join([f'{s}' for s in st.session_state.watchlist])
st.markdown(chips, unsafe_allow_html=True)-------------------------------------------------Header-------------------------------------------------ist = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(ist).strftime("%d %b %Y • %H:%M:%S IST")
st.markdown("# 📈 Apex Market Terminal")
st.caption(f"Live Indian Equities & Indices • {current_time}")========== MAIN CONTROLS ==========universe = get_stock_universe()
dropdown_universe = sorted(universe, key=lambda sym: (-NIFTY50_WEIGHT.get(sym, 0.0), sym))
col1, col2, col3 = st.columns([2.2, 1.2, 1])
with col1:
selected = st.selectbox("🔍 Select Stock (NSE)", options=dropdown_universe, index=0, key="selected")
with col2:
auto_refresh = st.checkbox("🔄 Auto-refresh every 1 min", value=False)
with col3:
st.markdown("", unsafe_allow_html=True)
if st.button("Refresh Now", use_container_width=True):
st.cache_data.clear()
st.rerun()========== STOCK SUMMARY BOX ==========st.markdown("---")
summary = get_stock_summary_analytics(selected)if summary:
bias_color = "#34d399" if summary["bias"] == "BULLISH" else "#f87171" if summary["bias"] == "BEARISH" else "#fbbf24"
st.markdown(f"""

📌 {selected} • Instant Snapshot

LTP: ₹{summary['current']:,.2f} ({summary['change']:+.2f} | {summary['pct']:+.2f}%)
Day H/L: ₹{summary['day_high']:,.2f} / ₹{summary['day_low']:,.2f}
5D Avg: ₹{summary['avg_5d']:,.2f}
5D High/Low: ₹{summary['high_5d']:,.2f} / ₹{summary['low_5d']:,.2f}
5D VWAP: ₹{summary['vwap_5d']:,.2f} {'✅ Above' if summary['above_vwap'] else '❌ Below'}
Bias: {summary['bias']}


""", unsafe_allow_html=True)st.markdown("---")-------------------------------------------------Market Indices + Global Instruments-------------------------------------------------st.markdown('Market Indices & Global Instruments', unsafe_allow_html=True)Extended fallbacks applied for GIFT Nifty, US Tech 100, US 30instruments = {
"INDIA VIX": ("cash", "^INDIAVIX", (), None, "^INDIAVIX", None),
"GIFT NIFTY 50 FUT": ("gift", "GIFT_NIFTY", ("NSEIX:NIFTY1!", "NSEIX:NIFTY2!"), "GIFT_NIFTY", None, None),
"NIFTY 50": ("cash", "^NSEI", (), None, "^NSEI", None),
"BANK NIFTY": ("cash", "^NSEBANK", (), None, "^NSEBANK", None),
"BSE SENSEX": ("cash", "^BSESN", (), None, "^BSESN", None),
"MIDCAP 150": ("cash", "NIFTYMIDCAP150.NS", (), None, "NIFTYMIDCAP150.NS", None),
"MIDCAP SELECT": ("cash", "NIFTY_MID_SELECT.NS", (), None, "NIFTY_MID_SELECT.NS", None),
"USD / INR": ("live", "INR=X", ("FX_IDC:USDINR", "OANDA:USDINR"), "INR=X", "INR=X", None),
"DXY (US DOLLAR INDEX)": ("live", "DX-Y.NYB", ("TVC:DXY",), "DX-Y.NYB", "DX-Y.NYB", None),
"US TECH 100 FUT": ("live", "US_TECH_FUT", ("CME_MINI:NQ1!", "NASDAQ:NDX"), "US_TECH_FUT", "^NDX", "us100:ind"),
"US 30 FUT": ("live", "US_30_FUT", ("CBOT:YM1!", "DJ:DJI"), "US_30_FUT", "^DJI", "indu:ind"),
"US 10Y BOND": ("live", "^TNX", ("TVC:US10Y",), "^TNX", "^TNX", None),
"CRUDE OIL WTI": ("live", "CL=F", ("TVC:USOIL",), "CL=F", "CL=F", None),
"GOLD": ("live", "GC=F", ("MCX:GOLD1!", "TVC:GOLD"), "GC=F", "GC=F", None),
"BITCOIN": ("live", "BTC-USD", ("COINBASE:BTCUSD",), "BTC-USD", "BTC-USD", None),
"HANG SENG": ("live", "^HSI", ("HSI:HSI",), "^HSI", "^HSI", None),
"NIKKEI 225": ("live", "^N225", ("TVC:NI225",), "^N225", "^N225", None),
"SHANGHAI COMPOSITE": ("live", "000001.SS", ("SSE:000001",), "000001.SS", "000001.SS", None),
}items = list(instruments.items())for i in range(0, len(items), 6):
row_items = items[i:i + 6]
cols = st.columns(6)
for j, (name, meta) in enumerate(row_items):
mode, key, tv_symbols, inv_key, yahoo_tk, te_symbol = meta
if mode == "gift":
data = fetch_gift_nifty_50()
elif mode == "cash":
data = fetch_index_quote(key)
else:
data = fetch_live_instrument(key, tv_symbols, inv_key, yahoo_tk, te_symbol)    with cols[j]:
        if data:
            sign = "+" if data["change"] >= 0 else ""
            color = "pos" if data["change"] >= 0 else "neg"
            triangle = "▲" if data["change"] >= 0 else "▼"
            price_str = f"₹{data['price']:,.2f}" if mode == "cash" and name != "INDIA VIX" else f"{data['price']:,.2f}"
            change_str = f"{triangle} {sign}{data['change']:.2f}"
            st.markdown(f"""
            <div class="metric-card">
                <div class="index-title">{name}</div>
                <div class="index-price">{price_str}</div>
                <div class="index-change {color}">{change_str} ({sign}{data['pct']:.2f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="index-title">{name}</div>
                <div class="index-price" style="font-size:12px; color:#94a3b8; padding-top:8px;">Unavailable</div>
            </div>
            """, unsafe_allow_html=True)
st.markdown("---")========== Global Macro Dashboard Section ==========st.markdown('🌍 Global Macro Dashboard & Scenario Expert Take', unsafe_allow_html=True)macro_take = """st.markdown("---")========== Market Breadth + PCR ==========st.markdown('📊 Market Breadth & Sentiment', unsafe_allow_html=True)bullish_cnt, bearish_cnt = get_market_breadth(universe)
nifty_sent = get_option_sentiment("NIFTY") or {}
bank_sent = get_option_sentiment("BANKNIFTY") or {}b1, b2, b3, b4 = st.columns(4)
b1.metric("🟢 Bullish Stocks (Nifty 50)", bullish_cnt)
b2.metric("🔴 Bearish Stocks (Nifty 50)", bearish_cnt)
b3.metric("Nifty PCR (OI)", f"{nifty_sent.get('pcr'):.3f}" if nifty_sent.get('pcr') else "Unavailable")
b4.metric("Bank Nifty PCR (OI)", f"{bank_sent.get('pcr'):.3f}" if bank_sent.get('pcr') else "Unavailable")st.markdown("---")-------------------------------------------------Heatmap Section-------------------------------------------------st.markdown('🔥 Nifty 50 Heatmap', unsafe_allow_html=True)
heatmap_df = get_nifty50_heatmap(universe[:25])
if not heatmap_df.empty:
cells_html = ""
for _, r in heatmap_df.iterrows():
bg = "rgba(52, 211, 153, 0.85)" if r["% Chg"] >= 0 else "rgba(248, 113, 113, 0.85)"
cells_html += f"""

{r['Symbol']}
{r['% Chg']:+.2f}%

"""
st.markdown(f'{cells_html}', unsafe_allow_html=True)st.markdown("---")-------------------------------------------------Built Up Section (FnO Top 15) - QUANTSAPP STYLE-------------------------------------------------st.markdown('⚡ FnO Top 15 Stocks - Daily Buildup Matrix', unsafe_allow_html=True)
buildup_data, dates = get_fno_buildup_data()if buildup_data and dates:
header_html = "Stock" + "".join([f"{d}" for d in dates]) + ""
rows_html = ""
for item in buildup_data:
sym = item["Symbol"]
dots_html = ""
for b in item["Buildups"]:
if b == "LB":
dots_html += '●'
elif b == "SB":
dots_html += '●'
elif b == "SC":
dots_html += '●'
else:
dots_html += '●'
rows_html += f"{sym}{dots_html}"table_html = f"""
<table class="buildup-table">
    {header_html}
    {rows_html}
</table>
<div style="margin-top:8px; font-size:12px; text-align:center;">
    Legend: 
    <span class="dot-long-buildup">●</span> Long Buildup &nbsp;&nbsp;
    <span class="dot-short-buildup">●</span> Short Buildup &nbsp;&nbsp;
    <span class="dot-short-covering">●</span> Short Covering &nbsp;&nbsp;
    <span class="dot-long-unwinding">●</span> Long Unwinding
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)
else:
st.info("FnO Buildup data currently loading...")st.markdown("---")-------------------------------------------------Corporate Actions Section-------------------------------------------------st.markdown('📢 Forthcoming Corporate Actions', unsafe_allow_html=True)
ca_df = get_corporate_actions(universe)
if not ca_df.empty:
st.dataframe(ca_df, use_container_width=True)
else:
st.info("No upcoming corporate actions found.")
