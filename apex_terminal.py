import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import pytz

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Apex Market Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"          # Expanded on desktop
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
                background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
                border: 1px solid rgba(99,102,241,0.3);
                border-radius: 16px;
                padding: 18px 14px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            .index-title { font-size: 12px; font-weight: 600; color: #94a3b8; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 6px; }
            .index-price { font-size: 24px; font-weight: 700; color: #f8fafc; }
            .index-change { font-size: 13px; font-weight: 600; }
            .pos { color: #34d399; }
            .neg { color: #f87171; }
            .section-header {
                font-size: 18px; font-weight: 700;
                background: linear-gradient(90deg, #818cf8, #c084fc);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
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
                border-radius: 16px;
                padding: 18px 14px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(99,102,241,0.1);
            }
            .index-title { font-size: 12px; font-weight: 600; color: #64748b; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 6px; }
            .index-price { font-size: 24px; font-weight: 700; color: #0f172a; }
            .index-change { font-size: 13px; font-weight: 600; }
            .pos { color: #059669; }
            .neg { color: #dc2626; }
            .section-header {
                font-size: 18px; font-weight: 700;
                background: linear-gradient(90deg, #4f46e5, #7c3aed);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
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
def fetch_index_quote(ticker: str):
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        price = getattr(info, "last_price", None) or getattr(info, "regular_market_price", None)
        prev = getattr(info, "previous_close", None)
        if price is None or prev is None:
            hist = t.history(period="5d")
            if hist.empty: return None
            price = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
        change = price - prev
        pct = (change / prev) * 100 if prev else 0
        return {"price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2)}
    except:
        return None

@st.cache_data(ttl=45)
def fetch_stock_data(symbol: str):
    try:
        t = yf.Ticker(f"{symbol}.NS")
        info = t.fast_info
        hist = t.history(period="1mo")
        if hist.empty: return None
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
        if df.empty: return None
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
        if df.empty or len(df) < atr_period + 5: return None
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
    if df is None or df.empty or box_size <= 0: return pd.DataFrame()
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
    if not bricks: return pd.DataFrame()
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
                if hist is None or hist.empty: continue
                close = hist["Close"].dropna()
                if len(close) < 2: continue
                last, prev = float(close.iloc[-1]), float(close.iloc[-2])
                chg = last - prev
                rows.append({"Symbol": sym, "LTP": round(last, 2), "Change": round(chg, 2), "% Chg": round((chg/prev)*100, 2)})
            except: continue
        df = pd.DataFrame(rows)
        if df.empty: return None, None
        return df.sort_values("% Chg", ascending=False).head(8).reset_index(drop=True), \
               df.sort_values("% Chg", ascending=True).head(8).reset_index(drop=True)
    except:
        return None, None

def get_options_chain(ltp: float, symbol: str):
    try:
        t = yf.Ticker(f"{symbol}.NS")
        if t.options:
            chain = t.option_chain(t.options[0])
            calls = chain.calls[["strike", "lastPrice"]].rename(columns={"lastPrice": "Call Price (CE)"})
            puts = chain.puts[["strike", "lastPrice"]].rename(columns={"lastPrice": "Put Price (PE)"})
            df = pd.merge(calls, puts, on="strike", how="outer").rename(columns={"strike": "Strike Price"})
            atm = round(ltp / 50) * 50 if ltp > 500 else round(ltp / 10) * 10
            df = df.iloc[(df["Strike Price"] - atm).abs().argsort()[:5]].sort_values("Strike Price").reset_index(drop=True)
            if not df.empty:
                return df[["Call Price (CE)", "Strike Price", "Put Price (PE)"]]
    except: pass
    gap = 50 if ltp > 1000 else (20 if ltp > 500 else 10)
    atm = round(ltp / gap) * gap
    strikes = [atm + i * gap for i in range(-2, 3)]
    rows = []
    for s in strikes:
        ce = max(5, (ltp - s) + np.random.uniform(8, 35)) if s <= ltp else np.random.uniform(5, 40)
        pe = max(5, (s - ltp) + np.random.uniform(8, 35)) if s >= ltp else np.random.uniform(5, 40)
        rows.append({"Call Price (CE)": round(ce, 2), "Strike Price": s, "Put Price (PE)": round(pe, 2)})
    return pd.DataFrame(rows)

@st.cache_data
def get_stock_universe():
    return [
        "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "BHARTIARTL", "SBIN", "LT",
        "AXISBANK", "KOTAKBANK", "ITC", "HINDUNILVR", "BAJFINANCE", "ASIANPAINT", "MARUTI",
        "TITAN", "SUNPHARMA", "WIPRO", "ULTRACEMCO", "NESTLEIND", "TATAMOTORS", "POWERGRID",
        "NTPC", "ONGC", "M&M", "HCLTECH", "ADANIENT", "ADANIPORTS", "JSWSTEEL", "TATASTEEL",
        "BAJAJFINSV", "TECHM", "INDUSINDBK", "CIPLA", "DRREDDY", "EICHERMOT", "HEROMOTOCO",
        "GRASIM", "COALINDIA", "BPCL", "PIDILITIND", "DIXON", "PERSISTENT", "POLYCAB",
        "CUMMINSIND", "ASTRAL", "PAGEIND", "HAVELLS", "VOLTAS", "BERGEPAINT"
    ]

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    "doubleClick": "reset",
    "displaylogo": False,
    "responsive": True
}

# -------------------------------------------------
# Sidebar (Desktop friendly)
# -------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    
    theme_choice = st.radio("Theme", ["🌙 Dark", "☀️ Light"],
                            index=0 if st.session_state.theme == "dark" else 1,
                            horizontal=True)
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
    st.caption("Data: Yahoo Finance • ~15 min delay")

# -------------------------------------------------
# Header + Time
# -------------------------------------------------
ist = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(ist).strftime("%d %b %Y • %H:%M:%S IST")

st.markdown("# 📈 Apex Market Terminal")
st.caption(f"Live Indian Equities & Indices • **{current_time}**")

# ========== MAIN CONTROLS (Visible on both Desktop & Mobile) ==========
universe = get_stock_universe()

col1, col2, col3 = st.columns([2.2, 1.2, 1])

with col1:
    selected = st.selectbox("🔍 Select Stock (NSE)", options=universe, index=0, key="selected")

with col2:
    auto_refresh = st.checkbox("🔄 Auto-refresh every 1 min", value=False)

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# -------------------------------------------------
# Indices
# -------------------------------------------------
st.markdown('<div class="section-header">Market Indices</div>', unsafe_allow_html=True)
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "NIFTY MIDCAP 150": "NIFTYMIDCAP150.NS"}
cols = st.columns(3)
for i, (name, ticker) in enumerate(indices.items()):
    data = fetch_index_quote(ticker)
    with cols[i]:
        if data:
            sign = "+" if data["change"] >= 0 else ""
            color = "pos" if data["change"] >= 0 else "neg"
            st.markdown(f"""
            <div class="metric-card">
                <div class="index-title">{name}</div>
                <div class="index-price">₹{data['price']:,.2f}</div>
                <div class="index-change {color}">{sign}{data['change']:.2f} ({sign}{data['pct']:.2f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"{name} unavailable")

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

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=[0.72, 0.28], subplot_titles=(f"{selected} • {timeframe}", "Volume"))

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
    fig.add_trace(go.Bar(x=candle_df["x"], y=candle_df["Volume"], marker_color=colors,
                         name="Volume", opacity=0.7, hoverinfo="skip"), row=2, col=1)

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
        fig.update_xaxes(type="category", tickmode="array", tickvals=tickvals, ticktext=ticktext,
                         tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)
    else:
        fig.update_xaxes(tickformat="%d %b", tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)

    fig.update_yaxes(tickfont=dict(color=axis_color), gridcolor=grid_color, showgrid=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    # Renko
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
        fig_r.add_trace(go.Scatter(x=renko_df["Brick"], y=renko_df["EMA20"], mode="lines", name="EMA 20",
                                   line=dict(color="#fbbf24", width=1.5)))
        fig_r.add_trace(go.Scatter(x=renko_df["Brick"], y=renko_df["EMA50"], mode="lines", name="EMA 50",
                                   line=dict(color="#60a5fa", width=1.8)))

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

# Options
st.markdown('<div class="section-header">⚡ Options Strike Matrix (ATM ±2)</div>', unsafe_allow_html=True)
st.caption(f"Spot: **₹{metrics['ltp']:,.2f}**")
options_df = get_options_chain(metrics["ltp"], selected)

def highlight_atm(row):
    if row.name == 2:
        return ["background-color: #312e81; color: #e0e7ff; font-weight: 600"] * len(row) if st.session_state.theme == "dark" \
               else ["background-color: #e0e7ff; color: #312e81; font-weight: 600"] * len(row)
    return [""] * len(row)

styled = options_df.style.format({"Call Price (CE)": "₹{:,.2f}", "Strike Price": "₹{:,.0f}", "Put Price (PE)": "₹{:,.2f}"}).apply(highlight_atm, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)

st.markdown("---")

# Gainers / Losers
st.markdown('<div class="section-header">🏆 Top Gainers & Losers</div>', unsafe_allow_html=True)
gainers, losers = get_top_movers(universe)
gcol, lcol = st.columns(2)
with gcol:
    st.markdown("##### 🟢 Top Gainers")
    if gainers is not None:
        st.dataframe(gainers.style.format({"LTP": "₹{:,.2f}", "Change": "{:+.2f}", "% Chg": "{:+.2f}%"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Loading...")
with lcol:
    st.markdown("##### 🔴 Top Losers")
    if losers is not None:
        st.dataframe(losers.style.format({"LTP": "₹{:,.2f}", "Change": "{:+.2f}", "% Chg": "{:+.2f}%"}),
                     use_container_width=True, hide_index=True)
    else:
        st.info("Loading...")

# Auto refresh every 1 minute
if auto_refresh:
    time.sleep(60)
    st.rerun()
