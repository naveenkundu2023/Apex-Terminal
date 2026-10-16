        }
    except:
        return None

@st.cache_data(ttl=45)
def get_pcr(symbol: str = "NIFTY"):
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
        if symbol.upper() in ["NIFTY", "NIFTY 50"]:
            url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        elif symbol.upper() in ["BANKNIFTY", "NIFTY BANK", "BANK NIFTY"]:
            url = "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
        else:
            return None
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        records = data.get("records", {})
        options = records.get("data", [])
        total_ce_oi = 0
        total_pe_oi = 0
        for item in options:
            ce = item.get("CE", {})
            pe = item.get("PE", {})
            total_ce_oi += ce.get("openInterest", 0) or 0
            total_pe_oi += pe.get("openInterest", 0) or 0
        if total_ce_oi == 0:
            return None
        pcr = total_pe_oi / total_ce_oi
        return round(pcr, 3)
    except Exception:
        return None

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
            except:
                continue
        return bullish, bearish
    except:
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
    except:
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
    except:
        return None

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
    st.caption("Data: Yahoo Finance + NSE + Moneycontrol • Options refresh every 30s")
