# APEX MARKET TERMINAL — UPDATED BUILD 2026-10-22 (v6 — Taiwan/FTSE/UK; Mid Select fix; stock PCR/MaxPain; Renko IST age - 22.10.26- 12.07 pm )
# Changes in this build (on top of v5):
# 1) Market Indices & Global Instruments: added TAIWAN TAIEX, FTSE 100 (UK).
# 2) MIDCAP SELECT: use Investing.com / Moneycontrol (latest) instead of unreliable Yahoo NIFTY_MID_SELECT.NS.
# 3) Stock Instant Snapshot: show selected stock PCR (OI) + Max Pain from NSE equity option chain.
# 4) Renko scanner Age Minutes: treat yfinance intraday timestamps as UTC→IST so age reflects Indian market time.
# Previous (v5) changes retained:
# 1) Market Indices cards: source prefix (U/M/I/T/Y/TE) + IST timestamp on every card.
# 2) Renko scanner order: 1 Hour groups first (BUY/BULLISH then SELL/BEARISH), then 30 Minutes groups.
# 3) Soft pastel up/down index cards; GIFT newest-timestamp selection; US TE fallback; China business-only news;
#    Corporate Actions + Top-5 news high-vis boxes; Built-up cycle section.

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
# Hide Manage app button
# -------------------------------------------------
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
# Theme CSS
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
            div[data-testid="stMetric"] label { color: #94a3b8 !important; }
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

            /* Readable select / radio / labels (match section-header clarity) */
            label, .stSelectbox label, .stRadio label, [data-testid="stWidgetLabel"] p,
            [data-testid="stSelectbox"] label, [data-testid="stRadio"] label {
                color: #f1f5f9 !important; font-weight: 600 !important;
            }
            .stSelectbox > div > div, .stRadio > div {
                color: #f8fafc !important;
            }
            div[data-baseweb="select"] > div, div[data-baseweb="select"] span {
                color: #f8fafc !important;
            }
            /* Soft pastel up/down cards: intentionally low-glare on mobile */
            .metric-card-up {
                background: #eaf6ed !important;
                border: 1px solid #d3e9d8 !important;
                box-shadow: none !important;
            }
            .metric-card-down {
                background: #fbeeee !important;
                border: 1px solid #f0d6d6 !important;
                box-shadow: none !important;
            }
            .metric-card-up .index-title,
            .metric-card-down .index-title { color: #52615a !important; }
            .metric-card-up .index-price,
            .metric-card-down .index-price { color: #26332b !important; }
            .metric-card-up .index-change { color: #386b49 !important; }
            .metric-card-down .index-change { color: #8a4545 !important; }
            .builtup-wrap {
                background: linear-gradient(145deg, rgba(30,41,59,0.95), rgba(15,23,42,0.98));
                border: 1px solid rgba(99,102,241,0.35);
                border-radius: 12px; padding: 14px; overflow-x: auto;
            }
            .builtup-table { border-collapse: collapse; width: 100%; font-size: 12px; }
            .builtup-table th { color: #94a3b8; font-weight: 600; padding: 4px 6px; text-align: center; }
            .builtup-table td { padding: 3px 4px; text-align: center; }
            .bu-cell {
                display: inline-block; width: 28px; height: 22px; border-radius: 4px;
                margin: 1px;
            }
            .bu-lb { background: #059669; }   /* Long build-up */
            .bu-sb { background: #dc2626; }   /* Short build-up */
            .bu-sc { background: #2563eb; }   /* Short covering */
            .bu-lu { background: #a3a30a; }   /* Long unwinding */
            .bu-na { background: #475569; }   /* N/A */
            .news-box, .ca-box {
                background: linear-gradient(145deg, rgba(30,41,59,0.95), rgba(15,23,42,0.98));
                border: 1px solid rgba(148,163,184,0.35);
                border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;
                color: #f1f5f9 !important;
            }
            .news-box a, .ca-box a { color: #a5b4fc !important; }
            .news-box, .news-box * , .ca-box, .ca-box * { color: #e2e8f0 !important; }

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
            div[data-testid="stMetric"] label { color: #64748b !important; }
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 700 !important; }
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

            label, .stSelectbox label, .stRadio label, [data-testid="stWidgetLabel"] p {
                color: #0f172a !important; font-weight: 600 !important;
            }
            /* Soft pastel up/down cards: intentionally low-glare on mobile */
            .metric-card-up {
                background: #eaf6ed !important;
                border: 1px solid #d3e9d8 !important;
                box-shadow: none !important;
            }
            .metric-card-down {
                background: #fbeeee !important;
                border: 1px solid #f0d6d6 !important;
                box-shadow: none !important;
            }
            .metric-card-up .index-title,
            .metric-card-down .index-title { color: #52615a !important; }
            .metric-card-up .index-price,
            .metric-card-down .index-price { color: #26332b !important; }
            .metric-card-up .index-change { color: #386b49 !important; }
            .metric-card-down .index-change { color: #8a4545 !important; }
            .builtup-wrap {
                background: #ffffff; border: 1px solid #c7d2fe;
                border-radius: 12px; padding: 14px; overflow-x: auto;
            }
            .builtup-table { border-collapse: collapse; width: 100%; font-size: 12px; }
            .builtup-table th { color: #64748b; font-weight: 600; padding: 4px 6px; text-align: center; }
            .builtup-table td { padding: 3px 4px; text-align: center; }
            .bu-cell { display: inline-block; width: 28px; height: 22px; border-radius: 4px; margin: 1px; }
            .bu-lb { background: #059669; }
            .bu-sb { background: #dc2626; }
            .bu-sc { background: #2563eb; }
            .bu-lu { background: #a3a30a; }
            .bu-na { background: #94a3b8; }
            .news-box, .ca-box {
                background: #ffffff; border: 1px solid #c7d2fe;
                border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;
                color: #0f172a !important; box-shadow: 0 2px 8px rgba(99,102,241,0.08);
            }
            .news-box a, .ca-box a { color: #4f46e5 !important; }

        </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _source_short(source: str) -> str:
    """Single-letter (or short) prefix for the data source, used on index cards."""
    if not source:
        return "?"
    s = source.lower()
    if "upstox" in s:
        return "U"
    if "moneycontrol" in s:
        return "M"
    if "investing" in s:
        return "I"
    if "tradingview" in s:
        return "T"
    if "yahoo" in s:
        return "Y"
    if "tradingeconomics" in s:
        return "TE"
    if "nse" in s:
        return "N"
    # First character of first word as last resort
    first = source.strip().split()[0] if source.strip() else "?"
    return first[0].upper() if first else "?"

def _ist_now_label() -> str:
    """Current IST timestamp string used as refresh marker on cards."""
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d %b %Y, %H:%M:%S IST")

def nse_session_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Referer": "https://www.nseindia.com/option-chain",
        "Origin": "https://www.nseindia.com",
        "Connection": "keep-alive",
    }

def is_nse_market_hours():
    """Rough NSE cash market hours 09:15–15:30 IST (Mon–Fri)."""
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    if now.weekday() >= 5:
        return False
    t = now.time()
    return dtime(9, 15) <= t <= dtime(15, 30)

@st.cache_data(ttl=15)
def fetch_yahoo_quote(ticker: str):
    """Robust Yahoo Finance quote — used for cash indices AND as final fallback for futures/commodities."""
    if not ticker or ticker in ("GIFT_NIFTY", "US_TECH_FUT", "US_30_FUT"):
        return None
    try:
        t = yf.Ticker(ticker)
        # Prefer short intraday history for live-ish price
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
                # Prefer previous daily close for change when available
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
                src = f"Yahoo Finance ({ticker})"
                ts = _ist_now_label()
                return {
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "pct": round(pct, 2),
                    "source": src,
                    "source_short": _source_short(src),
                    "source_time_label": ts,
                    "fetched_at": ts,
                }
        # fast_info fallback
        info = t.fast_info
        price = getattr(info, "last_price", None) or getattr(info, "regular_market_price", None)
        prev = getattr(info, "previous_close", None) or price
        if price is not None:
            change = float(price) - float(prev)
            pct = (change / float(prev) * 100) if prev else 0
            src = f"Yahoo Finance ({ticker})"
            ts = _ist_now_label()
            return {
                "price": round(float(price), 2),
                "change": round(change, 2),
                "pct": round(pct, 2),
                "source": src,
                "source_short": _source_short(src),
                "source_time_label": ts,
                "fetched_at": ts,
            }
    except Exception:
        pass
    return None


@st.cache_data(ttl=15)
def fetch_index_quote(ticker: str):
    """Yahoo for Indian cash indices (Nifty, Bank Nifty, Midcaps, Sensex, VIX)."""
    return fetch_yahoo_quote(ticker)

@st.cache_data(ttl=20, show_spinner=False)
def fetch_tradingview_quote(tv_symbol: str):
    """Best-effort public TradingView scanner quote."""
    try:
        exchange = tv_symbol.split(":", 1)[0].upper()
        region_map = {
            "NSEIX": "india", "NSE": "india", "MCX": "india", "BSE": "india",
            "COMEX": "america", "NYMEX": "america", "ICEEUR": "america", "DJ": "america",
            "NASDAQ": "america", "TVC": "america", "NYSE": "america", "CME": "america",
            "CBOT": "america", "CME_MINI": "america",
            "COINBASE": "crypto", "BINANCE": "crypto",
            "FX_IDC": "forex", "OANDA": "forex",
            "HSI": "hongkong", "TSE": "japan", "SSE": "china", "KRX": "korea", "ASX": "australia",
            "TWSE": "taiwan", "LSE": "uk", "FTSE": "uk"
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
        src = f"TradingView ({tv_symbol})"
        ts = _ist_now_label()
        return {
            "price": round(float(price), 2),
            "change": round(float(change or 0), 2),
            "pct": round(float(pct or 0), 2),
            "source": src,
            "source_short": _source_short(src),
            "source_time_label": ts,
            "fetched_at": ts,
        }
    except Exception:
        return None

@st.cache_data(ttl=30, show_spinner=False)
def fetch_investing_quote(slug: str):
    """Investing.com page parser — secondary fallback (24h coverage when it works)."""
    try:
        url = "https://www.investing.com/" + slug
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code != 200:
            return None
        html = r.text

        def extract(pattern):
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
        src = f"Investing.com ({slug})"
        ts = _ist_now_label()
        return {
            "price": round(price, 2),
            "change": round(change, 2),
            "pct": round(pct, 2),
            "source": src,
            "source_short": _source_short(src),
            "source_time_label": ts,
            "fetched_at": ts,
        }
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_tradingeconomics_quote(slug: str):
    """Parse TradingEconomics index page for price / change / pct. Used as final fallback for US100 & US30."""
    try:
        url = f"https://tradingeconomics.com/{slug}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            return None
        html = r.text
        # Actual value often in first large number after "Actual"
        m_price = re.search(r'Actual\s*</[^>]*>\s*([0-9,]+(?:\.[0-9]+)?)', html, re.I | re.S)
        if not m_price:
            m_price = re.search(r'traded at\s+([0-9,]+(?:\.[0-9]+)?)', html, re.I)
        if not m_price:
            m_price = re.search(r'([0-9]{4,6}(?:\.[0-9]+)?)\s*(?:this|Index Points)', html, re.I)
        price = None
        if m_price:
            price = float(m_price.group(1).replace(",", ""))
        # Daily Change: 341.79 1.17%
        m_chg = re.search(r'Daily Change\s*</[^>]*>\s*([+-]?[0-9,]+(?:\.[0-9]+)?)\s+([+-]?[0-9.]+)\s*%', html, re.I | re.S)
        change = pct = 0.0
        if m_chg:
            change = float(m_chg.group(1).replace(",", ""))
            pct = float(m_chg.group(2))
        else:
            m2 = re.search(r'([+-]?[0-9,]+(?:\.[0-9]+)?)\s+([+-]?[0-9.]+)\s*%', html)
            if m2 and price:
                change = float(m2.group(1).replace(",", ""))
                pct = float(m2.group(2))
        if price is None or price <= 0:
            return None
        src = f"TradingEconomics ({slug})"
        ts = _ist_now_label()
        return {
            "price": round(price, 2),
            "change": round(change, 2),
            "pct": round(pct, 2),
            "source": src,
            "source_short": _source_short(src),
            "source_time_label": ts,
            "fetched_at": ts,
        }
    except Exception:
        return None


@st.cache_data(ttl=20, show_spinner=False)
def fetch_investing_brent():
    """Live Brent crude from Investing.com (in. domain preferred).
    URL: https://in.investing.com/commodities/brent-oil
    Falls back to www.investing.com/commodities/brent-oil.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://in.investing.com/",
    }

    def number(value):
        if not value:
            return None
        cleaned = re.sub(r"[^0-9.+-]", "", str(value).replace(",", ""))
        try:
            return float(cleaned) if cleaned not in ("", "+", "-") else None
        except ValueError:
            return None

    def parse_html(html, source_label):
        def extract(pattern):
            m = re.search(pattern, html, flags=re.I | re.S)
            return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else None

        price_text = extract(r'data-test=["\']instrument-price-last["\'][^>]*>(.*?)</')
        change_text = extract(r'data-test=["\']instrument-price-change["\'][^>]*>(.*?)</')
        pct_text = extract(r'data-test=["\']instrument-price-change-percent["\'][^>]*>(.*?)</')
        if not price_text:
            m = re.search(r'["\']last["\']\s*:\s*["\']?([0-9,]+\.?[0-9]*)', html, flags=re.I)
            price_text = m.group(1) if m else None
        if not price_text:
            # Plain-text fallback near "Brent"
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            m = re.search(
                r"Brent.{0,120}?([0-9]{2,3}\.[0-9]{1,2})\s*([+-]?[0-9]+\.?[0-9]*)?\s*\(?\s*([+-]?[0-9]+\.?[0-9]*)?\s*%?",
                plain, re.I,
            )
            if m:
                price_text = m.group(1)
                if not change_text and m.group(2):
                    change_text = m.group(2)
                if not pct_text and m.group(3):
                    pct_text = m.group(3)

        price = number(price_text)
        change = number(change_text) or 0.0
        pct = number(pct_text) or 0.0
        # Brent sanity band — reject % returns misread as price
        if price is None or not (50.0 <= price <= 200.0):
            return None
        ts = _ist_now_label()
        return {
            "price": round(float(price), 2),
            "change": round(float(change), 2),
            "pct": round(float(pct), 2),
            "source": source_label,
            "source_short": _source_short(source_label),
            "source_time_label": ts,
            "fetched_at": ts,
        }

    urls = [
        ("https://in.investing.com/commodities/brent-oil", "Investing.com (Brent Oil)"),
        ("https://www.investing.com/commodities/brent-oil", "Investing.com (Brent Oil)"),
    ]
    for url, label in urls:
        try:
            r = requests.get(url, headers={**headers, "Referer": url.rsplit("/", 1)[0] + "/"}, timeout=8)
            if r.status_code != 200:
                continue
            quote = parse_html(r.text, label)
            if quote:
                return quote
        except Exception:
            continue
    return None


# Investing.com slug map (secondary fallback)
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
    "^TWII": "indices/taiwan-weighted",
    "^FTSE": "indices/uk-100",
    "MIDCAP_SELECT": "indices/nifty-midcap-select",
    "NIFTY_MID_SELECT": "indices/nifty-midcap-select",
}

# Yahoo tickers used as FINAL reliable fallback (matches your suggested table)
YAHOO_FALLBACK = {
    "GIFT_NIFTY": None,          # not reliable on Yahoo
    "US_TECH_FUT": "^NDX",       # Nasdaq-100 index (closest liquid proxy)
    "US_30_FUT": "^DJI",         # Dow Jones
    "CL=F": "CL=F",
    "BZ=F": None,          # Investing.com is source for Brent (no Yahoo)
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
    "^TWII": "^TWII",
    "^FTSE": "^FTSE",
    "MIDCAP_SELECT": None,
    "NIFTY_MID_SELECT": None,
}

@st.cache_data(ttl=20, show_spinner=False)
def fetch_live_instrument(key: str, tv_symbols=(), investing_key: str = None, yahoo_ticker: str = None):
    """
    Priority (most reliable first for each source):
      1) TradingView scanner
      2) Investing.com page parse
      3) Yahoo Finance  ← restored as final fallback (worked for most instruments earlier)
    """
    if isinstance(tv_symbols, str):
        tv_symbols = (tv_symbols,)
    # 1) TradingView
    for symbol in tv_symbols:
        quote = fetch_tradingview_quote(symbol)
        if quote:
            # Reject absurd Brent quotes (e.g. a % return scraped as price)
            if key in ("BZ=F", "CRUDE OIL BRENT") or (investing_key or key) in ("BZ=F",):
                if not (50.0 <= float(quote.get("price") or 0) <= 200.0):
                    quote = None
            if quote:
                return quote
    slug_key = investing_key or key
    # 2) Investing.com for Brent (in.investing.com/commodities/brent-oil) — before Investing
    if key in ("BZ=F", "CRUDE OIL BRENT") or slug_key in ("BZ=F",):
        brent = fetch_investing_brent()
        if brent:
            return brent
    # 3) Investing.com
    slug = INVESTING_SLUGS.get(slug_key)
    if slug:
        inv = fetch_investing_quote(slug)
        if inv:
            if key in ("BZ=F", "CRUDE OIL BRENT") or slug_key in ("BZ=F",):
                if not (50.0 <= float(inv.get("price") or 0) <= 200.0):
                    inv = None
            if inv:
                return inv
    # 4) Yahoo Finance (final) — skipped for Brent via YAHOO_FALLBACK=None
    y_ticker = yahoo_ticker or YAHOO_FALLBACK.get(key) or YAHOO_FALLBACK.get(slug_key)
    if y_ticker:
        yq = fetch_yahoo_quote(y_ticker)
        if yq:
            return yq
    # Last-ditch: try the raw key itself on Yahoo if it looks like a ticker
    if key and key not in ("GIFT_NIFTY", "US_TECH_FUT", "US_30_FUT") and ("=" in key or key.startswith("^") or key.endswith(".SS")):
        yq = fetch_yahoo_quote(key)
        if yq:
            return yq
    # 4) TradingEconomics final fallback for US indices
    te_map = {"US_TECH_FUT": "us100:ind", "US_30_FUT": "indu:ind", "^NDX": "us100:ind", "^DJI": "indu:ind"}
    te_slug = te_map.get(key)
    if te_slug:
        teq = fetch_tradingeconomics_quote(te_slug)
        if teq:
            return teq
    return None

@st.cache_data(ttl=10, show_spinner=False)
def fetch_gift_nifty_50():
    """Fetch GIFT Nifty from all available sources and prefer the newest parseable source timestamp.

    A timestamp is only assigned when the response contains a recognisable update-time marker.
    TradingView scanner quotes are used as an untimestamped fallback because its scanner response
    does not provide a comparable quote timestamp in this implementation.
    """
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://upstox.com/",
    }
    candidates = []

    def parse_timestamp(raw_text, source):
        """Parse explicit source update-time text to an IST-aware datetime; otherwise return None."""
        if not raw_text:
            return None
        raw = re.sub(r"\s+", " ", raw_text).strip()
        # Prefer explicit full dates and times.
        patterns = [
            (r"(?:last\s+updated(?:\s+on)?|updated\s+at|as\s+on)\s*[:|-]?\s*(\d{1,2}\s+[A-Za-z]{3,9},?\s+\d{4})\s*(?:\||,|at)?\s*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\s*(?:IST|GMT\+?5:?30)?)", ["%d %b, %Y %H:%M:%S", "%d %b, %Y %H:%M", "%d %b, %Y %I:%M %p", "%d %B, %Y %H:%M:%S", "%d %B, %Y %H:%M", "%d %B, %Y %I:%M %p"]),
            (r"(?:last\s+updated(?:\s+on)?|updated\s+at|as\s+on)\s*[:|-]?\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})\s*(?:\||,|at)?\s*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\s*(?:IST|GMT\+?5:?30)?)", ["%b %d, %Y %H:%M:%S", "%b %d, %Y %H:%M", "%b %d, %Y %I:%M %p", "%B %d, %Y %H:%M:%S", "%B %d, %Y %H:%M", "%B %d, %Y %I:%M %p"]),
            (r"(?:last\s+updated(?:\s+on)?|updated\s+at|as\s+on)\s*[:|-]?\s*(\d{4}-\d{2}-\d{2})[ T,]+(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\s*(?:IST|GMT\+?5:?30)?)", ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %I:%M %p"]),
        ]
        for pattern, formats in patterns:
            m = re.search(pattern, raw, re.I)
            if not m:
                continue
            date_part, time_part = m.group(1).strip(), m.group(2).strip()
            time_part = re.sub(r"\s*(IST|GMT\+?5:?30)$", "", time_part, flags=re.I).strip()
            combined = f"{date_part} {time_part}"
            for fmt in formats:
                try:
                    dt = datetime.strptime(combined, fmt)
                    return ist.localize(dt)
                except ValueError:
                    continue
        # Investing.com may show only a clock time beside a market status.
        if source == "Investing.com":
            m = re.search(r"(?:closed|last updated|updated)\s*[·|,:-]?\s*(\d{1,2}:\d{2}:\d{2})", raw, re.I)
            if m:
                try:
                    dt = datetime.strptime(now_ist.strftime("%Y-%m-%d") + " " + m.group(1), "%Y-%m-%d %H:%M:%S")
                    parsed = ist.localize(dt)
                    # Avoid treating a clock time far in the future as a current update.
                    if parsed <= now_ist:
                        return parsed
                except ValueError:
                    pass
        return None

    def add_candidate(price, change, pct, source, timestamp=None):
        try:
            price = float(price)
            change = float(change or 0)
            pct = float(pct or 0)
            if 15000 < price < 40000:
                short = _source_short(source)
                if timestamp:
                    time_str = timestamp.strftime("%d %b %Y, %H:%M:%S IST")
                else:
                    time_str = "timestamp unavailable"
                candidates.append({
                    "price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2),
                    "source": source, "source_timestamp": timestamp,
                    "source_short": short,
                    "source_time_label": f"{short} {time_str}",
                    "fetched_at": time_str if timestamp else _ist_now_label(),
                })
        except (TypeError, ValueError):
            pass

    # 1) Upstox — parse both the quote and any explicit update timestamp.
    try:
        r = requests.get("https://upstox.com/gift-nifty/", headers=headers, timeout=8)
        if r.status_code == 200:
            html = r.text
            timestamp = parse_timestamp(re.sub(r"<[^>]+>", " ", html), "Upstox")
            plain = re.sub(r"<script.*?</script>", " ", html, flags=re.I | re.S)
            plain = re.sub(r"<[^>]+>", " ", plain)
            plain = re.sub(r"\s+", " ", plain)
            m = re.search(r"(2[0-9],\d{3}\.\d{2})\s+([+-]?\d{1,3}(?:,\d{3})*\.?\d*)\s*\(\s*([+-]?\d+\.?\d*)\s*%\s*\)", plain)
            if m:
                add_candidate(m.group(1).replace(",", ""), m.group(2).replace(",", ""), m.group(3), "Upstox GIFT Nifty", timestamp)
            else:
                pm = re.search(r"GIFT NIFTY Live.*?(2[0-9],\d{3}\.\d{2})", plain, re.I | re.S) or re.search(r"(2[0-9],\d{3}\.\d{2})", plain)
                prev_m = re.search(r"Previous session close\s*([\d,]+\.?\d*)", plain, re.I)
                if pm:
                    price = float(pm.group(1).replace(",", ""))
                    prev = float(prev_m.group(1).replace(",", "")) if prev_m else price
                    add_candidate(price, price-prev, ((price-prev)/prev*100 if prev else 0), "Upstox GIFT Nifty", timestamp)
    except Exception:
        pass

    # 2) Moneycontrol — use its explicit 'As on' timestamp when present.
    try:
        r = requests.get("https://www.moneycontrol.com/live-index/gift-nifty?symbol=in;gsx", headers={**headers, "Referer": "https://www.moneycontrol.com/"}, timeout=8)
        if r.status_code == 200:
            html = r.text
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            timestamp = parse_timestamp(plain, "Moneycontrol")
            # Also support the commonly displayed 'As on 20 Oct, 2026 | 20:47 IST' layout.
            if timestamp is None:
                tm = re.search(r"As\s+on\s+(\d{1,2}\s+[A-Za-z]{3,9},?\s+\d{4})\s*[|,]?\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*IST", plain, re.I)
                if tm:
                    for fmt in ("%d %b, %Y %H:%M:%S", "%d %b, %Y %H:%M", "%d %B, %Y %H:%M:%S", "%d %B, %Y %H:%M"):
                        try:
                            timestamp = ist.localize(datetime.strptime(tm.group(1) + " " + tm.group(2), fmt))
                            break
                        except ValueError:
                            continue
            # Prefer a number near the GIFT Nifty label rather than the first 5-digit number on the page.
            price = None
            for pat in (r"GIFT\s*Nifty.{0,180}?(2[0-9],\d{3}(?:\.\d{1,2})?)", r"(2[0-9],\d{3}(?:\.\d{1,2})?).{0,100}?GIFT\s*Nifty"):
                pm = re.search(pat, plain, re.I)
                if pm:
                    price = float(pm.group(1).replace(",", "")); break
            if price is None:
                nums = re.findall(r"(2[0-9],\d{3}(?:\.\d{1,2})?)", plain)
                if nums:
                    price = float(nums[0].replace(",", ""))
            chg_m = re.search(r"([+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*\(\s*([+-]?\d+\.?\d*)\s*%\s*\)", plain)
            prev_m = re.search(r"Previous\s*Close\s*([\d,]+\.?\d*)", plain, re.I)
            if price is not None:
                if chg_m:
                    change, pct = float(chg_m.group(1).replace(",", "")), float(chg_m.group(2))
                elif prev_m:
                    prev = float(prev_m.group(1).replace(",", "")); change = price-prev; pct = change/prev*100 if prev else 0
                else:
                    change = pct = 0
                add_candidate(price, change, pct, "Moneycontrol GIFT Nifty", timestamp)
    except Exception:
        pass

    # 3) Investing.com — inspect both the page's quote and any explicit update time.
    try:
        gift_url = "https://in.investing.com/indices/gift-nifty-50-c1-futures"
        r = requests.get(gift_url, headers={**headers, "Referer": "https://in.investing.com/"}, timeout=10)
        if r.status_code == 200:
            html = r.text
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            timestamp = parse_timestamp(plain, "Investing.com")
            if timestamp is None:
                # Parse explicit instrument update markers only; do not infer a timestamp from arbitrary page metadata.
                tm = re.search(r"(?:instrument-price-last-update|last-update|lastUpdate)[^>]{0,160}>([^<]{0,100})<", html, re.I)
                if tm:
                    timestamp = parse_timestamp(tm.group(1), "Investing.com")
            def num(raw):
                if not raw: return None
                cleaned = re.sub(r"[^0-9.+-]", "", raw.replace(",", ""))
                try: return float(cleaned) if cleaned not in ("", "+", "-") else None
                except ValueError: return None
            pm = re.search(r'data-test=["\']instrument-price-last["\'][^>]*>\s*([0-9,]+(?:\.\d+)?)', html, re.I)
            if not pm:
                pm = re.search(r'["\']last["\']\s*:\s*["\']?([0-9,]+(?:\.\d+)?)', html, re.I)
            if pm:
                price = num(pm.group(1))
                cm = re.search(r'data-test=["\']instrument-price-change["\'][^>]*>\s*([^<]+)', html, re.I)
                xm = re.search(r'data-test=["\']instrument-price-change-percent["\'][^>]*>\s*([^<]+)', html, re.I)
                add_candidate(price, num(cm.group(1)) if cm else 0, num(xm.group(1)) if xm else 0, "Investing.com GIFT Nifty 50 Futures", timestamp)
    except Exception:
        pass

    # 4) TradingView scanner quote. Scanner response does not expose a reliable comparable timestamp.
    for symbol in ("NSEIX:NIFTY1!", "NSEIX:NIFTY2!", "NSEIX:GIFTNIFTY1!", "NSEIX:GIFTNIFTY"):
        try:
            quote = fetch_tradingview_quote(symbol)
            if quote and 15000 < quote["price"] < 40000:
                quote = dict(quote)
                src = f"TradingView ({symbol})"
                short = _source_short(src)
                quote["source"] = src
                quote["source_timestamp"] = None
                quote["source_short"] = short
                quote["source_time_label"] = f"{short} timestamp unavailable"
                candidates.append(quote)
                break
        except Exception:
            continue

    if not candidates:
        return None
    timestamped = [q for q in candidates if q.get("source_timestamp") is not None]
    if timestamped:
        # Only choose among source quotes with explicit, parseable update times.
        selected = max(timestamped, key=lambda q: q["source_timestamp"])
        selected["timestamp_selection"] = "newest explicit source timestamp"
        return selected
    # If every source omits a parseable timestamp, disclose that limitation in the card caption.
    # Preserve the established fallback priority rather than claiming any quote is demonstrably newest.
    priority = {"Upstox GIFT Nifty": 0, "Moneycontrol GIFT Nifty": 1, "Investing.com GIFT Nifty 50 Futures": 2}
    selected = min(candidates, key=lambda q: priority.get(q.get("source", ""), 3))
    selected["timestamp_selection"] = "no source exposed a parseable timestamp"
    return selected


@st.cache_data(ttl=20, show_spinner=False)
def fetch_midcap_select():
    """Nifty Mid Select from Moneycontrol + Investing.com; prefer the quote with the newest parseable timestamp."""
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    candidates = []

    def parse_ts(raw_text):
        if not raw_text:
            return None
        raw = re.sub(r"\s+", " ", raw_text).strip()
        patterns = [
            (r"(?:As\s+on|last\s+updated(?:\s+on)?|updated\s+at)\s*[:|-]?\s*(\d{1,2}\s+[A-Za-z]{3,9},?\s+\d{4})\s*[|,]?\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*(?:IST)?",
             ["%d %b, %Y %H:%M:%S", "%d %b, %Y %H:%M", "%d %B, %Y %H:%M:%S", "%d %B, %Y %H:%M"]),
            (r"(?:As\s+on|last\s+updated(?:\s+on)?|updated\s+at)\s*[:|-]?\s*(\d{1,2}\s+[A-Za-z]{3,9},?\s+\d{4})",
             ["%d %b, %Y", "%d %B, %Y"]),
        ]
        for pattern, formats in patterns:
            m = re.search(pattern, raw, re.I)
            if not m:
                continue
            parts = [g for g in m.groups() if g]
            combined = " ".join(parts)
            for fmt in formats:
                try:
                    dt = datetime.strptime(combined, fmt)
                    if "%H" not in fmt:
                        dt = dt.replace(hour=now_ist.hour, minute=now_ist.minute, second=0)
                    return ist.localize(dt)
                except ValueError:
                    continue
        return None

    def add_cand(price, change, pct, source, timestamp=None):
        try:
            price = float(price)
            change = float(change or 0)
            pct = float(pct or 0)
            if 5000 < price < 30000:
                short = _source_short(source)
                if timestamp:
                    time_str = timestamp.strftime("%d %b %Y, %H:%M:%S IST")
                else:
                    time_str = "timestamp unavailable"
                candidates.append({
                    "price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2),
                    "source": source, "source_timestamp": timestamp,
                    "source_short": short,
                    "source_time_label": f"{short} {time_str}",
                    "fetched_at": time_str if timestamp else _ist_now_label(),
                })
        except (TypeError, ValueError):
            pass

    # 1) Moneycontrol — https://www.moneycontrol.com/indian-indices/nifty-mid-select-128.html
    try:
        r = requests.get(
            "https://www.moneycontrol.com/indian-indices/nifty-mid-select-128.html",
            headers={**headers, "Referer": "https://www.moneycontrol.com/"},
            timeout=8,
        )
        if r.status_code == 200:
            html = r.text
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            timestamp = parse_ts(plain)
            price = None
            for pat in (
                r"Nifty\s*Mid\s*Select.{0,120}?([\d,]{4,}\.\d{1,2})",
                r"([\d,]{4,}\.\d{1,2}).{0,80}?Nifty\s*Mid\s*Select",
                r'id=["\']lastprice["\'][^>]*>\s*([\d,]+\.?\d*)',
                r'data-lastprice=["\']([\d.]+)',
            ):
                m = re.search(pat, plain if "id=" not in pat else html, re.I)
                if m:
                    try:
                        price = float(m.group(1).replace(",", ""))
                        break
                    except ValueError:
                        continue
            chg_m = re.search(r"([+-]?[\d,]+\.?\d*)\s*\(\s*([+-]?\d+\.?\d*)\s*%\s*\)", plain)
            prev_m = re.search(r"Previous\s*Close\s*([\d,]+\.?\d*)", plain, re.I)
            if price is not None:
                if chg_m:
                    change = float(chg_m.group(1).replace(",", ""))
                    pct = float(chg_m.group(2))
                elif prev_m:
                    prev = float(prev_m.group(1).replace(",", ""))
                    change = price - prev
                    pct = (change / prev * 100) if prev else 0
                else:
                    change = pct = 0
                add_cand(price, change, pct, "Moneycontrol Nifty Mid Select", timestamp)
    except Exception:
        pass

    # 2) Investing.com — https://in.investing.com/indices/nifty-midcap-select
    try:
        inv = fetch_investing_quote("indices/nifty-midcap-select")
        if inv and inv.get("price"):
            inv = dict(inv)
            inv["source"] = "Investing.com Nifty Midcap Select"
            inv["source_short"] = _source_short(inv["source"])
            inv["source_timestamp"] = None
            inv["source_time_label"] = f"{inv['source_short']} {inv.get('fetched_at') or _ist_now_label()}"
            candidates.append(inv)
    except Exception:
        pass

    # 3) TradingView fallback
    for symbol in ("NSE:NIFTYMIDSELECT", "NSE:NIFTY_MID_SELECT", "TVC:NIFTYMIDSELECT"):
        try:
            quote = fetch_tradingview_quote(symbol)
            if quote and 5000 < quote["price"] < 30000:
                quote = dict(quote)
                src = f"TradingView ({symbol})"
                short = _source_short(src)
                quote["source"] = src
                quote["source_timestamp"] = None
                quote["source_short"] = short
                quote["source_time_label"] = f"{short} timestamp unavailable"
                candidates.append(quote)
                break
        except Exception:
            continue

    if not candidates:
        return None
    timestamped = [q for q in candidates if q.get("source_timestamp") is not None]
    if timestamped:
        return max(timestamped, key=lambda q: q["source_timestamp"])
    priority = {"Moneycontrol Nifty Mid Select": 0, "Investing.com Nifty Midcap Select": 1}
    return min(candidates, key=lambda q: priority.get(q.get("source", ""), 3))


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
        return None

@st.cache_data(ttl=60)
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
        return None

@st.cache_data(ttl=90)
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
        return None

def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def generate_renko(df: pd.DataFrame, box_size: float) -> pd.DataFrame:
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
    return renko_df

@st.cache_data(ttl=90)
def get_top_movers(universe: list):
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
                chg = last - prev
                rows.append({"Symbol": sym, "LTP": round(last, 2), "Change": round(chg, 2), "% Chg": round((chg / prev) * 100, 2)})
            except Exception:
                continue
        df = pd.DataFrame(rows)
        if df.empty:
            return None, None
        return (
            df.sort_values("% Chg", ascending=False).head(8).reset_index(drop=True),
            df.sort_values("% Chg", ascending=True).head(8).reset_index(drop=True)
        )
    except Exception:
        return None, None

def analyze_renko_signal(symbol: str, timeframe: str):
    interval = "1h" if timeframe == "1 Hour" else "30m"
    period = "1mo" if interval == "1h" else "5d"
    candles = get_ohlc_data(symbol, interval=interval, period=period)
    if candles is None or candles.empty or len(candles) < 22:
        return None
    candles = candles.tail(120 if interval == "1h" else 150).copy().reset_index(drop=True)

    def _to_ist(ts):
        """Convert candle/brick timestamp to Asia/Kolkata. Naive yfinance intraday bars are UTC."""
        t = pd.Timestamp(ts)
        if t.tzinfo is None:
            # yfinance typically returns naive UTC for NSE intraday; convert UTC → IST
            try:
                t = t.tz_localize("UTC").tz_convert("Asia/Kolkata")
            except Exception:
                t = t.tz_localize("Asia/Kolkata")
        else:
            t = t.tz_convert("Asia/Kolkata")
        return t

    if not candles.empty:
        last_time = _to_ist(candles["Date"].iloc[-1])
        bar_length = pd.Timedelta(hours=1 if interval == "1h" else 0, minutes=30 if interval == "30m" else 0)
        if last_time + bar_length > pd.Timestamp.now(tz="Asia/Kolkata") and len(candles) > 1:
            candles = candles.iloc[:-1].reset_index(drop=True)
    if len(candles) < 22:
        return None
    candles["EMA20"] = calculate_ema(candles["Close"], 20)
    price = float(candles["Close"].iloc[-1])
    ema20 = float(candles["EMA20"].iloc[-1])
    daily_atr = get_daily_atr(symbol, 14, 7) or get_daily_atr(symbol, 14, 14) or (price * 0.005)
    box_size = daily_atr / 5 if interval == "1h" else daily_atr / 10
    bricks = generate_renko(candles, box_size)
    if bricks.empty or len(bricks) < 2:
        return None
    first, second = bricks.iloc[-2], bricks.iloc[-1]
    first_green = float(first["Close"]) > float(first["Open"])
    second_green = float(second["Close"]) > float(second["Open"])
    first_red = float(first["Close"]) < float(first["Open"])
    second_red = float(second["Close"]) < float(second["Open"])
    if first_green and second_green:
        direction = "BULLISH"
        action = "BUY" if price > ema20 else "BULLISH"
        entry = float(second["Close"])
        exit_price = float(first["Low"])
    elif first_red and second_red:
        direction = "BEARISH"
        action = "SELL" if price < ema20 else "BEARISH"
        entry = float(second["Close"])
        exit_price = float(first["High"])
    else:
        return None
    last_brick_ts = _to_ist(bricks["Date"].iloc[-1])
    now = pd.Timestamp.now(tz="Asia/Kolkata")
    age_minutes = (now - last_brick_ts).total_seconds() / 60.0
    # Clamp negative age (clock skew / incomplete bar) to 0
    if age_minutes < 0:
        age_minutes = 0.0
    just_entered = age_minutes <= 20
    return {
        "Stock": symbol, "Timeframe": timeframe, "Signal": action, "Renko": direction,
        "Price": round(price, 2), "EMA 20": round(ema20, 2),
        "Entry": round(entry, 2), "Exit": round(exit_price, 2),
        "Box Size": round(float(box_size), 2),
        "Last Brick Time": last_brick_ts.strftime("%d %b %H:%M"),
        "Last Brick TS": last_brick_ts, "Age Minutes": round(age_minutes, 1),
        "Just Entered": just_entered
    }

@st.cache_data(ttl=90, show_spinner=False)
def scan_renko_universe(universe_tuple: tuple):
    jobs = [(symbol, timeframe) for symbol in universe_tuple for timeframe in ("1 Hour", "30 Minutes")]
    rows = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(analyze_renko_signal, symbol, timeframe) for symbol, timeframe in jobs]
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    rows.append(result)
            except Exception:
                continue
    if not rows:
        return pd.DataFrame()
    result_df = pd.DataFrame(rows)
    # Required order:
    #   1) 1 Hour     — BUY / BULLISH (newest first)
    #   2) 1 Hour     — SELL / BEARISH (newest first)
    #   3) 30 Minutes — BUY / BULLISH (newest first)
    #   4) 30 Minutes — SELL / BEARISH (newest first)
    tf_order = {"1 Hour": 0, "30 Minutes": 1}
    sig_order = {"BUY": 0, "BULLISH": 1, "SELL": 2, "BEARISH": 3}
    result_df["_tf"] = result_df["Timeframe"].map(tf_order).fillna(9)
    result_df["_sig"] = result_df["Signal"].map(sig_order).fillna(9)
    # Order: 1H BUY → 1H BULLISH → 1H SELL → 1H BEARISH → 30M BUY → …
    # Within each group: lowest Age Minutes (newest) on top
    result_df = result_df.sort_values(
        by=["_tf", "_sig", "Age Minutes", "Last Brick TS"],
        ascending=[True, True, True, False],
        kind="stable"
    ).drop(columns=["_tf", "_sig"]).reset_index(drop=True)
    return result_df

@st.cache_data(ttl=30)
def get_options_chain(ltp: float, symbol: str):
    headers = nse_session_headers()
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=8)
        session.get("https://www.nseindia.com/option-chain", headers=headers, timeout=8)
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            raise Exception(f"NSE status {r.status_code}")
        data = r.json()
        records = data.get("records", {})
        underlying = records.get("underlyingValue", ltp)
        options = records.get("data", [])
        if not options:
            raise Exception("Empty chain")
        strike_map = {}
        for item in options:
            strike = item.get("strikePrice")
            if strike is None:
                continue
            ce = item.get("CE", {})
            pe = item.get("PE", {})
            strike_map[strike] = {
                "CE": ce.get("lastPrice") or ce.get("lastTradedPrice") or 0,
                "PE": pe.get("lastPrice") or pe.get("lastTradedPrice") or 0,
            }
        if not strike_map:
            raise Exception("No strikes")
        strikes = sorted(strike_map.keys())
        atm = min(strikes, key=lambda x: abs(x - underlying))
        atm_idx = strikes.index(atm)
        selected_strikes = strikes[max(0, atm_idx - 2): atm_idx + 3]
        rows = []
        for s in selected_strikes:
            rows.append({
                "Call Price (CE)": round(float(strike_map[s]["CE"]), 2),
                "Strike Price": s,
                "Put Price (PE)": round(float(strike_map[s]["PE"]), 2)
            })
        return pd.DataFrame(rows)
    except Exception:
        gap = 50 if ltp > 1000 else (20 if ltp > 500 else 10)
        atm = round(ltp / gap) * gap
        strikes = [atm + i * gap for i in range(-2, 3)]
        rows = []
        for s in strikes:
            ce = max(1, (ltp - s) + np.random.uniform(5, 25)) if s <= ltp else np.random.uniform(2, 20)
            pe = max(1, (s - ltp) + np.random.uniform(5, 25)) if s >= ltp else np.random.uniform(2, 20)
            rows.append({"Call Price (CE)": round(ce, 2), "Strike Price": s, "Put Price (PE)": round(pe, 2)})
        return pd.DataFrame(rows)

@st.cache_data(ttl=3600)
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
        "TITAN", "ULTRACEMCO", "UPL", "WIPRO", "ETERNAL"
    ]

NIFTY50_WEIGHT = {
    "HDFCBANK": 12.8, "ICICIBANK": 8.4, "RELIANCE": 8.0, "BHARTIARTL": 5.0, "INFY": 4.8,
    "SBIN": 4.0, "ITC": 3.6, "TCS": 3.5, "AXISBANK": 3.2, "KOTAKBANK": 2.8, "LT": 2.7,
    "BAJFINANCE": 2.5, "HINDUNILVR": 2.3, "M&M": 2.2, "TATAMOTORS": 1.9, "SUNPHARMA": 1.8,
    "MARUTI": 1.8, "HCLTECH": 1.7, "NTPC": 1.6, "TITAN": 1.5, "ULTRACEMCO": 1.4,
    "POWERGRID": 1.4, "TATASTEEL": 1.3, "ONGC": 1.2, "JSWSTEEL": 1.2, "BEL": 1.2,
    "ASIANPAINT": 1.1, "ADANIPORTS": 1.1, "BAJAJFINSV": 1.0, "COALINDIA": 1.0,
    "INDUSINDBK": 0.9, "GRASIM": 0.9, "TATACONSUM": 0.8, "NESTLEIND": 0.8, "WIPRO": 0.8,
    "TECHM": 0.7, "HINDALCO": 0.7, "DRREDDY": 0.7, "CIPLA": 0.7, "EICHERMOT": 0.6,
    "APOLLOHOSP": 0.6, "DIVISLAB": 0.6, "SBILIFE": 0.6, "HDFCLIFE": 0.6, "BRITANNIA": 0.5,
    "HEROMOTOCO": 0.5, "BAJAJ-AUTO": 0.5, "ADANIENT": 0.5, "ETERNAL": 0.5, "UPL": 0.3
}

@st.cache_data(ttl=60)
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
        return None

@st.cache_data(ttl=45, show_spinner=False)
def get_option_sentiment(symbol: str = "NIFTY"):
    """
    Returns dict: pcr, max_pain, atm_iv, source.
    Priority: NSE option-chain OI → Quantsapp max-pain page → niftytrader snapshot.
    Supports NIFTY / BANKNIFTY indices and individual equity symbols (NSE equity option chain).
    """
    sym = symbol.upper().replace(" ", "")
    is_index = False
    if sym in ["NIFTY", "NIFTY50"]:
        nse_symbol = "NIFTY"
        is_index = True
        qa_paths = [
            "https://www.quantsapp.com/max-pain/nifty",
            "https://web.quantsapp.com/option-pain/NIFTY",
        ]
    elif sym in ["BANKNIFTY", "NIFTYBANK"]:
        nse_symbol = "BANKNIFTY"
        is_index = True
        qa_paths = [
            "https://www.quantsapp.com/max-pain/banknifty",
            "https://web.quantsapp.com/option-pain/BANKNIFTY",
        ]
    else:
        # Equity F&O symbol
        nse_symbol = sym
        is_index = False
        qa_paths = [
            f"https://www.quantsapp.com/max-pain/{sym.lower()}",
            f"https://web.quantsapp.com/option-pain/{sym}",
        ]

    out = {"pcr": None, "max_pain": None, "atm_iv": None, "source": None}

    # ---- 1) NSE option-chain (authoritative PCR during market hours) ----
    headers = nse_session_headers()
    if is_index:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={nse_symbol}"
    else:
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={nse_symbol}"
    for _ in range(2):
        session = requests.Session()
        try:
            session.get("https://www.nseindia.com", headers=headers, timeout=6)
            session.get("https://www.nseindia.com/option-chain", headers=headers, timeout=6)
            response = session.get(url, headers=headers, timeout=8)
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", {})
                filtered = data.get("filtered", {}) or {}
                underlying = float(records.get("underlyingValue") or 0)
                expiry_dates = records.get("expiryDates") or []
                nearest_exp = expiry_dates[0] if expiry_dates else None

                # Prefer NSE "filtered" block (nearest/selected expiry only). Fall back to
                # records.data filtered by nearest expiryDate.
                chain_items = filtered.get("data") or []
                used_filtered = bool(chain_items)
                if not chain_items:
                    chain_items = records.get("data") or []

                ce_oi_total = pe_oi_total = 0
                for item in (records.get("data") or []):
                    ce = item.get("CE") or {}
                    pe = item.get("PE") or {}
                    ce_oi_total += int(ce.get("openInterest") or 0)
                    pe_oi_total += int(pe.get("openInterest") or 0)

                ce_oi_near = pe_oi_near = 0
                strike_oi = {}  # strike -> (ce_oi, pe_oi) for nearest expiry only
                for item in chain_items:
                    ce = item.get("CE") or {}
                    pe = item.get("PE") or {}
                    c_oi = int(ce.get("openInterest") or 0)
                    p_oi = int(pe.get("openInterest") or 0)
                    if not used_filtered and nearest_exp:
                        exp = (ce.get("expiryDate") or pe.get("expiryDate") or item.get("expiryDate") or "")
                        if exp and exp != nearest_exp:
                            continue
                    ce_oi_near += c_oi
                    pe_oi_near += p_oi
                    strike = item.get("strikePrice")
                    if strike is None:
                        continue
                    sk = float(strike)
                    # Keep strikes in a sane band around spot (avoids junk / far-series mix)
                    if underlying > 0 and (sk < underlying * 0.5 or sk > underlying * 1.5):
                        continue
                    strike_oi[sk] = (
                        strike_oi.get(sk, (0, 0))[0] + c_oi,
                        strike_oi.get(sk, (0, 0))[1] + p_oi,
                    )

                # PCR: nearest-expiry OI preferred; fall back to full-chain OI
                pcr_ce, pcr_pe = (ce_oi_near, pe_oi_near) if (ce_oi_near > 0 and pe_oi_near > 0) else (ce_oi_total, pe_oi_total)
                if pcr_ce > 0 and pcr_pe > 0:
                    pcr = pcr_pe / pcr_ce
                    if 0.05 < pcr < 10:
                        out["pcr"] = round(pcr, 3)
                        out["source"] = "NSE"

                # Max pain on nearest-expiry strikes only
                if strike_oi:
                    best_s, best_pain = None, None
                    for s in strike_oi:
                        pain = 0.0
                        for k, (c, p) in strike_oi.items():
                            if k < s:
                                pain += (s - k) * c
                            elif k > s:
                                pain += (k - s) * p
                        if best_pain is None or pain < best_pain:
                            best_pain = pain
                            best_s = s
                    # Sanity: max pain must sit near the underlying (reject truncated/wrong values)
                    if best_s is not None and underlying > 0 and (underlying * 0.5) <= best_s <= (underlying * 1.5):
                        out["max_pain"] = int(best_s) if best_s == int(best_s) else round(best_s, 1)
                    elif best_s is not None and underlying <= 0:
                        out["max_pain"] = int(best_s) if best_s == int(best_s) else round(best_s, 1)

                if out["pcr"] is not None:
                    return out
        except Exception:
            pass
        finally:
            try:
                session.close()
            except Exception:
                pass

    # Spot anchor for sanity-checking scraped max-pain (esp. equities / Quantsapp)
    spot_anchor = None
    if not is_index:
        try:
            t = yf.Ticker(f"{nse_symbol}.NS")
            fi = t.fast_info
            spot_anchor = getattr(fi, "last_price", None) or getattr(fi, "regular_market_price", None)
            if spot_anchor is not None:
                spot_anchor = float(spot_anchor)
        except Exception:
            spot_anchor = None

    def _accept_max_pain(val, anchor):
        """Reject truncated / absurd max-pain values (e.g. 83 when spot is 1899)."""
        try:
            v = float(val)
        except (TypeError, ValueError):
            return None
        if v <= 0:
            return None
        if anchor and anchor > 0:
            if not (anchor * 0.5 <= v <= anchor * 1.5):
                return None
        return int(v) if v == int(v) else round(v, 1)

    # ---- 2) Quantsapp (PCR + Max Pain + ATM IV) ----
    qa_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    for qa_url in qa_paths:
        try:
            r = requests.get(qa_url, headers=qa_headers, timeout=8)
            if r.status_code != 200:
                continue
            text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.I | re.S)
            plain = re.sub(r"<[^>]+>", " ", text)
            plain = re.sub(r"\s+", " ", plain)

            # PCR (OI) 1.11 or PCR (OI) **1.11**
            m = re.search(r"PCR\s*\(?\s*OI\s*\)?\s*[:\*]?\s*([0-9]+\.?[0-9]*)", plain, re.I)
            if not m:
                m = re.search(r"PCR[^0-9]{0,20}([0-9]+\.[0-9]{1,3})", plain, re.I)
            if m:
                try:
                    p = float(m.group(1))
                    if 0.05 < p < 10:
                        out["pcr"] = round(p, 3)
                except ValueError:
                    pass

            # Max pain — full strike (old regex [0-9]{2,3} truncated 1900→190, 1190→119)
            m = re.search(
                r"Max\s*pain\s*[:\*]?\s*\*?\s*([0-9][0-9,]{1,12}(?:\.[0-9]+)?)",
                plain, re.I,
            )
            if m:
                mp = _accept_max_pain(m.group(1).replace(",", ""), spot_anchor)
                if mp is not None:
                    out["max_pain"] = mp

            # ATM IV
            m = re.search(r"ATM\s*IV\s*[:\*]?\s*([0-9]+\.?[0-9]*)\s*%?", plain, re.I)
            if m:
                try:
                    out["atm_iv"] = round(float(m.group(1)), 1)
                except ValueError:
                    pass

            if out["pcr"] is not None or out["max_pain"] is not None:
                out["source"] = "Quantsapp"
                return out
        except Exception:
            continue

    # ---- 3) niftytrader.in snapshot page (indices only) ----
    if is_index:
        try:
            r = requests.get("https://www.niftytrader.in/nse-option-chain", headers=qa_headers, timeout=8)
            if r.status_code == 200:
                plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text))
                idx = plain.upper().find(nse_symbol if nse_symbol != "NIFTY" else "NIFTY 50")
                chunk = plain[idx: idx + 400] if idx >= 0 else plain
                m = re.search(r"PCR\s*([0-9]+\.?[0-9]*)", chunk, re.I)
                if m:
                    p = float(m.group(1))
                    if 0.05 < p < 10:
                        out["pcr"] = round(p, 3)
                m = re.search(r"MAX\s*PAIN\s*([0-9][0-9,]{1,12})", chunk, re.I)
                if m:
                    # Index max-pain sanity: Nifty ~20k band, BankNifty ~40–60k
                    raw = float(m.group(1).replace(",", ""))
                    if nse_symbol == "NIFTY" and 10000 <= raw <= 40000:
                        out["max_pain"] = int(raw) if raw == int(raw) else round(raw, 1)
                    elif nse_symbol == "BANKNIFTY" and 20000 <= raw <= 80000:
                        out["max_pain"] = int(raw) if raw == int(raw) else round(raw, 1)
                if out["pcr"] is not None:
                    out["source"] = "NiftyTrader"
                    return out
        except Exception:
            pass

    # Final guard: drop max_pain if it fails spot sanity (covers any earlier path)
    if out.get("max_pain") is not None and spot_anchor and spot_anchor > 0:
        if not (spot_anchor * 0.5 <= float(out["max_pain"]) <= spot_anchor * 1.5):
            out["max_pain"] = None

    return out if (out["pcr"] is not None or out["max_pain"] is not None) else None


def get_pcr(symbol: str = "NIFTY"):
    """Backward-compatible PCR-only helper."""
    data = get_option_sentiment(symbol)
    return data.get("pcr") if data else None

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
        return 0, 0

@st.cache_data(ttl=120)
def get_stock_news(symbol: str, limit: int = 4):
    try:
        t = yf.Ticker(f"{symbol}.NS")
        news = t.news
        if not news:
            return []
        items = []
        for n in news[:limit]:
            title = n.get("title") or n.get("content", {}).get("title", "No title")
            link = n.get("link") or n.get("content", {}).get("canonicalUrl", {}).get("url", "")
            items.append({"title": title, "link": link})
        return items
    except Exception:
        return []

@st.cache_data(ttl=60)
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
        return None

# ---------- Most Active (Value / Volume) from NSE ----------
@st.cache_data(ttl=60, show_spinner=False)
def get_most_active(by: str = "value"):
    """Top most-active equities by value or volume from NSE live-analysis endpoint."""
    headers = nse_session_headers()
    # Known NSE endpoints
    endpoints = [
        f"https://www.nseindia.com/api/live-analysis-most-active-securities?index={by}",
        f"https://www.nseindia.com/api/live-analysis-most-active-securities?index={'value' if by == 'value' else 'volume'}",
    ]
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=6)
        session.get("https://www.nseindia.com/market-data/most-active-equities", headers=headers, timeout=6)
        for url in endpoints:
            try:
                r = session.get(url, headers=headers, timeout=8)
                if r.status_code != 200:
                    continue
                data = r.json()
                # Response shapes vary: data / data.list / records
                rows = data.get("data") or data.get("list") or data.get("records") or []
                if isinstance(rows, dict):
                    rows = rows.get("data") or rows.get("list") or []
                if not rows:
                    continue
                out = []
                for item in rows[:12]:
                    sym = item.get("symbol") or item.get("Symbol") or item.get("symbolName")
                    if not sym:
                        continue
                    ltp = item.get("lastPrice") or item.get("ltp") or item.get("lastTradedPrice") or 0
                    chg = item.get("pChange") or item.get("percentChange") or item.get("perChange") or 0
                    vol = item.get("totalTradedVolume") or item.get("volume") or item.get("tradedQuantity") or 0
                    val = item.get("totalTradedValue") or item.get("value") or item.get("tradedValue") or 0
                    # value often in ₹ lakhs or crores; keep raw
                    out.append({
                        "Symbol": str(sym).strip(),
                        "LTP": round(float(ltp), 2) if ltp else 0,
                        "% Chg": round(float(chg), 2) if chg else 0,
                        "Volume": int(float(vol)) if vol else 0,
                        "Value (₹ Lakh)": round(float(val), 2) if val else 0,
                    })
                if out:
                    return pd.DataFrame(out[:10])
            except Exception:
                continue
    except Exception:
        pass
    finally:
        try:
            session.close()
        except Exception:
            pass
    return pd.DataFrame()

# ---------- Nifty 50 Heatmap ----------
@st.cache_data(ttl=90, show_spinner=False)
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
        return pd.DataFrame()

# ---------- Corporate Actions (Nifty 50) ----------
@st.cache_data(ttl=300, show_spinner=False)
def get_corporate_actions(universe: list):
    """Forthcoming corporate actions from NSE for Nifty-50 names."""
    headers = nse_session_headers()
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=6)
        session.get("https://www.nseindia.com/companies-listing/corporate-filings-actions", headers=headers, timeout=6)
        # NSE corporates-corporateActions
        url = "https://www.nseindia.com/api/corporates-corporateActions?index=equities"
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            # alternate
            r = session.get("https://www.nseindia.com/api/corporates-corporateActions", headers=headers, timeout=10)
        if r.status_code != 200:
            return pd.DataFrame()
        data = r.json()
        rows = data if isinstance(data, list) else (data.get("data") or data.get("corporateActions") or [])
        uni_set = set(s.upper() for s in universe)
        out = []
        for item in rows:
            sym = (item.get("symbol") or item.get("Symbol") or item.get("company") or "").strip().upper()
            if not sym or (uni_set and sym not in uni_set):
                continue
            purpose = item.get("purpose") or item.get("subject") or item.get("desc") or item.get("action") or ""
            ex_date = item.get("exDate") or item.get("ex_date") or item.get("exdate") or item.get("recordDate") or ""
            rec_date = item.get("recordDate") or item.get("record_date") or ""
            face = item.get("faceValue") or item.get("face_value") or ""
            out.append({
                "Symbol": sym,
                "Purpose": purpose[:80] if purpose else "—",
                "Ex-Date": ex_date,
                "Record Date": rec_date,
                "Face Value": face,
            })
        if not out:
            return pd.DataFrame()
        df = pd.DataFrame(out).drop_duplicates(subset=["Symbol", "Purpose", "Ex-Date"])
        return df.head(25)
    except Exception:
        return pd.DataFrame()
    finally:
        try:
            session.close()
        except Exception:
            pass

# ---------- Top 5 market-moving business news (30-min cache) ----------
@st.cache_data(ttl=1800, show_spinner=False)
def get_top_business_news():
    """Top headlines that can move global / Indian markets. 30-minute refresh."""
    items = []
    queries = [
        "(Federal+Reserve+OR+US+inflation+OR+Treasury+yields+OR+crude+oil+OR+geopolitics)+when:1d",
        "(India+OR+Nifty+OR+RBI+OR+FII+OR+trade+deal)+when:1d",
        "(China+OR+Japan+OR+Hong+Kong+OR+Asia+markets)+when:1d",
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    seen = set()
    for q in queries:
        try:
            rss = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
            nr = requests.get(rss, headers=headers, timeout=7)
            if not nr.ok:
                continue
            root = ET.fromstring(nr.content)
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                if not title or title in seen:
                    continue
                # Prefer market-relevant keywords
                low = title.lower()
                score = 0
                for kw in ["fed", "rate", "oil", "crude", "treasury", "china", "india", "nifty",
                           "trade", "war", "sanction", "inflation", "gdp", "stimulus", "yen",
                           "dollar", "bitcoin", "gold", "geopolit", "attack", "deal", "rbi"]:
                    if kw in low:
                        score += 1
                if score >= 1:
                    seen.add(title)
                    items.append({"title": title, "link": link, "score": score})
        except Exception:
            continue
    items.sort(key=lambda x: -x["score"])
    return items[:5]

@st.cache_data(ttl=900, show_spinner=False)
def get_china_asia_context():
    """Business-only China & Asia macro headlines (no sports) + short scenario take."""
    pointers = []
    sports_kw = ["cricket", "football", "soccer", "tennis", "nba", "ipl", "match", "tournament",
                 "olympic", "fifa", "premier league", "goal", "score", "series win", "vs "]
    try:
        rss = ("https://news.google.com/rss/search?q="
               "(China+economy+OR+PBOC+OR+stimulus+OR+property+OR+Japan+BOJ+OR+"
               "Hong+Kong+OR+Yuan+OR+Asia+markets+OR+trade+OR+export)+when:2d"
               "&hl=en-IN&gl=IN&ceid=IN:en")
        nr = requests.get(rss, headers={"User-Agent": "Mozilla/5.0"}, timeout=7)
        if nr.ok:
            root = ET.fromstring(nr.content)
            for item in root.findall(".//item"):
                t = (item.findtext("title") or "").strip()
                if not t:
                    continue
                low = t.lower()
                if any(sk in low for sk in sports_kw):
                    continue
                # Prefer business / macro keywords
                score = sum(1 for kw in ["china", "pboc", "stimulus", "property", "yuan", "boj",
                                         "japan", "hong kong", "export", "trade", "gdp", "inflation",
                                         "rate", "liquidity", "equity", "market", "fii"] if kw in low)
                if score >= 1:
                    pointers.append(t)
                if len(pointers) >= 6:
                    break
    except Exception:
        pass
    if not pointers:
        pointers = [
            "Monitor PBOC liquidity & property-sector support signals — still the primary driver of Asia risk appetite.",
            "Japan FX intervention risk remains elevated on sharp USD/JPY moves; can spill into regional equity flows.",
            "Hong Kong / Hang Seng sensitivity to China growth data and US–China trade rhetoric remains high.",
            "FII flows into India often react within 1–2 sessions to sustained Asian risk-on / risk-off swings.",
            "China property and local-gov financing remain the key soft spots for regional risk assets.",
            "Any sustained USD strength or higher US yields typically pressures EM Asia equities including India.",
        ]
    return pointers[:6]


def get_china_asia_deep_take(pointers):
    """Short analytical take based on the current headline set."""
    blob = " ".join(pointers).lower()
    bits = []
    if any(k in blob for k in ["stimulus", "pboc", "liquidity", "easing"]):
        bits.append("Policy support bias in China is visible in the headline flow — constructive for regional risk appetite if delivery follows.")
    if any(k in blob for k in ["property", "real estate", "evergrande", "developer"]):
        bits.append("Property-sector stress remains a drag; watch for transmission into bank balance sheets and consumer confidence.")
    if any(k in blob for k in ["yen", "boj", "intervention", "usd/jpy"]):
        bits.append("Japan FX volatility can quickly reprice Asia equities via carry and risk-parity channels.")
    if any(k in blob for k in ["trade", "tariff", "sanction", "export"]):
        bits.append("Trade/tariff rhetoric still a swing factor for Hang Seng and export-heavy names.")
    if not bits:
        bits.append("Asia risk tone is mixed; India tends to follow with a lag via FII flows and USD/INR.")
    bits.append("For Nifty open: treat GIFT Nifty + Asia closes as the first filter, then confirm with Bank Nifty breadth.")
    return bits


# ---------- Built-up cycle (F&O style, Quantsapp-inspired) ----------
@st.cache_data(ttl=90, show_spinner=False)
def get_fno_builtup(universe: list, top_n: int = 30):
    """
    Approximate Built-up cycle for top F&O stocks.
    Classification (today):
      Long Build-up  = price↑ & volume↑ (proxy for OI↑)
      Short Build-up = price↓ & volume↑
      Short Covering = price↑ & volume↓
      Long Unwinding = price↓ & volume↓
    For prior sessions we use daily price direction vs prior close as a light proxy
    (true multi-day OI matrix requires proprietary / bhavcopy history).
    """
    try:
        # Prefer most-active by value if available, else Nifty weight order
        tickers = [f"{s}.NS" for s in universe[:60]]
        data = yf.download(tickers, period="15d", group_by="ticker", progress=False, threads=True)
        rows = []
        for sym in universe:
            try:
                hist = data if len(universe) == 1 else (data[f"{sym}.NS"] if f"{sym}.NS" in data.columns.get_level_values(0) else None)
                if hist is None or hist.empty or len(hist) < 5:
                    continue
                hist = hist.dropna(subset=["Close"])
                if len(hist) < 5:
                    continue
                closes = hist["Close"]
                vols = hist["Volume"].fillna(0)
                last = float(closes.iloc[-1])
                prev = float(closes.iloc[-2])
                pct = (last - prev) / prev * 100 if prev else 0
                # OI proxy: volume vs 5-day avg volume
                vol_today = float(vols.iloc[-1])
                vol_avg = float(vols.tail(6).iloc[:-1].mean()) if len(vols) >= 6 else vol_today
                oi_up = vol_today >= vol_avg * 0.95  # slight tolerance
                if pct > 0.05 and oi_up:
                    today_bu = "LB"
                elif pct < -0.05 and oi_up:
                    today_bu = "SB"
                elif pct > 0.05 and not oi_up:
                    today_bu = "SC"
                elif pct < -0.05 and not oi_up:
                    today_bu = "LU"
                else:
                    today_bu = "NA"
                # Last ~10 sessions direction cells (newest first after today)
                day_cells = []
                for i in range(2, min(12, len(closes))):
                    c0 = float(closes.iloc[-i])
                    c1 = float(closes.iloc[-i - 1]) if len(closes) > i else c0
                    dlt = (c0 - c1) / c1 * 100 if c1 else 0
                    v0 = float(vols.iloc[-i]) if len(vols) >= i else 0
                    vavg = float(vols.iloc[max(0, -i - 5):-i].mean()) if i + 1 < len(vols) else v0
                    up = v0 >= vavg * 0.95 if vavg else True
                    if dlt > 0.05 and up:
                        day_cells.append("LB")
                    elif dlt < -0.05 and up:
                        day_cells.append("SB")
                    elif dlt > 0.05 and not up:
                        day_cells.append("SC")
                    elif dlt < -0.05 and not up:
                        day_cells.append("LU")
                    else:
                        day_cells.append("NA")
                # Day labels = calendar day of those bars
                day_labels = []
                for i in range(1, min(11, len(hist))):
                    ts = hist.index[-i]
                    try:
                        day_labels.append(str(pd.Timestamp(ts).day))
                    except Exception:
                        day_labels.append(str(i))
                rows.append({
                    "Symbol": sym,
                    "Price%": round(pct, 2),
                    "OI%": round((vol_today / vol_avg - 1) * 100, 1) if vol_avg else 0.0,
                    "Today": today_bu,
                    "Days": day_cells,          # oldest ... newest? we store newest-first after today
                    "DayLabels": day_labels,    # today is first label
                    "LTP": round(last, 2),
                    "Activity": vol_today,
                })
            except Exception:
                continue
        if not rows:
            return pd.DataFrame(), []
        df = pd.DataFrame(rows).sort_values("Activity", ascending=False).head(top_n).reset_index(drop=True)
        # Common day labels from first row
        labels = df.iloc[0]["DayLabels"] if len(df) else []
        return df, labels
    except Exception:
        return pd.DataFrame(), []


PLOTLY_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    "doubleClick": "reset",
    "displaylogo": False,
    "responsive": True
}

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:
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
        chips = " ".join([f'<span class="watchlist-chip">{s}</span>' for s in st.session_state.watchlist])
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.caption("Watchlist is empty")
    st.markdown("---")
    st.caption("Data: TradingView → Investing.com → Yahoo Finance • NSE")

# -------------------------------------------------
# Header + Time
# -------------------------------------------------
ist = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(ist).strftime("%d %b %Y • %H:%M:%S IST")
st.markdown("# 📈 Apex Market Terminal")
st.caption(f"Live Indian Equities & Indices • **{current_time}**")

# ========== MAIN CONTROLS ==========
universe = get_stock_universe()
dropdown_universe = sorted(universe, key=lambda sym: (-NIFTY50_WEIGHT.get(sym, 0.0), sym))
col1, col2, col3 = st.columns([2.2, 1.2, 1])
with col1:
    selected = st.selectbox("🔍 Select Stock (NSE)", options=dropdown_universe, index=0, key="selected")
with col2:
    auto_refresh = st.checkbox("🔄 Auto-refresh every 1 min", value=True)
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.session_state.last_options_refresh = time.time()
        st.rerun()

# ========== STOCK SUMMARY BOX ==========
st.markdown("---")
summary = get_stock_summary_analytics(selected)
news_items = get_stock_news(selected)
stock_sent = get_option_sentiment(selected) or {}
stock_pcr = stock_sent.get("pcr")
stock_mp = stock_sent.get("max_pain")
stock_pcr_src = stock_sent.get("source") or ""

if summary:
    bias_color = "#34d399" if summary["bias"] == "BULLISH" else "#f87171" if summary["bias"] == "BEARISH" else "#fbbf24"
    pcr_html = f"<div><b>PCR (OI):</b> {stock_pcr:.3f}" + (f" <span style='font-size:11px;color:#94a3b8;'>({stock_pcr_src})</span>" if stock_pcr_src else "") + "</div>" if stock_pcr is not None else "<div><b>PCR (OI):</b> —</div>"
    mp_html = f"<div><b>Max Pain:</b> ₹{stock_mp:,.0f}</div>" if stock_mp is not None else "<div><b>Max Pain:</b> —</div>"
    st.markdown(f"""
    <div class="analysis-box">
        <div style="font-size:16px; font-weight:700; margin-bottom:8px;">📌 {selected} • Instant Snapshot</div>
        <div style="display:flex; flex-wrap:wrap; gap:18px; font-size:13px;">
            <div><b>LTP:</b> ₹{summary['current']:,.2f} <span style="color:{'#34d399' if summary['change']>=0 else '#f87171'}">({summary['change']:+.2f} | {summary['pct']:+.2f}%)</span></div>
            <div><b>Day H/L:</b> ₹{summary['day_high']:,.2f} / ₹{summary['day_low']:,.2f}</div>
            <div><b>5D Avg:</b> ₹{summary['avg_5d']:,.2f}</div>
            <div><b>5D High/Low:</b> ₹{summary['high_5d']:,.2f} / ₹{summary['low_5d']:,.2f}</div>
            <div><b>5D VWAP:</b> ₹{summary['vwap_5d']:,.2f} {'✅ Above' if summary['above_vwap'] else '❌ Below'}</div>
            <div><b>Bias:</b> <span style="color:{bias_color}; font-weight:700;">{summary['bias']}</span></div>
            {pcr_html}
            {mp_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if news_items:
        with st.expander(f"📰 Latest News on {selected}", expanded=False):
            for n in news_items:
                if n["link"]:
                    st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    st.markdown(f"- {n['title']}")
else:
    st.info(f"Snapshot for {selected} temporarily unavailable")

st.markdown("---")

# -------------------------------------------------
# Market Indices + Global Instruments
# -------------------------------------------------
st.markdown('<div class="section-header">Market Indices & Global Instruments</div>', unsafe_allow_html=True)

# Display order: India → FX/USD → US futures → yields → commodities → crypto → Asia / Europe
# Tuple: (mode, key, tv_symbols, investing_key, yahoo_ticker)
instruments = {
    "INDIA VIX": ("cash", "^INDIAVIX", (), None, "^INDIAVIX"),
    "GIFT NIFTY 50 FUT": ("gift", "GIFT_NIFTY", ("NSEIX:NIFTY1!", "NSEIX:NIFTY2!"), "GIFT_NIFTY", None),
    "NIFTY 50": ("cash", "^NSEI", (), None, "^NSEI"),
    "BANK NIFTY": ("cash", "^NSEBANK", (), None, "^NSEBANK"),
    "BSE SENSEX": ("cash", "^BSESN", (), None, "^BSESN"),
    "MIDCAP 150": ("cash", "NIFTYMIDCAP150.NS", (), None, "NIFTYMIDCAP150.NS"),
    "MIDCAP SELECT": ("midselect", "MIDCAP_SELECT", ("NSE:NIFTYMIDSELECT",), "MIDCAP_SELECT", None),
    "USD / INR": ("live", "INR=X", ("FX_IDC:USDINR", "OANDA:USDINR"), "INR=X", "INR=X"),
    "DXY (US DOLLAR INDEX)": ("live", "DX-Y.NYB", ("TVC:DXY",), "DX-Y.NYB", "DX-Y.NYB"),
    "US TECH 100 FUT": ("live", "US_TECH_FUT", ("CME_MINI:NQ1!", "CME:NQ1!", "NASDAQ:NDX", "TVC:NDX"), "US_TECH_FUT", "^NDX"),
    "US 30 FUT": ("live", "US_30_FUT", ("CBOT:YM1!", "CME_MINI:YM1!", "DJ:DJI", "TVC:DJI"), "US_30_FUT", "^DJI"),
    "US 10Y BOND": ("live", "^TNX", ("TVC:US10Y",), "^TNX", "^TNX"),
    "US 30Y BOND": ("live", "^TYX", ("TVC:US30Y",), "^TYX", "^TYX"),
    "CRUDE OIL WTI": ("live", "CL=F", ("TVC:USOIL", "NYMEX:CL1!"), "CL=F", "CL=F"),
    "CRUDE OIL BRENT": ("live", "BZ=F", ("TVC:UKOIL", "ICEEUR:BRN1!"), "BZ=F", None),
    "NATURAL GAS": ("live", "NG=F", ("NYMEX:NG1!",), "NG=F", "NG=F"),
    "GOLD": ("live", "GC=F", ("MCX:GOLD1!", "COMEX:GC1!", "TVC:GOLD"), "GC=F", "GC=F"),
    "SILVER": ("live", "SI=F", ("MCX:SILVER1!", "COMEX:SI1!", "TVC:SILVER"), "SI=F", "SI=F"),
    "COPPER": ("live", "HG=F", ("MCX:COPPER1!", "COMEX:HG1!"), "HG=F", "HG=F"),
    "BITCOIN": ("live", "BTC-USD", ("COINBASE:BTCUSD", "BINANCE:BTCUSDT"), "BTC-USD", "BTC-USD"),
    "HANG SENG": ("live", "^HSI", ("HSI:HSI",), "^HSI", "^HSI"),
    "NIKKEI 225": ("live", "^N225", ("TVC:NI225",), "^N225", "^N225"),
    "SHANGHAI COMPOSITE": ("live", "000001.SS", ("SSE:000001",), "000001.SS", "000001.SS"),
    "KOSPI": ("live", "^KS11", ("KRX:KOSPI",), "^KS11", "^KS11"),
    "ASX 200": ("live", "^AXJO", ("ASX:XJO",), "^AXJO", "^AXJO"),
    "TAIWAN TAIEX": ("live", "^TWII", ("TWSE:TAIEX", "TVC:TAIEX"), "^TWII", "^TWII"),
    "FTSE 100 (UK)": ("live", "^FTSE", ("TVC:UKX", "LSE:UKX"), "^FTSE", "^FTSE"),
}

yield_keys = {"US 10Y BOND", "US 30Y BOND"}
vix_keys = {"INDIA VIX"}
items = list(instruments.items())

for i in range(0, len(items), 6):
    row_items = items[i:i + 6]
    cols = st.columns(6)
    for j, (name, meta) in enumerate(row_items):
        mode, key, tv_symbols, inv_key, yahoo_tk = meta
        if mode == "gift":
            data = fetch_gift_nifty_50()
        elif mode == "midselect":
            data = fetch_midcap_select()
        elif mode == "cash":
            data = fetch_index_quote(key)
        else:
            data = fetch_live_instrument(key, tv_symbols, inv_key, yahoo_tk)

        with cols[j]:
            if data:
                sign = "+" if data["change"] >= 0 else ""
                color = "pos" if data["change"] >= 0 else "neg"
                card_cls = "metric-card metric-card-up" if data["change"] >= 0 else "metric-card metric-card-down"
                if name in yield_keys:
                    price_str = f"{data['price']:.2f}%"
                    change_str = f"{sign}{data['change']:.2f}"
                else:
                    if (mode in ("cash", "gift", "midselect")) and name not in vix_keys:
                        price_str = f"₹{data['price']:,.2f}"
                    else:
                        price_str = f"{data['price']:,.2f}"
                    change_str = f"{sign}{data['change']:.2f}"
                # Source prefix + IST refresh / source timestamp (same 7px style as GIFT Nifty)
                # GIFT already builds "M 21 Oct 2026, 11:54:00 IST"; other sources store short + ts separately.
                short = data.get("source_short") or _source_short(data.get("source", ""))
                existing = (data.get("source_time_label") or "").strip()
                if existing and short and existing.upper().startswith(short.upper() + " "):
                    time_label = existing  # already "M 21 Oct ..."
                else:
                    ts = existing or data.get("fetched_at") or _ist_now_label()
                    time_label = f"{short} {ts}" if short else ts
                time_html = (
                    f'<div style="font-size:7px;color:#8a8a8a;text-align:center;'
                    f'margin-top:2px;line-height:1.1;">{time_label}</div>'
                )
                st.markdown(f"""
                <div class="{card_cls}">
                    <div class="index-title">{name}</div>
                    <div class="index-price">{price_str}</div>
                    <div class="index-change {color}">{change_str} ({sign}{data['pct']:.2f}%)</div>
                    {time_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="index-title">{name}</div>
                    <div class="index-price" style="font-size:12px; color:#94a3b8; padding-top:8px;">Unavailable</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# ========== Global Opening Commentary & Analytics ==========
st.markdown('<div class="section-header">🌍 Global Opening Commentary & Index Analytics</div>', unsafe_allow_html=True)

nifty_an = get_index_analytics("^NSEI")
bank_an = get_index_analytics("^NSEBANK")
gift = fetch_gift_nifty_50()

col_n, col_b = st.columns(2)

with col_n:
    if nifty_an:
        bias = "🟢 BUY BIAS" if nifty_an["above_vwap"] and nifty_an["current"] > nifty_an["avg_5d"] else "🔴 SELL BIAS" if not nifty_an["above_vwap"] and nifty_an["current"] < nifty_an["avg_5d"] else "🟡 NEUTRAL"
        st.markdown(f"""
        <div class="analysis-box">
            <b>NIFTY 50 Analytics (Last 5 Days)</b><br>
            Current: <b>₹{nifty_an['current']:,.2f}</b> ({nifty_an['change']:+.2f} | {nifty_an['pct']:+.2f}%)<br>
            Prev Close: ₹{nifty_an['prev_close']:,.2f} | Day H/L: ₹{nifty_an['day_high']:,.2f} / ₹{nifty_an['day_low']:,.2f}<br>
            5D Avg: ₹{nifty_an['avg_5d']:,.2f} | 5D High/Low: ₹{nifty_an['high_5d']:,.2f} / ₹{nifty_an['low_5d']:,.2f}<br>
            5D VWAP: ₹{nifty_an['vwap_5d']:,.2f} → {'✅ Price ABOVE VWAP' if nifty_an['above_vwap'] else '❌ Price BELOW VWAP'}<br>
            <b style="font-size:15px;">{bias}</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Nifty analytics loading...")

with col_b:
    if bank_an:
        bias = "🟢 BUY BIAS" if bank_an["above_vwap"] and bank_an["current"] > bank_an["avg_5d"] else "🔴 SELL BIAS" if not bank_an["above_vwap"] and bank_an["current"] < bank_an["avg_5d"] else "🟡 NEUTRAL"
        st.markdown(f"""
        <div class="analysis-box">
            <b>BANK NIFTY Analytics (Last 5 Days)</b><br>
            Current: <b>₹{bank_an['current']:,.2f}</b> ({bank_an['change']:+.2f} | {bank_an['pct']:+.2f}%)<br>
            Prev Close: ₹{bank_an['prev_close']:,.2f} | Day H/L: ₹{bank_an['day_high']:,.2f} / ₹{bank_an['day_low']:,.2f}<br>
            5D Avg: ₹{bank_an['avg_5d']:,.2f} | 5D High/Low: ₹{bank_an['high_5d']:,.2f} / ₹{bank_an['low_5d']:,.2f}<br>
            5D VWAP: ₹{bank_an['vwap_5d']:,.2f} → {'✅ Price ABOVE VWAP' if bank_an['above_vwap'] else '❌ Price BELOW VWAP'}<br>
            <b style="font-size:15px;">{bias}</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Bank Nifty analytics loading...")

st.markdown("#### 🌏 Global Macro Dashboard — US, China & Asia")

macro_specs = [
    ("US Tech 100 Fut", "US_TECH_FUT", ("CME_MINI:NQ1!", "CME:NQ1!", "NASDAQ:NDX"), "US_TECH_FUT", "^NDX"),
    ("US 30 Fut", "US_30_FUT", ("CBOT:YM1!", "CME_MINI:YM1!", "DJ:DJI"), "US_30_FUT", "^DJI"),
    ("US 10Y yield", "^TNX", ("TVC:US10Y",), "^TNX", "^TNX"),
    ("DXY", "DX-Y.NYB", ("TVC:DXY",), "DX-Y.NYB", "DX-Y.NYB"),
    ("WTI crude", "CL=F", ("TVC:USOIL", "NYMEX:CL1!"), "CL=F", "CL=F"),
    ("Hang Seng", "^HSI", ("HSI:HSI",), "^HSI", "^HSI"),
    ("Nikkei 225", "^N225", ("TVC:NI225",), "^N225", "^N225"),
    ("Shanghai Composite", "000001.SS", ("SSE:000001",), "000001.SS", "000001.SS"),
    ("KOSPI", "^KS11", ("KRX:KOSPI",), "^KS11", "^KS11"),
    ("ASX 200", "^AXJO", ("ASX:XJO",), "^AXJO", "^AXJO"),
]
macro_quotes = {}
for label, key, tv_symbols, inv_key, yahoo_tk in macro_specs:
    macro_quotes[label] = fetch_live_instrument(key, tv_symbols, inv_key, yahoo_tk)

st.markdown(
    '<div style="font-size:0.92rem; font-weight:600; margin-bottom:0.25rem;">Macro pointers</div>',
    unsafe_allow_html=True,
)
macro_lines = []
for label in ["US Tech 100 Fut", "US 30 Fut", "US 10Y yield", "DXY", "WTI crude"]:
    q = macro_quotes.get(label)
    if q:
        macro_lines.append(f"**{label}:** {q['price']:,.2f} ({q['change']:+.2f}, {q['pct']:+.2f}%).")

# Sharper China & Asia analysis (business-only + deep take)
china_asia = get_china_asia_context()
macro_lines.append("**China & Asia (key business drivers):**")
for p in china_asia[:6]:
    macro_lines.append(f"• {p}")
deep = get_china_asia_deep_take(china_asia)
macro_lines.append("**Deep take on current scenario:**")
for d in deep:
    macro_lines.append(f"→ {d}")

if macro_lines:
    for line in macro_lines:
        # Keep the existing content and order, but slightly reduce font size in this section.
        rendered_line = line.replace("**", "")
        if rendered_line.startswith("China & Asia") or rendered_line.startswith("Deep take"):
            st.markdown(
                f'<div style="font-size:0.92rem; font-weight:600; margin-top:0.35rem;">{rendered_line}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="font-size:0.92rem; line-height:1.35; margin-bottom:0.15rem;">{rendered_line}</div>',
                unsafe_allow_html=True,
            )
else:
    st.info("Global macro quotes are temporarily unavailable.")

# Rule-based global bias
score = 0
signals = []
if nifty_an:
    if nifty_an["above_vwap"] and nifty_an["current"] > nifty_an["avg_5d"]:
        score += 2
        signals.append("Nifty above 5-day VWAP and average (+2)")
    elif (not nifty_an["above_vwap"]) and nifty_an["current"] < nifty_an["avg_5d"]:
        score -= 2
        signals.append("Nifty below 5-day VWAP and average (-2)")
if gift and gift.get("pct", 0) != 0:
    score += 1 if gift["pct"] > 0 else -1
    signals.append(f"GIFT Nifty 50 Fut {gift['pct']:+.2f}%")
for label in ["US Tech 100 Fut", "US 30 Fut", "Hang Seng", "Nikkei 225", "Shanghai Composite"]:
    q = macro_quotes.get(label)
    if q and abs(q.get("pct", 0)) >= 0.15:
        score += 1 if q["pct"] > 0 else -1
        signals.append(f"{label} {q['pct']:+.2f}%")
for label, weight in [("DXY", -1), ("WTI crude", -1)]:
    q = macro_quotes.get(label)
    if q and q.get("pct", 0) >= 0.5:
        score += weight
        signals.append(f"{label} rising {q['pct']:+.2f}% (India headwind)")
    elif q and q.get("pct", 0) <= -0.5:
        score -= weight
        signals.append(f"{label} falling {q['pct']:+.2f}% (India tailwind)")
if score >= 2:
    global_bias = "🟢 BUY BIAS"
    bias_explain = "The available technical and global cues lean positive. Prefer confirmation at the open; avoid chasing gaps."
elif score <= -2:
    global_bias = "🔴 SELL BIAS"
    bias_explain = "The available technical and global cues lean negative. Avoid fresh longs until price action improves."
else:
    global_bias = "🟡 NEUTRAL / WAIT"
    bias_explain = "Signals are mixed or insufficient; wait for Nifty/Bank Nifty confirmation rather than forcing a directional trade."
st.markdown(f"### Global Bias for the Day: {global_bias}")
st.write(bias_explain)
if signals:
    st.caption("Bias inputs: " + "; ".join(signals[:8]))
st.caption("Transparent rule-based indicator only — not financial advice. Confirm prices with your broker.")

st.markdown("---")

# ========== Market Breadth + PCR / Max Pain / IV ==========
st.markdown('<div class="section-header">📊 Market Breadth, PCR, Max Pain & IV</div>', unsafe_allow_html=True)

bullish_cnt, bearish_cnt = get_market_breadth(universe)
nifty_sent = get_option_sentiment("NIFTY") or {}
bank_sent = get_option_sentiment("BANKNIFTY") or {}

nifty_pcr = nifty_sent.get("pcr")
bank_pcr = bank_sent.get("pcr")
nifty_mp = nifty_sent.get("max_pain")
bank_mp = bank_sent.get("max_pain")
nifty_iv = nifty_sent.get("atm_iv")
bank_iv = bank_sent.get("atm_iv")

# Persist last successful readings post-market
if nifty_pcr is not None:
    st.session_state["last_nifty_pcr"] = nifty_pcr
    st.session_state["last_pcr_time"] = datetime.now(ist).strftime("%d %b %H:%M IST")
    if nifty_mp is not None:
        st.session_state["last_nifty_mp"] = nifty_mp
    if nifty_iv is not None:
        st.session_state["last_nifty_iv"] = nifty_iv
elif st.session_state.get("last_nifty_pcr") is not None:
    nifty_pcr = st.session_state["last_nifty_pcr"]
    nifty_mp = st.session_state.get("last_nifty_mp", nifty_mp)
    nifty_iv = st.session_state.get("last_nifty_iv", nifty_iv)

if bank_pcr is not None:
    st.session_state["last_bank_pcr"] = bank_pcr
    if bank_mp is not None:
        st.session_state["last_bank_mp"] = bank_mp
    if bank_iv is not None:
        st.session_state["last_bank_iv"] = bank_iv
elif st.session_state.get("last_bank_pcr") is not None:
    bank_pcr = st.session_state["last_bank_pcr"]
    bank_mp = st.session_state.get("last_bank_mp", bank_mp)
    bank_iv = st.session_state.get("last_bank_iv", bank_iv)

pcr_note = ""
if not is_nse_market_hours() and st.session_state.get("last_nifty_pcr") is not None:
    pcr_note = f" (last live value @ {st.session_state.get('last_pcr_time', 'prior session')} — refreshes after 09:15 IST)"

src_n = nifty_sent.get("source") or ("cached" if nifty_pcr is not None else None)
src_b = bank_sent.get("source") or ("cached" if bank_pcr is not None else None)

b1, b2, b3, b4 = st.columns(4)
b1.metric("🟢 Bullish Stocks (Nifty 50)", bullish_cnt)
b2.metric("🔴 Bearish Stocks (Nifty 50)", bearish_cnt)
b3.metric("Nifty PCR (OI)", f"{nifty_pcr:.3f}" if nifty_pcr is not None else "Unavailable")
b4.metric("Bank Nifty PCR (OI)", f"{bank_pcr:.3f}" if bank_pcr is not None else "Unavailable")

# Max Pain + ATM IV row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Nifty Max Pain", f"{nifty_mp:,.0f}" if nifty_mp is not None else "—")
m2.metric("Nifty ATM IV", f"{nifty_iv:.1f}%" if nifty_iv is not None else "—")
m3.metric("Bank Nifty Max Pain", f"{bank_mp:,.0f}" if bank_mp is not None else "—")
m4.metric("Bank Nifty ATM IV", f"{bank_iv:.1f}%" if bank_iv is not None else "—")

st.caption(
    "PCR = total put OI ÷ total call OI. Sources: NSE → Quantsapp → NiftyTrader. "
    "Max Pain = strike where option writers’ payout is lowest. ATM IV from Quantsapp when available. "
    f"Nifty source: {src_n or 'n/a'} · Bank Nifty source: {src_b or 'n/a'}."
    + pcr_note
)

st.markdown("---")

# -------------------------------------------------
# Stock Analytics
# -------------------------------------------------
st.markdown(f'<div class="section-header">📌 {selected} • Live Analytics</div>', unsafe_allow_html=True)
metrics = fetch_stock_data(selected)
if metrics is None:
    st.error(f"Unable to fetch data for {selected}.NS")
    st.stop()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Last Traded Price", f"₹{metrics['ltp']:,.2f}")
m2.metric("Day High", f"₹{metrics['prev_high']:,.2f}")
m3.metric("Day Low", f"₹{metrics['prev_low']:,.2f}")
m4.metric("Previous Close", f"₹{metrics['prev_close']:,.2f}")
v1, v2 = st.columns(2)
v1.metric("Session Volume", f"{metrics['volume']:,}")
v2.metric("20-Day Avg Volume", f"{metrics['avg_volume']:,}")

# -------------------------------------------------
# Charts
# -------------------------------------------------
st.markdown("#### 📊 Price Chart")
tf_col1, tf_col2 = st.columns([2, 1])
with tf_col1:
    timeframe = st.radio("Timeframe", ["Daily", "1 Hour", "30 Minutes"], index=0, horizontal=True)
with tf_col2:
    if timeframe == "Daily":
        period = st.select_slider("Chart Period", ["1mo", "3mo", "6mo", "1y"], value="3mo")
    else:
        period = "1mo" if timeframe == "1 Hour" else "5d"
        st.caption(f"Period: **{period}**")

interval = {"Daily": "1d", "1 Hour": "1h", "30 Minutes": "30m"}[timeframe]
candle_df = get_ohlc_data(selected, interval=interval, period=period)

if candle_df is None or candle_df.empty:
    st.info("Chart data temporarily unavailable")
else:
    if timeframe == "1 Hour":
        candle_df = candle_df.tail(80).reset_index(drop=True)
    elif timeframe == "30 Minutes":
        candle_df = candle_df.tail(100).reset_index(drop=True)
    candle_df["EMA20"] = calculate_ema(candle_df["Close"], 20)
    candle_df["EMA50"] = calculate_ema(candle_df["Close"], 50)
    use_sequential = timeframe in ["1 Hour", "30 Minutes"]
    if use_sequential:
        candle_df["x"] = list(range(len(candle_df)))
        candle_df["hover"] = candle_df["Date"].dt.strftime("%d %b %Y<br>%H:%M")
    else:
        candle_df["x"] = candle_df["Date"]
        candle_df["hover"] = candle_df["Date"].dt.strftime("%d %b %Y")
    is_dark = st.session_state.theme == "dark"
    axis_color = "#e2e8f0" if is_dark else "#1e293b"
    grid_color = "rgba(148,163,184,0.2)" if is_dark else "rgba(100,116,139,0.15)"
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.72, 0.28],
                        subplot_titles=(f"{selected} • {timeframe}", "Volume"))
    fig.add_trace(go.Candlestick(
        x=candle_df["x"], open=candle_df["Open"], high=candle_df["High"],
        low=candle_df["Low"], close=candle_df["Close"], name="OHLC",
        increasing_line_color="#34d399", decreasing_line_color="#f87171",
        increasing_fillcolor="#34d399", decreasing_fillcolor="#f87171",
        text=candle_df["hover"], hoverinfo="text+y"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(x=candle_df["x"], y=candle_df["EMA20"], mode="lines", name="EMA 20",
                             line=dict(color="#fbbf24", width=1.8), hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=candle_df["x"], y=candle_df["EMA50"], mode="lines", name="EMA 50",
                             line=dict(color="#60a5fa", width=2.0), hoverinfo="skip"), row=1, col=1)
    colors = ["#34d399" if c >= o else "#f87171" for o, c in zip(candle_df["Open"], candle_df["Close"])]
    fig.add_trace(go.Bar(x=candle_df["x"], y=candle_df["Volume"], marker_color=colors, name="Volume", opacity=0.7, hoverinfo="skip"), row=2, col=1)
    fig.update_layout(height=580 if use_sequential else 520, xaxis_rangeslider_visible=False,
                      template="plotly_dark" if is_dark else "plotly_white",
                      margin=dict(l=10, r=10, t=40, b=10),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=axis_color)),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=axis_color), dragmode=False)
    if use_sequential:
        n = len(candle_df)
        step = max(1, n // 7)
        tickvals = list(range(0, n, step))
        ticktext = [candle_df["Date"].iloc[i].strftime("%d %b<br>%H:%M") for i in tickvals]
        fig.update_xaxes(type="category", tickmode="array", tickvals=tickvals, ticktext=ticktext,
                         tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)
    else:
        fig.update_xaxes(tickformat="%d %b", tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)
    fig.update_yaxes(tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    # Renko Chart
    st.markdown("#### 🧱 Renko Chart")
    daily_atr_14 = get_daily_atr(selected, 14, 14)
    daily_atr_7 = get_daily_atr(selected, 14, 7)
    if timeframe == "Daily":
        box_size = daily_atr_14 if daily_atr_14 and daily_atr_14 > 0 else metrics["ltp"] * 0.005
        box_label = f"ATR(14) ≈ ₹{box_size:.2f}"
    elif timeframe == "1 Hour":
        base = daily_atr_7 if daily_atr_7 and daily_atr_7 > 0 else (daily_atr_14 or metrics["ltp"] * 0.005)
        box_size = base / 5
        box_label = f"(7-day ATR / 5) ≈ ₹{box_size:.2f}"
    else:
        base = daily_atr_7 if daily_atr_7 and daily_atr_7 > 0 else (daily_atr_14 or metrics["ltp"] * 0.005)
        box_size = (base / 5) / 2
        box_label = f"½ of 1h box ≈ ₹{box_size:.2f}"
    st.caption(f"Renko Box Size: **{box_label}**  |  Timeframe: **{timeframe}**")
    renko_df = generate_renko(candle_df, box_size)
    if renko_df.empty:
        st.info("Not enough price movement to generate Renko bricks.")
    else:
        renko_df["EMA20"] = calculate_ema(renko_df["Close"], 20)
        renko_df["EMA50"] = calculate_ema(renko_df["Close"], 50)
        fig_r = go.Figure()
        fig_r.add_trace(go.Candlestick(
            x=renko_df["Brick"], open=renko_df["Open"], high=renko_df["High"],
            low=renko_df["Low"], close=renko_df["Close"], name="Renko",
            increasing_line_color="#34d399", decreasing_line_color="#f87171",
            increasing_fillcolor="#34d399", decreasing_fillcolor="#f87171"
        ))
        fig_r.add_trace(go.Scatter(x=renko_df["Brick"], y=renko_df["EMA20"], mode="lines", name="EMA 20", line=dict(color="#fbbf24", width=1.5)))
        fig_r.add_trace(go.Scatter(x=renko_df["Brick"], y=renko_df["EMA50"], mode="lines", name="EMA 50", line=dict(color="#60a5fa", width=1.8)))
        fig_r.update_layout(height=420, title=dict(text=f"{selected} Renko • {timeframe}  |  Box ≈ ₹{box_size:.2f}", font=dict(color=axis_color, size=16)),
                            xaxis_title=dict(text="Brick #", font=dict(color=axis_color)),
                            yaxis_title=dict(text="Price (₹)", font=dict(color=axis_color)),
                            xaxis_rangeslider_visible=False, template="plotly_dark" if is_dark else "plotly_white",
                            margin=dict(l=20, r=20, t=50, b=20),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=axis_color)),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=axis_color), dragmode=False)
        fig_r.update_xaxes(tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)
        fig_r.update_yaxes(tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)
        st.plotly_chart(fig_r, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# -------------------------------------------------
# Intraday Renko Signal Scanner
# -------------------------------------------------
st.markdown('<div class="section-header">🎯 Intraday Renko Signals • 1H BUY/Bullish → 1H SELL/Bearish → 30M BUY/Bullish → 30M SELL/Bearish</div>', unsafe_allow_html=True)
st.caption("Only stocks with the latest two Renko bricks in the same direction are listed. BUY/SELL requires close above/below 20 EMA. ⚡ = Just entered (≤ 20 min). Order: 1H BUY → 1H BULLISH → 1H SELL → 1H BEARISH → 30M same. Within each group sorted by Age Minutes — newest (lowest age) on top.")

scan_col1, scan_col2 = st.columns([1, 4])
with scan_col1:
    if st.button("🔄 Scan All Stocks", use_container_width=True):
        scan_renko_universe.clear()
        st.cache_data.clear()
        st.rerun()
with scan_col2:
    st.caption(f"Scanning {len(universe)} Nifty 50 stocks across 30-minute and 1-hour timeframes.")

with st.spinner("Scanning Renko bricks… first scan may take a little time."):
    signal_df = scan_renko_universe(tuple(universe))

if signal_df.empty:
    st.info("No stocks currently meet the two-consecutive-brick criteria, or intraday data is unavailable.")
else:
    buy_df = signal_df[signal_df["Signal"] == "BUY"]
    bullish_df = signal_df[signal_df["Signal"] == "BULLISH"]
    sell_df = signal_df[signal_df["Signal"] == "SELL"]
    bearish_df = signal_df[signal_df["Signal"] == "BEARISH"]
    just_entered_count = int(signal_df["Just Entered"].sum())
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    sc1.metric("BUY", len(buy_df))
    sc2.metric("BULLISH", len(bullish_df))
    sc3.metric("SELL", len(sell_df))
    sc4.metric("BEARISH", len(bearish_df))
    sc5.metric("⚡ Just Entered", just_entered_count)

    display_df = signal_df.copy()

    def format_signal(row):
        base = {"BUY": "🟢 BUY", "BULLISH": "🟩 BULLISH", "SELL": "🔴 SELL", "BEARISH": "🟥 BEARISH"}.get(row["Signal"], row["Signal"])
        return f"⚡{base}" if row["Just Entered"] else base

    display_df["Signal"] = display_df.apply(format_signal, axis=1)

    def highlight_just_entered(row):
        if row.get("Just Entered", False):
            return ["background-color: #fef08a; color: #000; font-weight: 600"] * len(row)
        return [""] * len(row)

    cols_to_show = ["Stock", "Timeframe", "Signal", "Price", "EMA 20", "Entry", "Exit", "Box Size", "Last Brick Time", "Age Minutes"]
    for col in ["Price", "EMA 20", "Entry", "Exit", "Box Size"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: round(float(x), 2) if pd.notnull(x) else x)

    styled = display_df[cols_to_show].style.apply(highlight_just_entered, axis=1).format({
        "Price": "{:.2f}", "EMA 20": "{:.2f}", "Entry": "{:.2f}", "Exit": "{:.2f}", "Box Size": "{:.2f}", "Age Minutes": "{:.1f}"
    })
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption("⚡ = Just entered (last Renko brick ≤ 20 min ago) • Yellow highlight = fresh signal")
    st.download_button("⬇️ Download signal list (CSV)",
                       data=signal_df.drop(columns=["Last Brick TS"], errors="ignore").to_csv(index=False).encode("utf-8"),
                       file_name="intraday_renko_signals.csv", mime="text/csv")

st.markdown("---")

# -------------------------------------------------
# Options
# -------------------------------------------------
st.markdown('<div class="section-header">⚡ Options Strike Matrix (ATM ±2)</div>', unsafe_allow_html=True)
st.caption(f"Spot: **₹{metrics['ltp']:,.2f}** • Source: NSE Option Chain (nearest expiry) • Auto-refreshes every 30 seconds")

options_df = get_options_chain(metrics["ltp"], selected)

def highlight_atm(row):
    if row.name == 2:
        if st.session_state.theme == "dark":
            return ["background-color: #312e81; color: #e0e7ff; font-weight: 600"] * len(row)
        else:
            return ["background-color: #e0e7ff; color: #312e81; font-weight: 600"] * len(row)
    return [""] * len(row)

styled = options_df.style.format({
    "Call Price (CE)": "₹{:,.2f}",
    "Strike Price": "₹{:,.0f}",
    "Put Price (PE)": "₹{:,.2f}"
}).apply(highlight_atm, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)

if time.time() - st.session_state.last_options_refresh > 30:
    get_options_chain.clear()
    st.session_state.last_options_refresh = time.time()
    st.rerun()

st.markdown("---")

# -------------------------------------------------
# Gainers / Losers
# -------------------------------------------------
st.markdown('<div class="section-header">🏆 Top Gainers & Losers</div>', unsafe_allow_html=True)
gainers, losers = get_top_movers(universe)
gcol, lcol = st.columns(2)
with gcol:
    st.markdown("##### 🟢 Top Gainers")
    if gainers is not None and not gainers.empty:
        st.dataframe(gainers.style.format({"LTP": "₹{:,.2f}", "Change": "{:+.2f}", "% Chg": "{:+.2f}%"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Loading...")
with lcol:
    st.markdown("##### 🔴 Top Losers")
    if losers is not None and not losers.empty:
        st.dataframe(losers.style.format({"LTP": "₹{:,.2f}", "Change": "{:+.2f}", "% Chg": "{:+.2f}%"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Loading...")

st.markdown("---")

# -------------------------------------------------
# Most Active — Value & Volume (NSE, all stocks)
# -------------------------------------------------
st.markdown('<div class="section-header">🔥 Most Active Stocks (NSE — All Equities)</div>', unsafe_allow_html=True)
st.caption("Top 10 by traded value and by volume. Source: NSE India live-analysis. Not limited to Nifty 50.")

ma_val = get_most_active("value")
ma_vol = get_most_active("volume")

mac1, mac2 = st.columns(2)
with mac1:
    st.markdown("##### 💰 Most Active by Value")
    if not ma_val.empty:
        st.dataframe(
            ma_val.style.format({"LTP": "₹{:,.2f}", "% Chg": "{:+.2f}%", "Volume": "{:,.0f}", "Value (₹ Lakh)": "{:,.2f}"}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Most-active value list temporarily unavailable (NSE throttle or off-hours).")
with mac2:
    st.markdown("##### 📦 Most Active by Volume")
    if not ma_vol.empty:
        st.dataframe(
            ma_vol.style.format({"LTP": "₹{:,.2f}", "% Chg": "{:+.2f}%", "Volume": "{:,.0f}", "Value (₹ Lakh)": "{:,.2f}"}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Most-active volume list temporarily unavailable (NSE throttle or off-hours).")

st.markdown("---")

# -------------------------------------------------
# Nifty 50 Heatmap
# -------------------------------------------------
st.markdown('<div class="section-header">🗺️ Nifty 50 Heatmap</div>', unsafe_allow_html=True)
st.caption("Colour intensity = day % change. Green = up, Red = down.")

heat_df = get_nifty50_heatmap(universe)
if heat_df.empty:
    st.info("Heatmap data temporarily unavailable.")
else:
    heat_df = heat_df.sort_values("% Chg", ascending=False)
    html_cells = []
    for _, row in heat_df.iterrows():
        pct = row["% Chg"]
        # colour scale
        if pct >= 2:
            bg = "#059669"
        elif pct >= 1:
            bg = "#10b981"
        elif pct >= 0.3:
            bg = "#34d399"
        elif pct > -0.3:
            bg = "#64748b"
        elif pct > -1:
            bg = "#f87171"
        elif pct > -2:
            bg = "#ef4444"
        else:
            bg = "#b91c1c"
        html_cells.append(
            f'<div class="heat-cell" style="background:{bg};">'
            f'{row["Symbol"]}<br>{pct:+.2f}%<br>₹{row["LTP"]:,.1f}</div>'
        )
    st.markdown("".join(html_cells), unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------
# Built-up Cycle · Most Active F&O Stocks (Quantsapp-style)
# -------------------------------------------------
st.markdown('<div class="section-header">🧱 Built-up Cycle · Most Active F&O Stocks</div>', unsafe_allow_html=True)
st.caption("Colour legend: 🟢 Long build-up · 🔴 Short build-up · 🔵 Short covering · 🟡 Long unwinding. "
           "Today = price% + volume-vs-avg proxy for OI%. Prior days use daily price/volume direction. "
           "Inspired by Quantsapp Built-up cycle. Refreshes with the main Refresh button.")

bu_df, bu_labels = get_fno_builtup(universe, top_n=30)
if bu_df.empty:
    st.info("Built-up data temporarily unavailable (Yahoo/NSE throttle or off-hours).")
else:
    # Header row of day numbers
    day_hdr = "".join(f"<th>{d}</th>" for d in bu_labels)
    rows_html = []
    for _, r in bu_df.iterrows():
        pct_s = f"{r['Price%']:+.2f}%"
        oi_s = f"{r['OI%']:+.1f}%"
        cells = ""
        # Today first
        code = r["Today"]
        cls = {"LB": "bu-lb", "SB": "bu-sb", "SC": "bu-sc", "LU": "bu-lu"}.get(code, "bu-na")
        cells += f'<td><span class="bu-cell {cls}" title="Today {code}"></span></td>'
        for code in r["Days"]:
            cls = {"LB": "bu-lb", "SB": "bu-sb", "SC": "bu-sc", "LU": "bu-lu"}.get(code, "bu-na")
            cells += f'<td><span class="bu-cell {cls}" title="{code}"></span></td>'
        # Pad if shorter
        extra = max(0, len(bu_labels) - 1 - len(r["Days"]))
        cells += '<td><span class="bu-cell bu-na"></span></td>' * extra
        rows_html.append(
            f'<tr><td style="text-align:left;font-weight:600;color:#e2e8f0;">{r["Symbol"]}<br>'
            f'<span style="font-size:10px;color:#94a3b8;">{pct_s} · {oi_s}</span></td>{cells}</tr>'
        )
    table = f'''
    <div class="builtup-wrap">
    <table class="builtup-table">
      <thead><tr><th style="text-align:left;">SYMBOL</th>{day_hdr}</tr></thead>
      <tbody>{"".join(rows_html)}</tbody>
    </table>
    <div style="margin-top:8px;font-size:11px;color:#94a3b8;">
      <span class="bu-cell bu-lb"></span> Long build-up &nbsp;
      <span class="bu-cell bu-sb"></span> Short build-up &nbsp;
      <span class="bu-cell bu-sc"></span> Short covering &nbsp;
      <span class="bu-cell bu-lu"></span> Long unwinding &nbsp;
      &nbsp; Price% · OI% (vol proxy) today
    </div>
    </div>
    '''
    st.markdown(table, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------
# Corporate Actions (Nifty 50)
# -------------------------------------------------
st.markdown('<div class="section-header">📋 Corporate Actions — Nifty 50</div>', unsafe_allow_html=True)
st.caption("Forthcoming dividends, bonuses, splits, rights etc. Source: NSE corporate filings.")

ca_df = get_corporate_actions(universe)
if ca_df.empty:
    st.info("No upcoming corporate actions found for Nifty 50 names, or NSE endpoint temporarily blocked.")
else:
    # High-visibility box
    ca_html = '<div class="ca-box">'
    for _, row in ca_df.iterrows():
        ca_html += (f'<div style="margin-bottom:6px;"><b>{row.get("Symbol","")}</b> — {row.get("Purpose","—")} '
                    f'| Ex: {row.get("Ex-Date","—")} | Record: {row.get("Record Date","—")}</div>')
    ca_html += "</div>"
    st.markdown(ca_html, unsafe_allow_html=True)
    with st.expander("Full table"):
        st.dataframe(ca_df, use_container_width=True, hide_index=True)

st.markdown("---")

# -------------------------------------------------
# Top 5 Business News (30-min refresh)
# -------------------------------------------------
st.markdown('<div class="section-header">📰 Top 5 Market-Moving Business News</div>', unsafe_allow_html=True)
st.caption("Global + India headlines that can influence equity, FX, rates or commodity markets. Auto-refreshes every 30 minutes.")

biz_news = get_top_business_news()
if not biz_news:
    st.info("News feed temporarily unavailable.")
else:
    news_html = '<div class="news-box">'
    for i, n in enumerate(biz_news, 1):
        if n.get("link"):
            news_html += f'<div style="margin-bottom:8px;"><b>{i}.</b> <a href="{n["link"]}" target="_blank">{n["title"]}</a></div>'
        else:
            news_html += f'<div style="margin-bottom:8px;"><b>{i}.</b> {n["title"]}</div>'
    news_html += "</div>"
    st.markdown(news_html, unsafe_allow_html=True)

# Auto refresh
if auto_refresh:
    time.sleep(60)
    st.rerun()
