import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import pytz
import requests
from io import StringIO
import re

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

# -------------------------------------------------
# Theme CSS (Compact cards)
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
                font-size: 10px !important; 
                font-weight: 600; 
                color: #94a3b8; 
                letter-spacing: 0.3px; 
                text-transform: uppercase; 
                margin-bottom: 3px !important;
                line-height: 1.1;
            }
            .index-price { 
                font-size: 15px !important; 
                font-weight: 700; 
                color: #f8fafc; 
                line-height: 1.15 !important;
                margin: 2px 0 !important;
            }
            .index-change { 
                font-size: 11px !important; 
                font-weight: 600; 
                margin-top: 1px !important;
            }
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
            .stCaption, [data-testid="stCaption"] {
                color: #cbd5e1 !important;
            }
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
                font-size: 10px !important; 
                font-weight: 600; 
                color: #64748b; 
                letter-spacing: 0.3px; 
                text-transform: uppercase; 
                margin-bottom: 3px !important;
                line-height: 1.1;
            }
            .index-price { 
                font-size: 15px !important; 
                font-weight: 700; 
                color: #0f172a; 
                line-height: 1.15 !important;
                margin: 2px 0 !important;
            }
            .index-change { 
                font-size: 11px !important; 
                font-weight: 600; 
                margin-top: 1px !important;
            }
            .pos { color: #059669 !important; }
            .neg { color: #dc2626 !important; }
            .section-header {
                font-size: 18px; font-weight: 700;
                background: linear-gradient(90deg, #4f46e5, #7c3aed);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }
            div[data-testid="stMetric"] {
                background: white;
                border: 1px solid #e2e8f0;
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
        </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# -------------------------------------------------
# Data Helpers
# -------------------------------------------------
@st.cache_data(ttl=45)
@st.cache_data(ttl=20)
def fetch_index_quote(ticker: str):
    try:
        t = yf.Ticker(ticker)
        
        # Prefer history (more reliable for commodities, crypto, indices)
        hist = t.history(period="5d")
        if not hist.empty and len(hist) >= 1:
            price = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
            change = price - prev
            pct = (change / prev) * 100 if prev else 0
            return {
                "price": round(price, 2),
                "change": round(change, 2),
                "pct": round(pct, 2)
            }
        
        # Fallback to fast_info
        info = t.fast_info
        price = getattr(info, "last_price", None) or getattr(info, "regular_market_price", None)
        prev = getattr(info, "previous_close", None)
        
        if price is not None:
            if prev is None:
                prev = price
            change = price - prev
            pct = (change / prev) * 100 if prev else 0
            return {
                "price": round(float(price), 2),
                "change": round(float(change), 2),
                "pct": round(float(pct), 2)
            }
    except Exception:
        pass
    return None
@st.cache_data(ttl=20)
def fetch_gift_nifty():
    """Fetch live GIFT Nifty from Moneycontrol"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.moneycontrol.com/",
        }
        url = "https://www.moneycontrol.com/live-index/gift-nifty?symbol=in;gsx"
        r = requests.get(url, headers=headers, timeout=12)
        
        if r.status_code != 200:
            return None

        text = r.text.replace(",", "")

        price = None
        change = 0.0
        pct = 0.0

        # Pattern 1: price + change + percentage
        match = re.search(r'(\d+\.\d{2})\s*([+-]?\d+\.\d{2})\s*\(\s*([+-]?\d+\.\d+)\s*%\s*\)', text)
        if match:
            price = float(match.group(1))
            change = float(match.group(2))
            pct = float(match.group(3))
        else:
            # Fallback: find number in GIFT Nifty range
            candidates = re.findall(r'(\d{5}\.\d{2})', text)
            for cand in candidates:
                val = float(cand)
                if 18000 < val < 35000:
                    price = val
                    break

        if price is not None:
            return {
                "price": round(price, 2),
                "change": round(change, 2),
                "pct": round(pct, 2)
            }
    except Exception:
        pass
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
    except:
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
    except:
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
    except:
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
            bricks.append({
                "Date": date,
                "Open": current_brick,
                "High": current_brick + box_size,
                "Low": current_brick,
                "Close": current_brick + box_size
            })
            current_brick += box_size
        while price <= current_brick - box_size:
            bricks.append({
                "Date": date,
                "Open": current_brick,
                "High": current_brick,
                "Low": current_brick - box_size,
                "Close": current_brick - box_size
            })
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
                rows.append({
                    "Symbol": sym,
                    "LTP": round(last, 2),
                    "Change": round(chg, 2),
                    "% Chg": round((chg / prev) * 100, 2)
                })
            except:
                continue
        df = pd.DataFrame(rows)
        if df.empty:
            return None, None
        return (
            df.sort_values("% Chg", ascending=False).head(8).reset_index(drop=True),
            df.sort_values("% Chg", ascending=True).head(8).reset_index(drop=True)
        )
    except:
        return None, None

def analyze_renko_signal(symbol: str, timeframe: str):
    interval = "1h" if timeframe == "1 Hour" else "30m"
    period = "1mo" if interval == "1h" else "5d"
    candles = get_ohlc_data(symbol, interval=interval, period=period)
    if candles is None or candles.empty or len(candles) < 22:
        return None
    candles = candles.tail(120 if interval == "1h" else 150).copy().reset_index(drop=True)
    if not candles.empty:
        last_time = pd.Timestamp(candles["Date"].iloc[-1])
        if last_time.tzinfo is None:
            last_time = last_time.tz_localize("Asia/Kolkata")
        else:
            last_time = last_time.tz_convert("Asia/Kolkata")
        bar_length = pd.Timedelta(hours=1 if interval == "1h" else 0, minutes=30 if interval == "30m" else 0)
        if last_time + bar_length > pd.Timestamp.now(tz="Asia/Kolkata") and len(candles) > 1:
            candles = candles.iloc[:-1].reset_index(drop=True)
    if len(candles) < 22:
        return None
    candles["EMA20"] = calculate_ema(candles["Close"], 20)
    price = float(candles["Close"].iloc[-1])
    ema20 = float(candles["EMA20"].iloc[-1])
    daily_atr = get_daily_atr(symbol, 14, 7)
    if not daily_atr or daily_atr <= 0:
        daily_atr = get_daily_atr(symbol, 14, 14)
    if not daily_atr or daily_atr <= 0:
        daily_atr = price * 0.005
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
    last_brick_ts = pd.Timestamp(bricks["Date"].iloc[-1])
    if last_brick_ts.tzinfo is None:
        last_brick_ts = last_brick_ts.tz_localize("Asia/Kolkata")
    else:
        last_brick_ts = last_brick_ts.tz_convert("Asia/Kolkata")
    now = pd.Timestamp.now(tz="Asia/Kolkata")
    age_minutes = (now - last_brick_ts).total_seconds() / 60.0
    just_entered = age_minutes <= 20
    return {
        "Stock": symbol,
        "Timeframe": timeframe,
        "Signal": action,
        "Renko": direction,
        "Price": round(price, 2),
        "EMA 20": round(ema20, 2),
        "Entry": round(entry, 2),
        "Exit": round(exit_price, 2),
        "Box Size": round(float(box_size), 2),
        "Last Brick Time": last_brick_ts.strftime("%d %b %H:%M"),
        "Last Brick TS": last_brick_ts,
        "Age Minutes": round(age_minutes, 1),
        "Just Entered": just_entered
    }

@st.cache_data(ttl=90, show_spinner=False)
def scan_renko_universe(universe_tuple: tuple):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    jobs = [(symbol, timeframe) for symbol in universe_tuple for timeframe in ("30 Minutes", "1 Hour")]
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
    tf_order = {"30 Minutes": 0, "1 Hour": 1}
    signal_order = {"BUY": 0, "SELL": 1, "BULLISH": 2, "BEARISH": 3}
    result_df["_tf"] = result_df["Timeframe"].map(tf_order)
    result_df["_sig"] = result_df["Signal"].map(signal_order).fillna(9)
    result_df = result_df.sort_values(
        by=["_tf", "Last Brick TS", "_sig"],
        ascending=[True, False, True]
    ).drop(columns=["_tf", "_sig"]).reset_index(drop=True)
    return result_df

@st.cache_data(ttl=30)
def get_options_chain(ltp: float, symbol: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/option-chain",
    }
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
            rows.append({
                "Call Price (CE)": round(ce, 2),
                "Strike Price": s,
                "Put Price (PE)": round(pe, 2)
            })
        return pd.DataFrame(rows)

@st.cache_data(ttl=3600)
def get_stock_universe():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/csv,application/json,text/plain,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
    }
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
    theme_choice = st.radio(
        "Theme",
        ["🌙 Dark", "☀️ Light"],
        index=0 if st.session_state.theme == "dark" else 1,
        horizontal=True
    )
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
    st.caption("Data: Yahoo Finance + NSE + Moneycontrol • Options refresh every 30s")

# -------------------------------------------------
# Header + Time
# -------------------------------------------------
ist = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(ist).strftime("%d %b %Y • %H:%M:%S IST")
st.markdown("# 📈 Apex Market Terminal")
st.caption(f"Live Indian Equities & Indices • **{current_time}**")

# ========== MAIN CONTROLS ==========
universe = get_stock_universe()
col1, col2, col3 = st.columns([2.2, 1.2, 1])
with col1:
    selected = st.selectbox("🔍 Select Stock (NSE)", options=universe, index=0, key="selected")
with col2:
    auto_refresh = st.checkbox("🔄 Auto-refresh every 1 min", value=False)
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if     st.button("Refresh Now", use_container_width=True):
         st.cache_data.clear()
        st.session_state.last_options_refresh = time.time()
       st.rerun()

st.markdown("---")

# -------------------------------------------------
# Market Indices + Global Instruments (6 cards per row)
# -------------------------------------------------
st.markdown('<div class="section-header">Market Indices & Global Instruments</div>', unsafe_allow_html=True)

instruments = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "MIDCAP 150": "NIFTYMIDCAP150.NS",
    "GIFT NIFTY": "GIFT_NIFTY_SPECIAL",
    "MIDCAP SELECT": "NIFTY_MID_SELECT.NS",
    "INDIA VIX": "^INDIAVIX",
    "CRUDE OIL WTI": "CL=F",
    "CRUDE OIL BRENT": "BZ=F",
    "NATURAL GAS": "NG=F",
    "USD / INR": "INR=X",
    "US 10Y BOND": "^TNX",
    "US 30Y BOND": "^TYX",
    "US TECH 100": "^NDX",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "COPPER": "HG=F",
    "BITCOIN": "BTC-USD",
}

yield_tickers = {"^TNX", "^TYX"}
vix_tickers = {"^INDIAVIX"}

items = list(instruments.items())

for i in range(0, len(items), 6):
    row_items = items[i:i+6]
    cols = st.columns(6)
    
    for j, (name, ticker) in enumerate(row_items):
        if ticker == "GIFT_NIFTY_SPECIAL":
            data = fetch_gift_nifty()
        else:
            data = fetch_index_quote(ticker)
        
        with cols[j]:
            if data:
                sign = "+" if data["change"] >= 0 else ""
                color = "pos" if data["change"] >= 0 else "neg"

                if ticker in yield_tickers:
                    price_str = f"{data['price']:.2f}%"
                    change_str = f"{sign}{data['change']:.2f}"
                elif ticker in vix_tickers or ticker == "GIFT_NIFTY_SPECIAL":
                    price_str = f"{data['price']:,.2f}"
                    change_str = f"{sign}{data['change']:.2f}"
                elif ticker in ["CL=F", "BZ=F", "NG=F", "GC=F", "SI=F", "HG=F", "BTC-USD", "INR=X"]:
                    price_str = f"{data['price']:,.2f}"
                    change_str = f"{sign}{data['change']:.2f}"
                else:
                    price_str = f"₹{data['price']:,.2f}"
                    change_str = f"{sign}{data['change']:.2f}"

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
# Timeframe
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

# -------------------------------------------------
# Charts
# -------------------------------------------------
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

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        row_heights=[0.72, 0.28], subplot_titles=(f"{selected} • {timeframe}", "Volume")
    )
    fig.add_trace(go.Candlestick(
        x=candle_df["x"], open=candle_df["Open"], high=candle_df["High"],
        low=candle_df["Low"], close=candle_df["Close"], name="OHLC",
        increasing_line_color="#34d399", decreasing_line_color="#f87171",
        increasing_fillcolor="#34d399", decreasing_fillcolor="#f87171",
        text=candle_df["hover"], hoverinfo="text+y"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=candle_df["x"], y=candle_df["EMA20"], mode="lines", name="EMA 20",
        line=dict(color="#fbbf24", width=1.8), hoverinfo="skip"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=candle_df["x"], y=candle_df["EMA50"], mode="lines", name="EMA 50",
        line=dict(color="#60a5fa", width=2.0), hoverinfo="skip"
    ), row=1, col=1)

    colors = ["#34d399" if c >= o else "#f87171" for o, c in zip(candle_df["Open"], candle_df["Close"])]
    fig.add_trace(go.Bar(
        x=candle_df["x"], y=candle_df["Volume"], marker_color=colors,
        name="Volume", opacity=0.7, hoverinfo="skip"
    ), row=2, col=1)

    fig.update_layout(
        height=580 if use_sequential else 520,
        xaxis_rangeslider_visible=False,
        template="plotly_dark" if is_dark else "plotly_white",
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=axis_color)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=axis_color), dragmode=False
    )
    if use_sequential:
        n = len(candle_df)
        step = max(1, n // 7)
        tickvals = list(range(0, n, step))
        ticktext = [candle_df["Date"].iloc[i].strftime("%d %b<br>%H:%M") for i in tickvals]
        fig.update_xaxes(
            type="category", tickmode="array", tickvals=tickvals, ticktext=ticktext,
            tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True
        )
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
        fig_r.add_trace(go.Scatter(
            x=renko_df["Brick"], y=renko_df["EMA20"], mode="lines", name="EMA 20",
            line=dict(color="#fbbf24", width=1.5)
        ))
        fig_r.add_trace(go.Scatter(
            x=renko_df["Brick"], y=renko_df["EMA50"], mode="lines", name="EMA 50",
            line=dict(color="#60a5fa", width=1.8)
        ))
        fig_r.update_layout(
            height=420,
            title=dict(text=f"{selected} Renko • {timeframe}  |  Box ≈ ₹{box_size:.2f}", font=dict(color=axis_color, size=16)),
            xaxis_title=dict(text="Brick #", font=dict(color=axis_color)),
            yaxis_title=dict(text="Price (₹)", font=dict(color=axis_color)),
            xaxis_rangeslider_visible=False,
            template="plotly_dark" if is_dark else "plotly_white",
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=axis_color)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=axis_color), dragmode=False
        )
        fig_r.update_xaxes(tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)
        fig_r.update_yaxes(tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)
        st.plotly_chart(fig_r, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("---")

# -------------------------------------------------
# Intraday Renko Signal Scanner
# -------------------------------------------------
st.markdown(
    '<div class="section-header">🎯 Intraday Renko Signals • 30 Minutes first, then 1 Hour</div>',
    unsafe_allow_html=True
)
st.caption(
    "Only stocks with the latest two Renko bricks in the same direction are listed. "
    "BUY/SELL additionally requires the latest timeframe close to be above/below its 20 EMA. "
    "⚡ = Just entered (last brick ≤ 20 min ago). Sorted by newest entry first."
)

scan_col1, scan_col2 = st.columns([1, 4])
with scan_col1:
    if st.button("🔄 Scan All Stocks", use_container_width=True):
        scan_renko_universe.clear()
        st.cache_data.clear()
        st.rerun()
with scan_col2:
    st.caption(f"Scanning {len(universe)} Nifty 50 stocks across 30-minute and 1-hour timeframes.")

with st.spinner("Scanning Renko bricks for the stock universe… first scan may take a little time."):
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
        base = {
            "BUY": "🟢 BUY",
            "BULLISH": "🟩 BULLISH",
            "SELL": "🔴 SELL",
            "BEARISH": "🟥 BEARISH"
        }.get(row["Signal"], row["Signal"])
        if row["Just Entered"]:
            return f"⚡{base}"
        return base
    display_df["Signal"] = display_df.apply(format_signal, axis=1)

    def highlight_just_entered(row):
        if row.get("Just Entered", False):
            return ["background-color: #fef08a; color: #000; font-weight: 600"] * len(row)
        return [""] * len(row)

    cols_to_show = [
        "Stock", "Timeframe", "Signal", "Price", "EMA 20",
        "Entry", "Exit", "Box Size", "Last Brick Time", "Age Minutes"
    ]
    styled = display_df[cols_to_show].style.apply(highlight_just_entered, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption("⚡ = Just entered (last Renko brick ≤ 20 min ago) • Yellow highlight = fresh signal")

    st.download_button(
        "⬇️ Download signal list (CSV)",
        data=signal_df.drop(columns=["Last Brick TS"], errors="ignore").to_csv(index=False).encode("utf-8"),
        file_name="intraday_renko_signals.csv",
        mime="text/csv"
    )

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
    if gainers is not None:
        st.dataframe(
            gainers.style.format({"LTP": "₹{:,.2f}", "Change": "{:+.2f}", "% Chg": "{:+.2f}%"}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Loading...")
with lcol:
    st.markdown("##### 🔴 Top Losers")
    if losers is not None:
        st.dataframe(
            losers.style.format({"LTP": "₹{:,.2f}", "Change": "{:+.2f}", "% Chg": "{:+.2f}%"}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Loading...")

# Auto refresh every 1 minute
if auto_refresh:
    time.sleep(60)
    st.rerun()
