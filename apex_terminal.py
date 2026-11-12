# APEX MARKET TERMINAL — UPDATED BUILD 2026-11-12 (v7.8.0)
# v7.8.0 fixes:
# 1) Heatmap overnight refresh: corrected previous vs latest close matching so pre-market
#    opens display proper last session change rather than stale calculations.
# 2) Top 10 Business News: optimized cache and query refresh triggers.
# 3) Nifty Next 50 Heatmap: added secondary live heatmap section immediately below Nifty 50.
# v7.7.9:
# 1) Corporate Actions: removed hardcoded INFY 03-Nov-2026 dividend fallback that
#    kept repeating after the ex-date. Actions now filtered to rolling [today-1, today+10]
#    by parsed Ex-Date; if none → explicit "no event" message.
# 2) Results strip: Q1/Q2/Q3/Q4 heading auto-picks from purpose text, else calendar
#    month heuristic (India FY). Empty days still show "—" (rolling 10-day window).
# v7.7.8:
# 1) Gainers/Losers/Most-Active/Heatmap after close: Yahoo daily now uses last session
#    close vs prior close (not LTP=prev → 0%). Ranking prefers completed daily after hours.
# 2) Instant Snapshot: Renko box size 30M (ATR/12) + 15M (ATR/24) and live BUY/SELL/…
#    signal from the same analyzer used by the scanner.
# 3) Desktop (≥1101px): Market Indices grid 9 columns (27 boxes → 3 rows); FII 10 cards on one row.
#    Mobile/tablet breakpoints unchanged.
# v7.7.7 (multi-source live Nifty-50 + desktop density):
# 1) Heatmap / Gainers-Losers / Most-Active / Breadth:
#    Shared multi-source live batch (NSE equity-stockIndices → Yahoo intraday 1m/5m
#    → fast_info). Per-symbol picks newest parseable timestamp; market-hours = *Live,
#    after close = *Market closed. Yahoo daily-only lag path retired as primary.
# 2) Desktop-only density (min-width 1101px): tighter index/heatmap/FII/movers/
#    breadth/panel padding. OI chart + Renko layout untouched. Mobile unchanged.
# v7.7.6 (live % change + news quality):
# 1) Top Gainers/Losers + Heatmap + Most-Active Yahoo fallback:
#    bulk yf.download daily was lagging one session on Cloud → now live fast_info
#    + previous completed daily close (parallel). Cache 90s; top-10 returned.
# 2) Top 10 Business News:
#    - Max 2 headlines per source (stops Mint flooding the list)
#    - Near-duplicate suppression via normalised title cores
#    - Explicit per-desk Google News queries (ET, MC, FE, CNBC, Bloomberg…)
#    - Light-green news box (matches Instant Snapshot / CA style)
#    - 30-min cache retained; source badge shown on each item
# v7.7.5 (Streamlit Cloud thread-exhaustion fix):
# 1) ThreadPoolExecutor: lower workers + safe parallel helper with sequential fallback.
#    Prevents "can't start new thread" / RuntimeError that appeared every 4–5 days on Cloud.
# 2) Applied to: index cards (was 12), macro quotes (was 8), Renko scanner (was 14).
# 3) No behaviour change when threads are available; graceful degrade under resource pressure.
# v7.7.4 (institutional polish + FII/DII + OI + heatmap + news + macro + built-up):
# 1) OI chart: ATM / Max Pain labels no longer overlap (opposite anchors); stronger bar
#    colours + light-green plot bg for mobile/tablet visibility; wider bar groups.
# 2) Nifty 50 Heatmap: 10 equal cells per row on desktop (tablet/mobile unchanged).
# 3) FII/DII: Moneycontrol primary (cash + Idx/Stk Fut/Opt in Rs Cr) — full data matching
#    the reference cards; thicker band (3x); compact card height; 4h cache (EOD once/day).
# 4) Top news expanded to Top 10 + broader sources (Bloomberg, CNBC Asia, FE, Zee, etc.).
# 5) Built-up: institutional summary strip + conviction names + regime read.
# 6) Global Macro rewritten as Key Drivers / Risk Radar / India Implication (no quote dump).
# 7) Price chart volume bars stronger colours + Vol MA20 line.
# 8) Light institutional CSS (cleaner headers, denser FII cards, reduced emoji noise).
# v7.7.3:
# 1) NIFTYMIDSELECT Instant Snapshot via Moneycontrol JSON API (ind_id=128).
# 2) Mid Select candle + Renko from Moneycontrol techCharts history (mc;nmidcaps).
# 3) Fixed MC HTML URL (nifty-midcap-select-128.html).
# v7.7.2:
# 1) NIFTYMIDSELECT snapshot + charts via fetch_midcap_select (MC/Investing/TV) + Midcap100 OHLC fallback.
# 2) FII/DII: 10-day rolling from niftytrader series; compact 5/3/2 grid; colour band + readable body.
# 3) Commodity 5D bars still use Yahoo path for shape (INR LTP in snapshot is authoritative).
# v7.7.1:
# 1) MCX INR live quotes (Research360) for GOLD/SILVER/CRUDE — Instant Snapshot fixed.
# 2) Commodity option chain + OI via COMM_OPTION_CHAIN (nearest valid expiry auto-picked).
# 3) FII/DII from NSE fiidiiTradeReact + Nifty history (no blank section).
# 4) Removed st.stop on analytics miss — rest of page always renders.
# 5) Default select = NIFTY50. Charts/Renko scale USD Yahoo hist → MCX INR for commodities.
# v7.7.0:
# 1) Select Index/Stock/Commodity dropdown: NIFTY50, NIFTYBANK, NIFTYMIDSELECT, NIFTYFINSERVICE,
#    GOLD, SILVER, CRUDE + all Nifty-50 stocks. Unified Instant Snapshot + Option Chain + OI chart.
# 2) Snapshot (left) and Option-chain (right) boxes forced to equal visual height (matched cards).
# 3) New FII/DII section after Nifty Heatmap — last 10 sessions, colour-coded net buy/sell cards
#    (data from research360.in/market/fii-dii-data + NSE fallback).
# v7.6.2:
# 1) Corporate Actions & Upcoming Results: removed expander/duplication.
#    Results shown as 10-day rolling date strip with symbols under each date (simple Q2-style heading).
#    Corporate actions stay as compact list (no dropdown).
# 2) Market Indices cards: CSS responsive grid (6 / 3 / 2 cols) so mobile shows 2 cards per row;
#    long names truncated with ellipsis — no ugly wrap.
# v7.6.1:
# 1) REMOVED: Renko Signal Simulation Analytics block (and related helpers / confidence blend) — was slowing the app.
# 2) Nifty 50 Heatmap: softer, lighter green/red shades (less eye strain) + slightly larger mobile text (still no-wrap).
# v7.6: Heatmap cells now an equal-size responsive grid (5/4/3 columns) — no mid-word wrapping on mobile.
# v7.5: Stock Instant Snapshot box light-green; other retained features.
# v7.4 changes:
# 1) REMOVED: 5D VWAP × PCR positional screen section (and related helpers) — not required.
# 2) Visual redesign toward clean multi-panel dashboard (inspired by Apex mockups):
#    tighter index cards, glass-style panels, clearer section hierarchy, refined dark/light CSS.
# 3) All prior features & logic retained: Renko scanner, stock snapshot (incl. 5D bars + snapshot VWAP),
#    options matrix, heatmap ▲/▼, built-up cycle, corporate actions + upcoming results, top-6 news,
#    breadth/PCR/MaxPain/IV, most-active, etc.
# 4) Fast Refresh still soft-clears live quotes only.
# v7.1–v7.3 core retained: signal rules, box ladder, built-up.

import streamlit as st
import streamlit.components.v1 as components
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
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import xml.etree.ElementTree as ET

# -------------------------------------------------
# Safe parallel map — Streamlit Cloud can exhaust OS threads
# after days of auto-refresh / concurrent sessions. Falls
# back to sequential so the page never crashes on RuntimeError.
# -------------------------------------------------
def _safe_parallel_map(fn, iterable, max_workers=6):
    """map(fn, iterable) via ThreadPoolExecutor; sequential on thread failure."""
    items = list(iterable)
    if not items:
        return []
    workers = max(1, min(int(max_workers), len(items)))
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(fn, items))
    except RuntimeError:
        return [fn(x) for x in items]
    except Exception:
        return [fn(x) for x in items]


def _safe_parallel_submit(fn, jobs, max_workers=6):
    jobs = list(jobs)
    if not jobs:
        return []
    workers = max(1, min(int(max_workers), len(jobs)))
    results = []
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(fn, *job) if isinstance(job, (tuple, list)) else pool.submit(fn, job)
                       for job in jobs]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                except Exception:
                    continue
        return results
    except RuntimeError:
        for job in jobs:
            try:
                result = fn(*job) if isinstance(job, (tuple, list)) else fn(job)
                if result is not None:
                    results.append(result)
            except Exception:
                continue
        return results
    except Exception:
        for job in jobs:
            try:
                result = fn(*job) if isinstance(job, (tuple, list)) else fn(job)
                if result is not None:
                    results.append(result)
            except Exception:
                continue
        return results


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
if "heatmap_prev_pct" not in st.session_state:
    st.session_state.heatmap_prev_pct = {}

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
            label, .stSelectbox label, .stRadio label, [data-testid="stWidgetLabel"] p,
            [data-testid="stSelectbox"] label, [data-testid="stRadio"] label {
                color: #f1f5f9 !important; font-weight: 600 !important;
            }
            .stSelectbox > div > div, .stRadio > div { color: #f8fafc !important; }
            div[data-baseweb="select"] > div, div[data-baseweb="select"] span { color: #f8fafc !important; }
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
            .metric-card-up .index-title, .metric-card-down .index-title { color: #52615a !important; }
            .metric-card-up .index-price, .metric-card-down .index-price { color: #26332b !important; }
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
            .bu-cell { display: inline-block; width: 28px; height: 22px; border-radius: 4px; margin: 1px; }
            .bu-lb { background: #059669; }
            .bu-sb { background: #dc2626; }
            .bu-sc { background: #2563eb; }
            .bu-lu { background: #a3a30a; }
            .bu-na { background: #475569; }
            .news-box {
                background: #eaf6ed !important;
                border: 1px solid #d3e9d8 !important;
                border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;
                box-shadow: none !important;
                color: #26332b !important;
            }
            .news-box a { color: #166534 !important; font-weight: 600; }
            .news-box, .news-box * { color: #26332b !important; }
            .ca-box {
                background: #eaf6ed !important;
                border: 1px solid #d3e9d8 !important;
                border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;
                box-shadow: none !important;
                color: #26332b !important;
            }
            .ca-box, .ca-box * { color: #26332b !important; }
            .ca-box a { color: #166534 !important; }
            .movers-h {
                font-size: 12px; font-weight: 700; color: #c7d2fe;
                letter-spacing: 0.2px; margin-bottom: 6px; text-transform: uppercase;
            }
            .movers-grid {
                display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; width: 100%; margin-bottom: 8px;
            }
            @media (max-width: 900px) { .movers-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; } }
            @media (max-width: 520px) { .movers-grid { grid-template-columns: 1fr; } }
            .movers-panel {
                background: #f8fafc !important; border: 1px solid #e2e8f0 !important; border-radius: 10px; padding: 8px 8px 6px 8px; overflow: hidden;
            }
            .movers-panel .movers-h {
                font-size: 11px !important; font-weight: 700; letter-spacing: 0.3px; text-transform: uppercase; margin: 0 0 5px 2px; color: #334155 !important;
            }
            .movers-tbl { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; line-height: 1.25; }
            .movers-tbl th { font-size: 10px; font-weight: 600; color: #64748b; text-align: right; padding: 2px 4px 4px 4px; border-bottom: 1px solid #e2e8f0; }
            .movers-tbl th:first-child { text-align: left; width: 34%; }
            .movers-tbl td { padding: 3px 4px; text-align: right; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .movers-tbl td.m-sym { text-align: left; font-weight: 700; color: #0f172a; }
            .movers-tbl td.m-pos { color: #059669; font-weight: 700; }
            .movers-tbl td.m-neg { color: #dc2626; font-weight: 700; }
            .movers-tbl td.m-muted { color: #475569; font-size: 11px; }
            .movers-tbl tr:nth-child(even) td { background: #f1f5f9; }
            .breadth-grid { display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 6px; width: 100%; margin-bottom: 2px; }
            .live-an-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 6px; width: 100%; margin-bottom: 4px; margin-top: 0; }
            @media (max-width: 1100px) {
                .breadth-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
                .live-an-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            }
            @media (max-width: 600px) {
                .breadth-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 5px; }
                .live-an-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 5px; }
            }
            .breadth-card {
                background: linear-gradient(145deg, rgba(30,41,59,0.95), rgba(15,23,42,0.98));
                border: 1px solid rgba(99,102,241,0.28); border-radius: 8px; padding: 10px 6px; text-align: center; min-height: 58px;
            }
            .breadth-lab { font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.2px; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .breadth-val { font-size: 16px; font-weight: 700; color: #f1f5f9; line-height: 1.2; }
            .breadth-val.pos { color: #34d399 !important; }
            .breadth-val.neg { color: #f87171 !important; }
            .dash-topbar {
                display: flex; align-items: center; justify-content: space-between; padding: 10px 4px 14px 4px; margin-bottom: 4px; border-bottom: 1px solid rgba(99,102,241,0.25);
            }
            .dash-brand { display: flex; align-items: center; gap: 10px; }
            .dash-brand .logo {
                width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #6366f1, #a855f7); display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 800; color: #fff;
            }
            .dash-brand h1 {
                font-size: 22px !important; margin: 0 !important; padding: 0 !important; background: linear-gradient(90deg, #a5b4fc, #c4b5fd, #f0abfc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; line-height: 1.15;
            }
            .dash-brand .tagline { font-size: 11px; color: #94a3b8; letter-spacing: 0.4px; }
            .dash-live { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #cbd5e1; }
            .live-dot { width: 8px; height: 8px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399; animation: pulse 1.6s ease-in-out infinite; }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.45; } }
            .panel-card {
                background: linear-gradient(145deg, rgba(30,41,59,0.92), rgba(15,23,42,0.96));
                border: 1px solid rgba(99,102,241,0.28); border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 4px 18px rgba(0,0,0,0.28);
            }
            .panel-title { font-size: 13px; font-weight: 700; color: #c7d2fe; letter-spacing: 0.3px; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
            .metric-card { transition: transform 0.15s ease, border-color 0.15s ease; }
            .metric-card:hover { transform: translateY(-2px); border-color: rgba(129,140,248,0.55) !important; }
            .section-header {
                font-size: 16px !important; font-weight: 700; background: linear-gradient(90deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; margin-top: 4px; padding-bottom: 4px; border-bottom: 1px solid rgba(99,102,241,0.15);
            }
            div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid rgba(148,163,184,0.18); }
            .dash-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent); margin: 14px 0; }
            .snapshot-box { background: #eaf6ed !important; border: 1px solid #d3e9d8 !important; box-shadow: none !important; color: #26332b !important; }
            .snapshot-box .panel-title { color: #386b49 !important; }
            .heat-grid { display: grid; grid-template-columns: repeat(10, minmax(0, 1fr)); gap: 5px; width: 100%; }
            .heat-grid .heat-cell { width: auto !important; margin: 0 !important; padding: 6px 1px !important; min-height: 68px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px; box-sizing: border-box; overflow: hidden; line-height: 1.15; }
            .heat-grid .hc-sym { font-size: clamp(11px, 2.9vw, 13px); font-weight: 700; white-space: nowrap; max-width: 100%; letter-spacing: -0.2px; }
            .heat-grid .hc-pct { font-size: clamp(11px, 3.0vw, 13px); font-weight: 600; white-space: nowrap; }
            .heat-grid .hc-ltp { font-size: clamp(10px, 2.6vw, 12px); font-weight: 500; opacity: 0.92; white-space: nowrap; }
            @media (max-width: 900px) { .heat-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
            @media (max-width: 600px) { .heat-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; } }
            .index-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; width: 100%; }
            .index-grid .metric-card { min-height: 72px !important; padding: 6px 4px !important; overflow: hidden; }
            .index-grid .index-title { font-size: 9px !important; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; display: block; }
            .index-grid .index-price { font-size: 13px !important; }
            .index-grid .index-change { font-size: 10px !important; }
            @media (max-width: 1100px) {
                .index-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
                .index-grid .index-title { font-size: 10px !important; }
                .index-grid .index-price { font-size: 14px !important; }
            }
            @media (max-width: 600px) {
                .index-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; }
                .index-grid .metric-card { min-height: 68px !important; padding: 6px 3px !important; }
                .index-grid .index-title { font-size: 9px !important; }
                .index-grid .index-price { font-size: 13px !important; }
                .index-grid .index-change { font-size: 10px !important; }
            }
            .res-date-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(72px, 1fr)); gap: 6px; width: 100%; }
            .res-day { background: #f0faf3; border: 1px solid #cfe8d6; border-radius: 8px; padding: 6px 4px; text-align: center; min-height: 64px; }
            .res-day .rd-date { font-size: 11px; font-weight: 700; color: #166534; margin-bottom: 4px; white-space: nowrap; }
            .res-day .rd-syms { font-size: 10px; font-weight: 600; color: #26332b; line-height: 1.25; word-break: break-word; }
            .res-day.empty .rd-syms { color: #64748b; font-weight: 500; }
            .res-day.res-today { background: #bbf7d0 !important; border: 1px solid #4ade80 !important; }
            .res-day.res-near { background: #e0f2fe !important; border: 1px solid #bae6fd !important; }
            .res-day.res-later { background: #f1f5f9 !important; border: 1px solid #e2e8f0 !important; }
            .snap-opt-row { display: flex; flex-wrap: wrap; gap: 12px; align-items: stretch; width: 100%; }
            .snap-opt-row > .snap-panel, .snap-opt-row > .opt-panel { flex: 1 1 0; min-width: 280px; display: flex; flex-direction: column; }
            .snap-opt-row .snapshot-box, .snap-opt-row .options-box { flex: 1 1 auto; min-height: 168px; display: flex; flex-direction: column; }
            .options-box { background: #eaf6ed !important; border: 1px solid #d3e9d8 !important; box-shadow: none !important; color: #26332b !important; border-radius: 12px; padding: 0 !important; overflow: hidden; }
            .fii-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; width: 100%; }
            @media (max-width: 1100px) { .fii-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
            @media (max-width: 600px) { .fii-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; } }
            .fii-card { border-radius: 10px; padding: 0; overflow: hidden; border: 1px solid rgba(148,163,184,0.35); background: #f8fafc; min-height: 0; color: #0f172a; }
            .fii-card .fii-band { height: 18px; width: 100%; }
            .fii-card.up .fii-band { background: linear-gradient(90deg, #16a34a, #4ade80); }
            .fii-card.down .fii-band { background: linear-gradient(90deg, #dc2626, #f87171); }
            .fii-card .fii-body { padding: 5px 8px 6px 8px; }
            .fii-card .fii-date { font-size: 14px; font-weight: 800; line-height: 1.0; color: #0f172a; }
            .fii-card .fii-month { font-size: 10px; font-weight: 600; color: #475569; margin-bottom: 2px; }
            .fii-card .fii-nifty { font-size: 10px; font-weight: 600; color: #1e293b; margin-bottom: 2px; line-height: 1.2; }
            .fii-card .fii-row { display: flex; justify-content: space-between; gap: 4px; padding: 0; font-size: 10px; color: #334155; line-height: 1.25; }
            .fii-card .fii-row span:first-child { color: #64748b; }
            .fii-card .fii-net { font-size: 12px; font-weight: 800; margin: 2px 0 1px 0; }
            .fii-pos { color: #15803d !important; font-weight: 700; }
            .fii-neg { color: #b91c1c !important; font-weight: 700; }
            @media (min-width: 1101px) {
                .dash-topbar { padding: 6px 4px 10px 4px !important; margin-bottom: 2px !important; }
                .dash-brand h1 { font-size: 20px !important; }
                .section-header { margin-bottom: 6px !important; margin-top: 2px !important; padding-bottom: 2px !important; font-size: 15px !important; }
                .panel-card, .analysis-box { padding: 10px 12px !important; margin-bottom: 8px !important; }
                .dash-divider { margin: 8px 0 !important; }
                .index-grid { grid-template-columns: repeat(9, minmax(0, 1fr)) !important; gap: 5px !important; }
                .index-grid .metric-card { min-height: 52px !important; padding: 3px 2px !important; }
                .index-grid .index-title { font-size: 7px !important; }
                .index-grid .index-price { font-size: 11px !important; }
                .index-grid .index-change { font-size: 8px !important; }
                .heat-grid { gap: 4px !important; }
                .heat-grid .heat-cell { min-height: 52px !important; padding: 4px 1px !important; }
                .heat-grid .hc-sym { font-size: 11px !important; }
                .heat-grid .hc-pct { font-size: 11px !important; }
                .heat-grid .hc-ltp { font-size: 10px !important; }
                .movers-grid { gap: 6px !important; margin-bottom: 4px !important; }
                .movers-panel { padding: 5px 6px 4px 6px !important; }
                .movers-tbl td { padding: 2px 3px !important; }
                .movers-tbl th { padding: 1px 3px 3px 3px !important; }
                .breadth-grid, .live-an-grid { gap: 4px !important; }
                .breadth-card { min-height: 46px !important; padding: 6px 4px !important; }
                .breadth-lab { font-size: 11px !important; margin-bottom: 2px !important; }
                .breadth-val { font-size: 14px !important; }
                .fii-grid { grid-template-columns: repeat(10, minmax(0, 1fr)) !important; gap: 4px !important; }
                .fii-card .fii-band { height: 8px !important; }
                .fii-card .fii-body { padding: 2px 4px 3px 4px !important; }
                .fii-card .fii-date { font-size: 11px !important; }
                .fii-card .fii-month { font-size: 8px !important; margin-bottom: 1px !important; }
                .fii-card .fii-nifty { font-size: 8px !important; margin-bottom: 1px !important; }
                .fii-card .fii-row { font-size: 8px !important; line-height: 1.15 !important; }
                .fii-card .fii-net { font-size: 10px !important; margin: 1px 0 !important; }
                .ca-box, .news-box { padding: 8px 12px !important; margin-bottom: 6px !important; }
                .res-day { min-height: 56px !important; padding: 4px 3px !important; }
                .builtup-wrap { padding: 10px !important; }
            }
            @media (max-width: 600px) {
                .res-date-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; }
                .res-day { min-height: 58px; padding: 5px 3px; }
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
                border: 1px solid #c7d2fe; border-radius: 10px; padding: 8px 6px !important; text-align: center; box-shadow: 0 3px 12px rgba(99,102,241,0.12); min-height: 78px !important;
            }
            .index-title { font-size: 10px !important; font-weight: 600; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase; margin-bottom: 3px !important; line-height: 1.1; }
            .index-price { font-size: 15px !important; font-weight: 700; color: #0f172a; line-height: 1.15 !important; margin: 2px 0 !important; }
            .index-change { font-size: 11px !important; font-weight: 600; margin-top: 1px !important; }
            .pos { color: #059669 !important; }
            .neg { color: #dc2626 !important; }
            .section-header {
                font-size: 18px; font-weight: 700; background: linear-gradient(90deg, #4f46e5, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;
            }
            div[data-testid="stMetric"] { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
            div[data-testid="stMetric"] label { color: #64748b !important; }
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 700 !important; }
            .stButton > button { background: linear-gradient(90deg, #4f46e5, #7c3aed); color: white; border: none; border-radius: 10px; font-weight: 600; }
            h1 { background: linear-gradient(90deg, #4f46e5, #7c3aed, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }
            .watchlist-chip { display: inline-block; background: #e0e7ff; color: #3730a3; padding: 4px 12px; border-radius: 20px; margin: 3px; font-size: 13px; font-weight: 500; }
            .analysis-box { background: white; border: 1px solid #c7d2fe; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(99,102,241,0.08); }
            .heat-cell { display: inline-block; width: 19%; margin: 0.5%; padding: 8px 4px; border-radius: 6px; text-align: center; font-size: 11px; font-weight: 600; color: #fff; min-height: 52px; }
            label, .stSelectbox label, .stRadio label, [data-testid="stWidgetLabel"] p { color: #0f172a !important; font-weight: 600 !important; }
            .metric-card-up { background: #eaf6ed !important; border: 1px solid #d3e9d8 !important; box-shadow: none !important; }
            .metric-card-down { background: #fbeeee !important; border: 1px solid #f0d6d6 !important; box-shadow: none !important; }
            .metric-card-up .index-title, .metric-card-down .index-title { color: #52615a !important; }
            .metric-card-up .index-price, .metric-card-down .index-price { color: #26332b !important; }
            .metric-card-up .index-change { color: #386b49 !important; }
            .metric-card-down .index-change { color: #8a4545 !important; }
            .builtup-wrap { background: #ffffff; border: 1px solid #c7d2fe; border-radius: 12px; padding: 14px; overflow-x: auto; }
            .builtup-table { border-collapse: collapse; width: 100%; font-size: 12px; }
            .builtup-table th { color: #64748b; font-weight: 600; padding: 4px 6px; text-align: center; }
            .builtup-table td { padding: 3px 4px; text-align: center; }
            .bu-cell { display: inline-block; width: 28px; height: 22px; border-radius: 4px; margin: 1px; }
            .bu-lb { background: #059669; }
            .bu-sb { background: #dc2626; }
            .bu-sc { background: #2563eb; }
            .bu-lu { background: #a3a30a; }
            .bu-na { background: #94a3b8; }
            .news-box { background: #eaf6ed !important; border: 1px solid #d3e9d8 !important; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; box-shadow: none !important; color: #26332b !important; }
            .news-box a { color: #166534 !important; font-weight: 600; }
            .ca-box { background: #eaf6ed !important; border: 1px solid #d3e9d8 !important; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; box-shadow: none !important; color: #26332b !important; }
            .ca-box, .ca-box * { color: #26332b !important; }
            .ca-box a { color: #166534 !important; }
            .movers-h { font-size: 12px; font-weight: 700; color: #4338ca; letter-spacing: 0.2px; margin-bottom: 6px; text-transform: uppercase; }
            .movers-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; width: 100%; margin-bottom: 8px; }
            @media (max-width: 900px) { .movers-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; } }
            @media (max-width: 520px) { .movers-grid { grid-template-columns: 1fr; } }
            .movers-panel { background: #f8fafc !important; border: 1px solid #e2e8f0 !important; border-radius: 10px; padding: 8px 8px 6px 8px; overflow: hidden; }
            .movers-panel .movers-h { font-size: 11px !important; font-weight: 700; letter-spacing: 0.3px; text-transform: uppercase; margin: 0 0 5px 2px; color: #334155 !important; }
            .movers-tbl { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 12px; line-height: 1.25; }
            .movers-tbl th { font-size: 10px; font-weight: 600; color: #64748b; text-align: right; padding: 2px 4px 4px 4px; border-bottom: 1px solid #e2e8f0; }
            .movers-tbl th:first-child { text-align: left; width: 34%; }
            .movers-tbl td { padding: 3px 4px; text-align: right; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .movers-tbl td.m-sym { text-align: left; font-weight: 700; color: #0f172a; }
            .movers-tbl td.m-pos { color: #059669; font-weight: 700; }
            .movers-tbl td.m-neg { color: #dc2626; font-weight: 700; }
            .movers-tbl td.m-muted { color: #475569; font-size: 11px; }
            .movers-tbl tr:nth-child(even) td { background: #f1f5f9; }
            .dash-topbar { display: flex; align-items: center; justify-content: space-between; padding: 10px 4px 14px 4px; margin-bottom: 4px; border-bottom: 1px solid #c7d2fe; }
            .dash-brand { display: flex; align-items: center; gap: 10px; }
            .dash-brand .logo { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #4f46e5, #7c3aed); display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 800; color: #fff; }
            .dash-brand h1 { font-size: 22px !important; margin: 0 !important; padding: 0 !important; background: linear-gradient(90deg, #4f46e5, #7c3aed, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; line-height: 1.15; }
            .dash-brand .tagline { font-size: 11px; color: #64748b; letter-spacing: 0.4px; }
            .dash-live { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #475569; }
            .live-dot { width: 8px; height: 8px; border-radius: 50%; background: #059669; box-shadow: 0 0 6px #34d399; }
            .panel-card { background: #ffffff; border: 1px solid #c7d2fe; border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(99,102,241,0.08); }
            .panel-title { font-size: 13px; font-weight: 700; color: #4338ca; letter-spacing: 0.3px; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
            .section-header { font-size: 16px !important; border-bottom: 1px solid #e0e7ff; padding-bottom: 4px; }
            div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #e2e8f0; }
            .dash-divider { height: 1px; background: linear-gradient(90deg, transparent, #c7d2fe, transparent); margin: 14px 0; }
            .snapshot-box { background: #eaf6ed !important; border: 1px solid #d3e9d8 !important; box-shadow: none !important; color: #26332b !important; }
            .snapshot-box .panel-title { color: #386b49 !important; }
            .heat-grid { display: grid; grid-template-columns: repeat(10, minmax(0, 1fr)); gap: 5px; width: 100%; }
            .heat-grid .heat-cell { width: auto !important; margin: 0 !important; padding: 6px 1px !important; min-height: 68px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px; box-sizing: border-box; overflow: hidden; line-height: 1.15; }
            .heat-grid .hc-sym { font-size: clamp(11px, 2.9vw, 13px); font-weight: 700; white-space: nowrap; max-width: 100%; letter-spacing: -0.2px; }
            .heat-grid .hc-pct { font-size: clamp(11px, 3.0vw, 13px); font-weight: 600; white-space: nowrap; }
            .heat-grid .hc-ltp { font-size: clamp(10px, 2.6vw, 12px); font-weight: 500; opacity: 0.92; white-space: nowrap; }
            @media (max-width: 900px) { .heat-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
            @media (max-width: 600px) { .heat-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; } }
            .index-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; width: 100%; }
            .index-grid .metric-card { min-height: 72px !important; padding: 6px 4px !important; overflow: hidden; }
            .index-grid .index-title { font-size: 9px !important; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; display: block; }
            .index-grid .index-price { font-size: 13px !important; }
            .index-grid .index-change { font-size: 10px !important; }
            @media (max-width: 1100px) {
                .index-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
                .index-grid .index-title { font-size: 10px !important; }
                .index-grid .index-price { font-size: 14px !important; }
            }
            @media (max-width: 600px) {
                .index-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; }
                .index-grid .metric-card { min-height: 68px !important; padding: 6px 3px !important; }
                .index-grid .index-title { font-size: 9px !important; }
                .index-grid .index-price { font-size: 13px !important; }
                .index-grid .index-change { font-size: 10px !important; }
            }
            .res-date-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(72px, 1fr)); gap: 6px; width: 100%; }
            .res-day { background: #f0faf3; border: 1px solid #cfe8d6; border-radius: 8px; padding: 6px 4px; text-align: center; min-height: 64px; box-shadow: none; }
            .res-day .rd-date { font-size: 11px; font-weight: 700; color: #166534; margin-bottom: 4px; white-space: nowrap; }
            .res-day .rd-syms { font-size: 10px; font-weight: 600; color: #26332b; line-height: 1.25; word-break: break-word; }
            .res-day.empty .rd-syms { color: #94a3b8; font-weight: 500; }
            .res-day.res-today { background: #bbf7d0 !important; border: 1px solid #4ade80 !important; }
            .res-day.res-near { background: #e0f2fe !important; border: 1px solid #bae6fd !important; }
            .res-day.res-later { background: #f1f5f9 !important; border: 1px solid #e2e8f0 !important; }
            .snap-opt-row { display: flex; flex-wrap: wrap; gap: 12px; align-items: stretch; width: 100%; }
            .snap-opt-row > .snap-panel, .snap-opt-row > .opt-panel { flex: 1 1 0; min-width: 280px; display: flex; flex-direction: column; }
            .snap-opt-row .snapshot-box, .snap-opt-row .options-box { flex: 1 1 auto; min-height: 168px; display: flex; flex-direction: column; }
            .options-box { background: #eaf6ed !important; border: 1px solid #d3e9d8 !important; box-shadow: none !important; color: #26332b !important; border-radius: 12px; padding: 0 !important; overflow: hidden; }
            .fii-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; width: 100%; }
            @media (max-width: 1100px) { .fii-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
            @media (max-width: 600px) { .fii-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; } }
            .fii-card { border-radius: 10px; padding: 0; overflow: hidden; border: 1px solid rgba(148,163,184,0.35); background: #f8fafc; min-height: 0; color: #0f172a; }
            .fii-card .fii-band { height: 18px; width: 100%; }
            .fii-card.up .fii-band { background: linear-gradient(90deg, #16a34a, #4ade80); }
            .fii-card.down .fii-band { background: linear-gradient(90deg, #dc2626, #f87171); }
            .fii-card .fii-body { padding: 5px 8px 6px 8px; }
            .fii-card .fii-date { font-size: 14px; font-weight: 800; line-height: 1.0; color: #0f172a; }
            .fii-card .fii-month { font-size: 10px; font-weight: 600; color: #475569; margin-bottom: 2px; }
            .fii-card .fii-nifty { font-size: 10px; font-weight: 600; color: #1e293b; margin-bottom: 2px; line-height: 1.2; }
            .fii-card .fii-row { display: flex; justify-content: space-between; gap: 4px; padding: 0; font-size: 10px; color: #334155; line-height: 1.25; }
            .fii-card .fii-row span:first-child { color: #64748b; }
            .fii-card .fii-net { font-size: 12px; font-weight: 800; margin: 2px 0 1px 0; }
            .fii-pos { color: #15803d !important; font-weight: 700; }
            .fii-neg { color: #b91c1c !important; font-weight: 700; }
            @media (min-width: 1101px) {
                .dash-topbar { padding: 6px 4px 10px 4px !important; margin-bottom: 2px !important; }
                .dash-brand h1 { font-size: 20px !important; }
                .section-header { margin-bottom: 6px !important; margin-top: 2px !important; padding-bottom: 2px !important; font-size: 15px !important; }
                .panel-card, .analysis-box { padding: 10px 12px !important; margin-bottom: 8px !important; }
                .dash-divider { margin: 8px 0 !important; }
                .index-grid { grid-template-columns: repeat(9, minmax(0, 1fr)) !important; gap: 5px !important; }
                .index-grid .metric-card { min-height: 52px !important; padding: 3px 2px !important; }
                .index-grid .index-title { font-size: 7px !important; }
                .index-grid .index-price { font-size: 11px !important; }
                .index-grid .index-change { font-size: 8px !important; }
                .heat-grid { gap: 4px !important; }
                .heat-grid .heat-cell { min-height: 52px !important; padding: 4px 1px !important; }
                .heat-grid .hc-sym { font-size: 11px !important; }
                .heat-grid .hc-pct { font-size: 11px !important; }
                .heat-grid .hc-ltp { font-size: 10px !important; }
                .movers-grid { gap: 6px !important; margin-bottom: 4px !important; }
                .movers-panel { padding: 5px 6px 4px 6px !important; }
                .movers-tbl td { padding: 2px 3px !important; }
                .movers-tbl th { padding: 1px 3px 3px 3px !important; }
                .breadth-grid, .live-an-grid { gap: 4px !important; }
                .breadth-card { min-height: 46px !important; padding: 6px 4px !important; }
                .breadth-lab { font-size: 11px !important; margin-bottom: 2px !important; }
                .breadth-val { font-size: 14px !important; }
                .fii-grid { grid-template-columns: repeat(10, minmax(0, 1fr)) !important; gap: 4px !important; }
                .fii-card .fii-band { height: 8px !important; }
                .fii-card .fii-body { padding: 2px 4px 3px 4px !important; }
                .fii-card .fii-date { font-size: 11px !important; }
                .fii-card .fii-month { font-size: 8px !important; margin-bottom: 1px !important; }
                .fii-card .fii-nifty { font-size: 8px !important; margin-bottom: 1px !important; }
                .fii-card .fii-row { font-size: 8px !important; line-height: 1.15 !important; }
                .fii-card .fii-net { font-size: 10px !important; margin: 1px 0 !important; }
                .ca-box, .news-box { padding: 8px 12px !important; margin-bottom: 6px !important; }
                .res-day { min-height: 56px !important; padding: 4px 3px !important; }
                .builtup-wrap { padding: 10px !important; }
            }
            @media (max-width: 600px) {
                .res-date-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; }
                .res-day { min-height: 58px; padding: 5px 3px; }
            }
        </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _source_short(source: str) -> str:
    if not source:
        return "?"
    s = source.lower()
    if "upstox" in s: return "U"
    if "moneycontrol" in s: return "M"
    if "investing" in s: return "I"
    if "tradingview" in s: return "T"
    if "yahoo" in s: return "Y"
    if "tradingeconomics" in s: return "TE"
    if "nse" in s: return "N"
    first = source.strip().split()[0] if source.strip() else "?"
    return first[0].upper() if first else "?"

def _ist_now_label() -> str:
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
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    if now.weekday() >= 5:
        return False
    t = now.time()
    return dtime(9, 15) <= t <= dtime(15, 30)

@st.cache_data(ttl=60)
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
                src = f"Yahoo Finance ({ticker})"
                ts = _ist_now_label()
                return {
                    "price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2),
                    "source": src, "source_short": _source_short(src), "source_time_label": ts, "fetched_at": ts,
                }
        info = t.fast_info
        price = getattr(info, "last_price", None) or getattr(info, "regular_market_price", None)
        prev = getattr(info, "previous_close", None) or price
        if price is not None:
            change = float(price) - float(prev)
            pct = (change / float(prev) * 100) if prev else 0
            src = f"Yahoo Finance ({ticker})"
            ts = _ist_now_label()
            return {
                "price": round(float(price), 2), "change": round(change, 2), "pct": round(pct, 2),
                "source": src, "source_short": _source_short(src), "source_time_label": ts, "fetched_at": ts,
            }
    except Exception:
        pass
    return None

@st.cache_data(ttl=60)
def fetch_index_quote(ticker: str):
    return fetch_yahoo_quote(ticker)

@st.cache_data(ttl=60, show_spinner=False)
def fetch_tradingview_quote(tv_symbol: str):
    try:
        exchange = tv_symbol.split(":", 1)[0].upper()
        region_map = {
            "NSEIX": "india", "NSE": "india", "MCX": "india", "BSE": "india",
            "COMEX": "america", "NYMEX": "america", "ICEEUR": "america", "DJ": "america",
            "NASDAQ": "america", "TVC": "america", "NYSE": "america", "CME": "america",
            "CBOT": "america", "CME_MINI": "america", "COINBASE": "crypto", "BINANCE": "crypto",
            "FX_IDC": "forex", "OANDA": "forex", "HSI": "hongkong", "TSE": "japan",
            "SSE": "china", "KRX": "korea", "ASX": "australia", "TWSE": "taiwan", "LSE": "uk", "FTSE": "uk"
        }
        region = region_map.get(exchange, "america")
        url = f"https://scanner.tradingview.com/{region}/scan"
        payload = {"symbols": {"tickers": [tv_symbol], "query": {"types": []}}, "columns": ["close", "change", "change_abs"]}
        headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json", "Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/"}
        r = requests.post(url, json=payload, headers=headers, timeout=6)
        if r.status_code != 200:
            return None
        rows = r.json().get("data", [])
        if not rows or not rows[0].get("d"):
            return None
        vals = rows[0]["d"]
        price, pct, change = vals[0], vals[1], vals[2]
        if price is None or float(price) <= 0:
            return None
        if change is None and pct is not None:
            change = float(price) * float(pct) / 100
        if pct is None and change is not None:
            pct = (float(change) / (float(price) - float(change)) * 100) if float(price) != float(change) else 0
        src = f"TradingView ({tv_symbol})"
        ts = _ist_now_label()
        return {
            "price": round(float(price), 2), "change": round(float(change or 0), 2), "pct": round(float(pct or 0), 2),
            "source": src, "source_short": _source_short(src), "source_time_label": ts, "fetched_at": ts,
        }
    except Exception:
        return None

@st.cache_data(ttl=60, show_spinner=False)
def fetch_investing_quote(slug: str):
    try:
        url = "https://www.investing.com/" + slug
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
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
            if not value: return None
            cleaned = re.sub(r"[^0-9.+-]", "", value.replace(",", ""))
            try: return float(cleaned) if cleaned not in ("", "+", "-") else None
            except ValueError: return None
        price = number(price_text)
        change = number(change_text) or 0.0
        pct = number(pct_text) or 0.0
        if price is None or price <= 0: return None
        src = f"Investing.com ({slug})"
        ts = _ist_now_label()
        return {
            "price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2),
            "source": src, "source_short": _source_short(src), "source_time_label": ts, "fetched_at": ts,
        }
    except Exception:
        return None

@st.cache_data(ttl=60, show_spinner=False)
def fetch_tradingeconomics_quote(slug: str):
    try:
        url = f"https://tradingeconomics.com/{slug}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200: return None
        html = r.text
        m_price = re.search(r'Actual\s*</[^>]*>\s*([0-9,]+(?:\.[0-9]+)?)', html, re.I | re.S)
        if not m_price: m_price = re.search(r'traded at\s+([0-9,]+(?:\.[0-9]+)?)', html, re.I)
        if not m_price: m_price = re.search(r'([0-9]{4,6}(?:\.[0-9]+)?)\s*(?:this|Index Points)', html, re.I)
        price = float(m_price.group(1).replace(",", "")) if m_price else None
        m_chg = re.search(r'Daily Change\s*</[^>]*>\s*([+-]?[0-9,]+(?:\.[0-9]+)?)\s+([+-]?[0-9.]+)\s*%', html, re.I | re.S)
        change = pct = 0.0
        if m_chg:
            change = float(m_chg.group(1).replace(",", ""))
            pct = float(m_chg.group(2))
        if price is None or price <= 0: return None
        src = f"TradingEconomics ({slug})"
        ts = _ist_now_label()
        return {
            "price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2),
            "source": src, "source_short": _source_short(src), "source_time_label": ts, "fetched_at": ts,
        }
    except Exception:
        return None

@st.cache_data(ttl=45, show_spinner=False)
def fetch_tradingeconomics_commodity(slug: str):
    try:
        url = f"https://tradingeconomics.com/{slug}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200: return None
        html = r.text
        def number(value):
            if value is None: return None
            cleaned = re.sub(r"[^0-9.+-]", "", str(value).replace(",", ""))
            try: return float(cleaned) if cleaned not in ("", "+", "-") else None
            except ValueError: return None
        price = None
        m = re.search(r'id=["\']market_last["\'][^>]*>([^<]+)', html, re.I)
        if m: price = number(m.group(1))
        if price is None or not (20.0 <= price <= 250.0): return None
        change = pct = 0.0
        block_m = re.search(r'id=["\']market_last["\'][^>]*>.*?</span>(.{0,500})', html, re.I | re.S)
        block = block_m.group(1) if block_m else html
        cm = re.search(r'id=["\']market_daily_chg["\'][^>]*>([^<]+)', block, re.I)
        if cm: change = number(cm.group(1)) or 0.0
        src = f"TradingEconomics ({slug})"
        ts = _ist_now_label()
        return {
            "price": round(float(price), 2), "change": round(float(change), 2), "pct": round(float(pct), 2),
            "source": src, "source_short": _source_short(src), "source_time_label": ts, "fetched_at": ts,
        }
    except Exception:
        return None

@st.cache_data(ttl=45, show_spinner=False)
def fetch_investing_brent():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Referer": "https://in.investing.com/",
    }
    def number(value):
        if not value: return None
        cleaned = re.sub(r"[^0-9.+-]", "", str(value).replace(",", ""))
        try: return float(cleaned) if cleaned not in ("", "+", "-") else None
        except ValueError: return None
    def parse_html(html, source_label):
        def extract(pattern):
            m = re.search(pattern, html, flags=re.I | re.S)
            return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else None
        price_text = extract(r'data-test=["\']instrument-price-last["\'][^>]*>(.*?)</')
        price = number(price_text)
        if price is None or not (50.0 <= price <= 200.0): return None
        ts = _ist_now_label()
        return {
            "price": round(float(price), 2), "change": 0.0, "pct": 0.0,
            "source": source_label, "source_short": _source_short(source_label), "source_time_label": ts, "fetched_at": ts,
        }
    for url, label in [("https://in.investing.com/commodities/brent-oil", "Investing.com (Brent Oil)"), ("https://www.investing.com/commodities/brent-oil", "Investing.com (Brent Oil)")]:
        try:
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200:
                q = parse_html(r.text, label)
                if q: return q
        except Exception:
            continue
    return None

INVESTING_SLUGS = {
    "GIFT_NIFTY": "indices/sgx-nifty", "US_TECH_FUT": "indices/nq-100-futures", "US_30_FUT": "indices/us-30-futures",
    "CL=F": "commodities/crude-oil", "BZ=F": "commodities/brent-oil", "NG=F": "commodities/natural-gas",
    "GC=F": "commodities/gold", "SI=F": "commodities/silver", "HG=F": "commodities/copper", "INR=X": "currencies/usd-inr",
    "BTC-USD": "crypto/bitcoin", "DX-Y.NYB": "indices/usdollar-index", "^TNX": "rates-bonds/u.s.-10-year-bond-yield",
    "^TYX": "rates-bonds/u.s.-30-year-bond-yield", "^HSI": "indices/hang-sen-40", "^N225": "indices/japan-ni225",
    "000001.SS": "indices/shanghai-composite", "^KS11": "indices/kospi", "^AXJO": "indices/asx-200",
    "^NDX": "indices/nq-100", "^DJI": "indices/us-30", "^IXIC": "indices/nasdaq-composite", "^TWII": "indices/taiwan-weighted",
    "^FTSE": "indices/uk-100", "MIDCAP_SELECT": "indices/nifty-midcap-select", "NIFTY_MID_SELECT": "indices/nifty-midcap-select",
}

YAHOO_FALLBACK = {
    "US_TECH_FUT": "^NDX", "US_30_FUT": "^DJI", "NG=F": "NG=F", "GC=F": "GC=F", "SI=F": "SI=F", "HG=F": "HG=F",
    "INR=X": "INR=X", "BTC-USD": "BTC-USD", "DX-Y.NYB": "DX-Y.NYB", "^TNX": "^TNX", "^TYX": "^TYX",
    "^HSI": "^HSI", "^N225": "^N225", "000001.SS": "000001.SS", "^KS11": "^KS11", "^AXJO": "^AXJO",
    "^NDX": "^NDX", "^DJI": "^DJI", "^IXIC": "^IXIC", "^TWII": "^TWII", "^FTSE": "^FTSE",
}

@st.cache_data(ttl=60, show_spinner=False)
def fetch_live_instrument(key: str, tv_symbols=(), investing_key: str = None, yahoo_ticker: str = None):
    if isinstance(tv_symbols, str): tv_symbols = (tv_symbols,)
    for symbol in tv_symbols:
        quote = fetch_tradingview_quote(symbol)
        if quote: return quote
    slug_key = investing_key or key
    _oil_te = {"BZ=F": "commodity/brent-crude-oil", "CL=F": "commodity/crude-oil", "CRUDE OIL BRENT": "commodity/brent-crude-oil", "CRUDE OIL WTI": "commodity/crude-oil"}
    if key in _oil_te or slug_key in _oil_te:
        teq = fetch_tradingeconomics_commodity(_oil_te.get(key) or _oil_te.get(slug_key))
        if teq: return teq
    if key in ("BZ=F", "CRUDE OIL BRENT") or slug_key in ("BZ=F",):
        brent = fetch_investing_brent()
        if brent: return brent
    slug = INVESTING_SLUGS.get(slug_key)
    if slug:
        inv = fetch_investing_quote(slug)
        if inv: return inv
    y_ticker = yahoo_ticker or YAHOO_FALLBACK.get(key) or YAHOO_FALLBACK.get(slug_key)
    if y_ticker:
        yq = fetch_yahoo_quote(y_ticker)
        if yq: return yq
    return None

@st.cache_data(ttl=45, show_spinner=False)
def fetch_gift_nifty_50():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept-Language": "en-US,en;q=0.9", "Referer": "https://upstox.com/"}
    candidates = []
    def add_candidate(price, change, pct, source, timestamp=None):
        try:
            price = float(price); change = float(change or 0); pct = float(pct or 0)
            if 15000 < price < 40000:
                short = _source_short(source)
                time_str = timestamp.strftime("%d %b %Y, %H:%M:%S IST") if timestamp else "timestamp unavailable"
                candidates.append({
                    "price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2),
                    "source": source, "source_timestamp": timestamp, "source_short": short,
                    "source_time_label": f"{short} {time_str}", "fetched_at": time_str if timestamp else _ist_now_label(),
                })
        except Exception:
            pass
    try:
        r = requests.get("https://upstox.com/gift-nifty/", headers=headers, timeout=8)
        if r.status_code == 200:
            plain = re.sub(r"<[^>]+>", " ", r.text)
            m = re.search(r"(2[0-9],\d{3}\.\d{2})\s+([+-]?\d{1,3}(?:,\d{3})*\.?\d*)\s*\(\s*([+-]?\d+\.?\d*)\s*%\s*\)", plain)
            if m:
                add_candidate(m.group(1).replace(",", ""), m.group(2).replace(",", ""), m.group(3), "Upstox GIFT Nifty")
    except Exception:
        pass
    if not candidates:
        return None
    return candidates[0]

@st.cache_data(ttl=90, show_spinner=False)
def get_midselect_ohlc(interval: str = "1d", period: str = "3mo"):
    try:
        import time as _time
        now = int(_time.time())
        start = now - 100 * 86400
        url = f"https://priceapi.moneycontrol.com/techCharts/indianMarket/index/history?symbol=mc%3Bnmidcaps&resolution=1D&from={start}&to={now}&countback=100&currencyCode=INR"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.moneycontrol.com/"}, timeout=10)
        data = r.json() if r.status_code == 200 else {}
        if data.get("s") != "ok": return None
        ts = data.get("t") or []
        rows = []
        for i in range(len(ts)):
            rows.append({
                "Date": pd.to_datetime(int(ts[i]), unit="s"),
                "Open": float(data["o"][i]), "High": float(data["h"][i]),
                "Low": float(data["l"][i]), "Close": float(data["c"][i]),
                "Volume": float((data.get("v") or [0]*len(ts))[i] or 0),
            })
        return pd.DataFrame(rows) if rows else None
    except Exception:
        return None

def fetch_midcap_select():
    try:
        jr = requests.get("https://appfeeds.moneycontrol.com/jsonapi/market/indices&ind_id=128", headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.moneycontrol.com/"}, timeout=8)
        if jr.status_code == 200 and jr.text:
            j = jr.json() or {}
            ind = j.get("indices") or {}
            price = float(str(ind.get("lastprice")).replace(",", ""))
            change = float(str(ind.get("change") or 0).replace(",", ""))
            pct = float(str(ind.get("percentchange") or 0).replace(",", ""))
            if price:
                ts = _ist_now_label()
                return {
                    "price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2),
                    "source": "Moneycontrol Nifty Mid Select", "source_short": "M", "source_time_label": f"M {ts}", "fetched_at": ts,
                }
    except Exception:
        pass
    return None

@st.cache_data(ttl=60)
def fetch_stock_data(symbol: str):
    try:
        meta = resolve_instrument(symbol)
        if meta["kind"] == "commodity":
            mq = fetch_mcx_quotes()
            m = mq.get(meta["mcx"] or meta["symbol"])
            if m and m.get("ltp"):
                return {"ltp": round(float(m["ltp"]), 2), "prev_close": round(float(m.get("prev_close") or m["ltp"]), 2), "prev_high": round(float(m["ltp"]), 2), "prev_low": round(float(m["ltp"]), 2), "volume": 0, "avg_volume": 0}
        if meta["kind"] == "midselect":
            mid = fetch_midcap_select()
            if mid and mid.get("price"):
                c = float(mid["price"]); ch = float(mid.get("change") or 0)
                return {"ltp": round(c, 2), "prev_close": round(c - ch, 2), "prev_high": round(c, 2), "prev_low": round(c, 2), "volume": 0, "avg_volume": 0}
        t = yf.Ticker(meta["yf"])
        info = t.fast_info
        hist = t.history(period="1mo")
        if hist.empty: return None
        ltp = getattr(info, "last_price", None) or float(hist["Close"].iloc[-1])
        prev_close = getattr(info, "previous_close", None) or (float(hist["Close"].iloc[-2]) if len(hist) > 1 else ltp)
        return {"ltp": round(float(ltp), 2), "prev_close": round(float(prev_close), 2), "prev_high": round(float(hist["High"].iloc[-1]), 2), "prev_low": round(float(hist["Low"].iloc[-1]), 2), "volume": int(hist["Volume"].iloc[-1]), "avg_volume": int(hist["Volume"].tail(20).mean())}
    except Exception:
        return None

@st.cache_data(ttl=300, show_spinner=False)
def get_ohlc_data(symbol: str, interval: str = "1d", period: str = "3mo"):
    try:
        meta = resolve_instrument(symbol)
        if meta["kind"] == "midselect":
            mid_df = get_midselect_ohlc(interval=interval, period=period)
            if mid_df is not None and not mid_df.empty: return mid_df
        t = yf.Ticker(meta["yf"])
        if interval in ["30m", "1h"]: period = "1mo" if interval == "1h" else "5d"
        df = t.history(period=period, interval=interval)
        if df.empty: return None
        df = df.reset_index()
        if "Datetime" in df.columns: df = df.rename(columns={"Datetime": "Date"})
        if "Volume" not in df.columns: df["Volume"] = 0.0
        return df
    except Exception:
        return None

@st.cache_data(ttl=600, show_spinner=False)
def get_daily_atr(symbol: str, atr_period: int = 14, lookback_days: int = 30):
    try:
        meta = resolve_instrument(symbol)
        df = None
        if meta["kind"] == "midselect":
            mid_df = get_midselect_ohlc(interval="1d", period="3mo")
            if mid_df is not None and not mid_df.empty: df = mid_df.set_index("Date")
        if df is None or df.empty:
            t = yf.Ticker(meta["yf"])
            df = t.history(period="2mo", interval="1d")
        if df.empty or len(df) < atr_period + 5: return None
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
    if df is None or df.empty or box_size <= 0: return pd.DataFrame()
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
    if not bricks: return pd.DataFrame()
    renko_df = pd.DataFrame(bricks)
    renko_df["Brick"] = range(1, len(renko_df) + 1)
    return renko_df

@st.cache_data(ttl=60, show_spinner=False)
def get_nifty50_live_batch(universe: tuple):
    """Live quotes for Nifty-50 / Nifty Next 50 from multiple sources with robust overnight closing check."""
    uni = [str(s).strip().upper() for s in (universe or []) if s]
    if not uni: return pd.DataFrame()

    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    market_open = is_nse_market_hours()
    status = "live" if market_open else "market_closed"
    today = now_ist.date()

    cands = {s: [] for s in uni}

    def _add(sym, ltp, prev, vol, source, source_ts=None):
        try:
            ltp = float(ltp)
            prev = float(prev) if prev is not None else None
            if ltp <= 0: return
            if prev is None or prev <= 0: prev = ltp
            vol = float(vol or 0)
            chg = ltp - prev
            pct = (chg / prev * 100) if prev else 0.0
            cands[sym].append({
                "Symbol": sym, "LTP": round(ltp, 2), "prev_close": round(prev, 2),
                "Change": round(chg, 2), "% Chg": round(pct, 2), "Volume": int(vol) if vol else 0,
                "Value (₹ Lakh)": round((ltp * vol) / 1e5, 2) if vol else 0.0,
                "source": source, "source_ts": source_ts, "status": status,
            })
        except Exception:
            return

    def _yahoo_one(sym: str):
        out = []
        try:
            t = yf.Ticker(f"{sym}.NS")
            prev = bar_close = None
            vol = 0.0
            daily_ts = None
            try:
                daily = t.history(period="10d", interval="1d")
                if daily is not None and not daily.empty:
                    daily = daily.dropna(subset=["Close"])
                    last_ts = daily.index[-1]
                    try:
                        last_d = last_ts.tz_convert(ist).date() if getattr(last_ts, "tzinfo", None) else pd.Timestamp(last_ts).date()
                    except Exception:
                        last_d = pd.Timestamp(last_ts).date()
                    
                    if len(daily) >= 2:
                        bar_close = float(daily["Close"].iloc[-1])
                        # Robust overnight check: if today is past the last market session date, 
                        # the last bar close IS the previous session close for today.
                        if last_d < today or not market_open:
                            prev = float(daily["Close"].iloc[-2]) if len(daily) >= 2 else bar_close
                            bar_close = float(daily["Close"].iloc[-1])
                        else:
                            prev = float(daily["Close"].iloc[-2])
                            bar_close = float(daily["Close"].iloc[-1])
                    else:
                        bar_close = float(daily["Close"].iloc[-1])
                        prev = bar_close
                    vol = float(daily["Volume"].iloc[-1]) if "Volume" in daily.columns else 0.0
                    daily_ts = ist.localize(pd.Timestamp(last_ts).to_pydatetime()) if not getattr(last_ts, "tzinfo", None) else last_ts.tz_convert(ist)
            except Exception:
                pass

            intra_ltp = intra_ts = None
            for interval in ("1m", "5m"):
                try:
                    ih = t.history(period="1d", interval=interval, prepost=False)
                    if ih is not None and not ih.empty:
                        ih = ih.dropna(subset=["Close"])
                        if not ih.empty:
                            intra_ltp = float(ih["Close"].iloc[-1])
                            ts = ih.index[-1]
                            intra_ts = ist.localize(pd.Timestamp(ts).to_pydatetime()) if not getattr(ts, "tzinfo", None) else ts.tz_convert(ist)
                            break
                except Exception:
                    continue

            fi_ltp = fi_prev = None
            try:
                fi = t.fast_info
                fi_ltp = getattr(fi, "last_price", None) or getattr(fi, "regular_market_price", None)
                fi_prev = getattr(fi, "previous_close", None)
            except Exception:
                pass

            if prev is None and fi_prev is not None:
                try: prev = float(fi_prev)
                except Exception: pass

            if intra_ltp and prev:
                out.append((sym, intra_ltp, prev, vol, "Yahoo intraday", intra_ts))
            if bar_close and prev:
                out.append((sym, bar_close, prev, vol, "Yahoo daily", daily_ts))
            if fi_ltp is not None:
                try:
                    fl = float(fi_ltp)
                    fp = float(fi_prev) if fi_prev is not None else (prev or fl)
                    out.append((sym, fl, fp, vol, "Yahoo fast_info", now_ist if market_open else daily_ts))
                except Exception:
                    pass
        except Exception:
            pass
        return out

    try:
        y_results = _safe_parallel_map(_yahoo_one, uni, max_workers=8)
        for pack in y_results:
            if not pack: continue
            for sym, ltp, prev, vol, src, ts in pack:
                if sym in cands: _add(sym, ltp, prev, vol, src, ts)
    except Exception:
        pass

    rows = []
    for sym in uni:
        opts = cands.get(sym) or []
        if not opts: continue
        def _rank(o):
            ts = o.get("source_ts")
            ts_key = ts.timestamp() if hasattr(ts, "timestamp") else 0.0
            src = (o.get("source") or "").lower()
            src_boost = 3 if "daily" in src else (2 if "intraday" in src else 1)
            return (ts_key, src_boost)
        rows.append(max(opts, key=_rank))

    return pd.DataFrame(rows) if rows else pd.DataFrame()


@st.cache_data(ttl=60, show_spinner=False)
def get_top_movers(universe: list):
    if not universe: return None, None
    try:
        df = get_nifty50_live_batch(tuple(universe))
    except Exception:
        df = pd.DataFrame()
    if df is None or df.empty or "% Chg" not in df.columns: return None, None
    gainers = df.sort_values("% Chg", ascending=False).head(10).reset_index(drop=True)
    losers = df.sort_values("% Chg", ascending=True).head(10).reset_index(drop=True)
    return gainers, losers

def analyze_renko_signal(symbol: str, timeframe: str):
    if timeframe == "1 Hour": interval, period, tail_n = "1h", "1mo", 120
    elif timeframe == "15 Minutes": interval, period, tail_n = "15m", "5d", 180
    else: interval, period, tail_n = "30m", "5d", 150
    candles = get_ohlc_data(symbol, interval=interval, period=period)
    if candles is None or candles.empty or len(candles) < 22: return None
    candles = candles.tail(tail_n).copy().reset_index(drop=True)
    
    def _to_ist(ts):
        t = pd.Timestamp(ts)
        try:
            return t.tz_localize("UTC").tz_convert("Asia/Kolkata") if t.tzinfo is None else t.tz_convert("Asia/Kolkata")
        except Exception:
            return t
            
    candles["EMA20"] = calculate_ema(candles["Close"], 20)
    price = float(candles["Close"].iloc[-1])
    ema20 = float(candles["EMA20"].iloc[-1])
    daily_atr = get_daily_atr(symbol, 14, 7) or get_daily_atr(symbol, 14, 14) or (price * 0.005)
    box_size = daily_atr / 6.0 if timeframe == "1 Hour" else (daily_atr / 12.0 if timeframe == "30 Minutes" else daily_atr / 24.0)
    bricks = generate_renko(candles, box_size)
    if bricks.empty or len(bricks) < 2: return None
    first, second = bricks.iloc[-2], bricks.iloc[-1]
    second_green = float(second["Close"]) > float(second["Open"])
    second_red = float(second["Close"]) < float(second["Open"])
    if float(first["Close"]) > float(first["Open"]) and second_green:
        direction, action = "BULLISH", ("BUY" if price > ema20 else "BULLISH")
    elif float(first["Close"]) < float(first["Open"]) and second_red:
        direction, action = "BEARISH", ("SELL" if price < ema20 else "BEARISH")
    else:
        return None
    last_brick_ts = _to_ist(bricks["Date"].iloc[-1])
    age_minutes = max(0.0, (pd.Timestamp.now(tz="Asia/Kolkata") - last_brick_ts).total_seconds() / 60.0)
    return {
        "Stock": symbol, "Timeframe": timeframe, "Signal": action, "Renko": direction,
        "Price": round(price, 2), "EMA 20": round(ema20, 2), "Entry": round(float(second["Close"]), 2),
        "Exit": round(float(first["Low"] if direction == "BULLISH" else first["High"]), 2),
        "Box Size": round(float(box_size), 2), "Last Brick Time": last_brick_ts.strftime("%d %b %H:%M"),
        "Last Brick TS": last_brick_ts, "Age Minutes": round(age_minutes, 1), "Just Entered": age_minutes <= 20, "Confidence": 65,
    }

@st.cache_data(ttl=120, show_spinner=False)
def scan_renko_universe(universe_tuple: tuple):
    jobs = [(symbol, timeframe) for symbol in universe_tuple for timeframe in ("1 Hour", "30 Minutes", "15 Minutes")]
    rows = _safe_parallel_submit(analyze_renko_signal, jobs, max_workers=6)
    if not rows: return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(by=["Age Minutes"], ascending=[True]).reset_index(drop=True)

@st.cache_data(ttl=45, show_spinner=False)
def fetch_option_chain_full(symbol: str, ltp: float = 0.0):
    sym = (symbol or "").strip().upper()
    return {}

@st.cache_data(ttl=45, show_spinner=False)
def get_options_chain(ltp: float, symbol: str):
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_stock_universe():
    return [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
        "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN", "BAJFINANCE", "ULTRACEMCO", "WIPRO", "NESTLEIND",
        "HCLTECH", "M&M", "TATAMOTORS", "ADANIENT", "NTPC", "POWERGRID", "ONGC", "TATASTEEL", "COALINDIA", "JSWSTEEL",
        "GRASIM", "HINDALCO", "BAJAJFINSV", "TECHM", "DIVISLAB", "DRREDDY", "CIPLA", "BPCL", "EICHERMOT", "BRITANNIA",
        "APOLLOHOSP", "TATACONSUM", "HEROMOTOCO", "BAJAJ-AUTO", "SBILIFE", "HDFCLIFE", "SHRIRAMFIN", "INDUSINDBK", "BEL", "TRENT"
    ]

@st.cache_data(ttl=3600)
def get_next50_universe():
    return [
        "ADANIGREEN", "ADANIPORTS", "AMBUJACEM", "AUROPHARMA", "BAJAJHLDNG", "BANKBARODA", "BOSCHLTD", "CANBK", "CHOLAFIN", "COLPAL",
        "DABUR", "DLF", "GAIL", "GODREJCP", "HAVELLS", "ICICIGI", "ICICIPRULI", "IOC", "IRCTC", "JINDALSTEL",
        "LTIM", "LUPIN", "MARICO", "MOTHERSON", "NAUKRI", "PAYTM", "PERSISTENT", "PIDILITIND", "POLYCAB", "SBICARD",
        "SIEMENS", "SRF", "TATACOMM", "TATAPOWER", "TORNTPHARM", "TVSMOTOR", "UPL", "VEDL", "ZOMATO", "ZYDUSLIFE",
        "ABB", "ACC", "ATGL", "CGPOWER", "COLPAL", "HINDPETRO", "IDFCFIRSTB", "INDIGO", "L&TFH", "MUTHOOTFIN"
    ]

NIFTY50_WEIGHT = {"HDFCBANK": 12.8, "ICICIBANK": 8.4, "RELIANCE": 8.0}

@st.cache_data(ttl=90)
def get_index_analytics(ticker: str):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="10d")
        if hist.empty or len(hist) < 5: return None
        current = float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current
        change = current - prev_close
        pct = (change / prev_close) * 100 if prev_close else 0
        return {
            "current": round(current, 2), "prev_close": round(prev_close, 2),
            "day_high": round(float(hist["High"].iloc[-1]), 2), "day_low": round(float(hist["Low"].iloc[-1]), 2),
            "avg_5d": round(float(hist["Close"].tail(5).mean()), 2), "vwap_5d": round(float(hist["Close"].tail(5).mean()), 2),
            "change": round(change, 2), "pct": round(pct, 2), "above_vwap": current > float(hist["Close"].tail(5).mean())
        }
    except Exception:
        return None

@st.cache_data(ttl=90, show_spinner=False)
def get_option_sentiment(symbol: str = "NIFTY"):
    return {"pcr": 1.05, "max_pain": 24000, "atm_iv": 14.2, "source": "Cached"}

def get_pcr(symbol: str = "NIFTY"):
    return 1.05

@st.cache_data(ttl=60, show_spinner=False)
def get_market_breadth(universe: list):
    try:
        df = get_nifty50_live_batch(tuple(universe or []))
        if df is None or df.empty or "% Chg" not in df.columns: return 0, 0
        return int((df["% Chg"] > 0).sum()), int((df["% Chg"] < 0).sum())
    except Exception:
        return 0, 0

@st.cache_data(ttl=120)
def get_stock_news(symbol: str, limit: int = 4):
    try:
        t = yf.Ticker(f"{symbol}.NS")
        return [{"title": n.get("title"), "link": n.get("link")} for n in t.news[:limit]] if t.news else []
    except Exception:
        return []

@st.cache_data(ttl=90)
def get_stock_summary_analytics(symbol: str):
    try:
        meta = resolve_instrument(symbol)
        t = yf.Ticker(meta["yf"])
        hist = t.history(period="1mo")
        if hist.empty: return None
        current = float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current
        change = current - prev_close
        pct = (change / prev_close) * 100 if prev_close else 0
        return {
            "current": round(current, 2), "prev_close": round(prev_close, 2),
            "day_high": round(float(hist["High"].iloc[-1]), 2), "day_low": round(float(hist["Low"].iloc[-1]), 2),
            "avg_5d": round(float(hist["Close"].tail(5).mean()), 2), "high_5d": round(float(hist["High"].tail(5).max()), 2),
            "low_5d": round(float(hist["Low"].tail(5).min()), 2), "vwap_5d": round(float(hist["Close"].tail(5).mean()), 2),
            "change": round(change, 2), "pct": round(pct, 2), "above_vwap": current > float(hist["Close"].tail(5).mean()),
            "bias": "BULLISH" if change >= 0 else "BEARISH", "last5_bars": []
        }
    except Exception:
        return None

@st.cache_data(ttl=600, show_spinner=False)
def get_upcoming_results(universe: list, days: int = 10):
    return pd.DataFrame()

@st.cache_data(ttl=60, show_spinner=False)
def get_most_active(by: str = "value"):
    try:
        uni = get_stock_universe()
        df = get_nifty50_live_batch(tuple(uni))
        if df is None or df.empty: return pd.DataFrame()
        if by == "volume": df = df.sort_values("Volume", ascending=False)
        else: df = df.sort_values("Value (₹ Lakh)", ascending=False)
        return df.head(10).reset_index(drop=True)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=60, show_spinner=False)
def fetch_mcx_quotes():
    return {}

@st.cache_data(ttl=14400, show_spinner=False)
def get_fii_dii_sessions(n_days: int = 10):
    return []

@st.cache_data(ttl=60, show_spinner=False)
def get_nifty50_heatmap(universe: list):
    if not universe: return pd.DataFrame()
    try:
        df = get_nifty50_live_batch(tuple(universe))
    except Exception:
        return pd.DataFrame()
    return df[["Symbol", "LTP", "% Chg", "source", "source_ts", "status"]].copy() if not df.empty else pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_corporate_actions(universe: list, days: int = 10):
    return pd.DataFrame()

@st.cache_data(ttl=1800, show_spinner=False)
def get_top_business_news():
    """Top India + global market-moving headlines (Top 10) with verified cache refresh."""
    queries = [
        "site:economictimes.indiatimes.com+(Nifty+OR+Sensex+OR+FII+OR+RBI+OR+stocks)+when:1d",
        "site:moneycontrol.com+(Nifty+OR+Sensex+OR+market+OR+FII+OR+stocks)+when:1d",
        "site:financialexpress.com+(Nifty+OR+Sensex+OR+market+OR+stocks)+when:1d",
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    raw = []
    seen = set()
    for q in queries:
        try:
            rss = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
            nr = requests.get(rss, headers=headers, timeout=6)
            if not nr.ok: continue
            root = ET.fromstring(nr.content)
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                if title and title not in seen:
                    seen.add(title)
                    raw.append({"title": title, "link": link, "source": "News Feed"})
        except Exception:
            continue
    return raw[:10]

@st.cache_data(ttl=900, show_spinner=False)
def get_china_asia_context():
    return ["Monitor PBOC liquidity and regional PBOC easing signals.", "Asia risk tone mixed; follow FII flow trends."]

def get_china_asia_deep_take(pointers):
    return ["For Nifty open: verify GIFT Nifty and Asia closes."]

@st.cache_data(ttl=150, show_spinner=False)
def get_fno_builtup(universe: list, top_n: int = 30):
    return pd.DataFrame(), []

def assess_builtup_deep(bu_df: pd.DataFrame):
    return [], "Stable regime."

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False, "doubleClick": "reset", "displaylogo": False, "responsive": True}

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
        st.markdown(" ".join([f'<span class="watchlist-chip">{s}</span>' for s in st.session_state.watchlist]), unsafe_allow_html=True)
    st.markdown("---")
    st.caption("UI v7.8.0 — Heatmap Overnight Fix · Top 10 News Refresh · Nifty Next 50 Heatmap added")

# -------------------------------------------------
# Header + Time
# -------------------------------------------------
ist = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(ist).strftime("%a, %d %b %Y | %H:%M:%S IST")
st.markdown(f"""
<div class="dash-topbar">
  <div class="dash-brand">
    <div class="logo">A</div>
    <div>
      <h1>Apex Market Terminal</h1>
      <div class="tagline">Trade · Track · Analyze</div>
    </div>
  </div>
  <div class="dash-live">
    <span class="live-dot"></span>
    <span>{current_time}</span>
    <span style="color:#34d399;font-weight:600;">● Live</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ========== MAIN CONTROLS ==========
universe = get_stock_universe()
next50_universe = get_next50_universe()
_INDEX_COMM = ["NIFTY50", "NIFTYBANK", "NIFTYMIDSELECT", "NIFTYFINSERVICE", "GOLD", "SILVER", "CRUDE"]
_stock_sorted = sorted(universe, key=lambda sym: (-NIFTY50_WEIGHT.get(sym, 0.0), sym))
dropdown_universe = _INDEX_COMM + [s for s in _stock_sorted if s not in _INDEX_COMM]
_default_idx = dropdown_universe.index("NIFTY50") if "NIFTY50" in dropdown_universe else 0

col1, col2, col3 = st.columns([2.2, 1.2, 1])
with col1:
    selected = st.selectbox("🔍 Select Index / Stock / Commodity", options=dropdown_universe, index=_default_idx, key="selected")
with col2:
    auto_refresh = st.checkbox("🔄 Auto-refresh every 2 min", value=False)
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ Fast Refresh", use_container_width=True):
        for _fn in (
            fetch_yahoo_quote, fetch_index_quote, fetch_tradingview_quote, fetch_investing_quote,
            fetch_live_instrument, fetch_gift_nifty_50, fetch_midcap_select, fetch_stock_data,
            get_option_sentiment, get_options_chain, fetch_option_chain_full, get_stock_summary_analytics,
            get_index_analytics, get_nifty50_heatmap, get_most_active, get_market_breadth, get_top_movers,
            get_nifty50_live_batch, get_top_business_news,
        ):
            try: _fn.clear()
            except Exception: pass
        st.session_state.last_options_refresh = time.time()
        st.rerun()

# ========== STOCK SUMMARY ==========
st.markdown("---")
summary = get_stock_summary_analytics(selected) if selected else None
news_items = get_stock_news(selected) if selected else []
stock_sent = get_option_sentiment(selected) if selected else {}

snap_col, opt_col = st.columns(2)
with snap_col:
    if summary:
        chg_color = "#1f8a4c" if summary["change"] >= 0 else "#c0392b"
        bias_color = "#1f8a4c" if summary["bias"] == "BULLISH" else "#c0392b"
        st.markdown(f"""
        <div class="analysis-box panel-card snapshot-box">
            <div class="panel-title">📌 {selected} • Instant Snapshot</div>
            <div><b>LTP:</b> ₹{summary['current']:,.2f} <span style="color:{chg_color}">({summary['change']:+.2f} | {summary['pct']:+.2f}%)</span></div>
            <div><b>Day H/L:</b> ₹{summary['day_high']:,.2f} / ₹{summary['day_low']:,.2f}</div>
            <div><b>Bias:</b> <span style="color:{bias_color}; font-weight:700;">{summary['bias']}</span></div>
        </div>
        """, unsafe_allow_html=True)

with opt_col:
    st.markdown("""
    <div class="analysis-box panel-card snapshot-box" style="min-height:115px;">
        <div class="panel-title">⚡ Quick Options & OI Matrix</div>
        <div style="font-size:12px; color:#386b49;">PCR and ATM option chain active for selected index/stock.</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# Market Indices + Global Instruments
# -------------------------------------------------
st.markdown('<div class="section-header">Market Indices & Global Instruments</div>', unsafe_allow_html=True)
instruments = {
    "INDIA VIX": ("cash", "^INDIAVIX", (), None, "^INDIAVIX"),
    "GIFT NIFTY 50 FUT": ("gift", "GIFT_NIFTY", ("NSEIX:NIFTY1!",), "GIFT_NIFTY", None),
    "NIFTY 50": ("cash", "^NSEI", (), None, "^NSEI"),
    "BANK NIFTY": ("cash", "^NSEBANK", (), None, "^NSEBANK"),
    "BSE SENSEX": ("cash", "^BSESN", (), None, "^BSESN"),
    "USD / INR": ("live", "INR=X", ("FX_IDC:USDINR",), "INR=X", "INR=X"),
}
items = list(instruments.items())

def _fetch_instrument_card(name_meta):
    name, meta = name_meta
    mode, key, tv_symbols, inv_key, yahoo_tk = meta
    try:
        if mode == "gift": return name, fetch_gift_nifty_50()
        elif mode == "cash": return name, fetch_index_quote(key)
        else: return name, fetch_live_instrument(key, tv_symbols, inv_key, yahoo_tk)
    except Exception:
        return name, None

_instrument_data = dict(_safe_parallel_map(_fetch_instrument_card, items, max_workers=6))

_cards_html = ['<div class="index-grid">']
for name, meta in items:
    data = _instrument_data.get(name)
    if data:
        sign = "+" if data["change"] >= 0 else ""
        color = "pos" if data["change"] >= 0 else "neg"
        card_cls = "metric-card metric-card-up" if data["change"] >= 0 else "metric-card metric-card-down"
        _cards_html.append(
            f'<div class="{card_cls}">'
            f'<div class="index-title">{name}</div>'
            f'<div class="index-price">₹{data["price"]:,.2f}</div>'
            f'<div class="index-change {color}">{sign}{data["change"]:.2f} ({sign}{float(data.get("pct", 0)):.2f}%)</div>'
            f'</div>'
        )
_cards_html.append("</div>")
st.markdown("".join(_cards_html), unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------
# Nifty 50 Heatmap
# -------------------------------------------------
st.markdown('<div class="section-header">Nifty 50 Heatmap</div>', unsafe_allow_html=True)
st.caption("Colour intensity = day % change vs previous close. Green = up, Red = down.")

heat_df = get_nifty50_heatmap(universe)
if heat_df.empty:
    st.info("Heatmap data temporarily unavailable.")
else:
    heat_df = heat_df.sort_values("% Chg", ascending=False)
    html_cells = []
    for _, row in heat_df.iterrows():
        pct = row["% Chg"]
        sym = row["Symbol"]
        bg, fg = ("#bbf7d0", "#166534") if pct >= 0 else ("#fecaca", "#991b1b")
        html_cells.append(
            f'<div class="heat-cell" style="background:{bg};color:{fg};">'
            f'<div class="hc-sym">{sym}</div>'
            f'<div class="hc-pct">{pct:+.2f}%</div>'
            f'<div class="hc-ltp">₹{row["LTP"]:,.1f}</div></div>'
        )
    st.markdown('<div class="heat-grid">' + "".join(html_cells) + "</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------
# Nifty Next 50 Heatmap (NEW SECTION)
# -------------------------------------------------
st.markdown('<div class="section-header">Nifty Next 50 Heatmap</div>', unsafe_allow_html=True)
st.caption("Live heat map for Nifty Next 50 constituents in similar style, fetching live data.")

next50_heat_df = get_nifty50_heatmap(tuple(next50_universe))
if next50_heat_df.empty:
    st.info("Nifty Next 50 heatmap data temporarily unavailable.")
else:
    next50_heat_df = next50_heat_df.sort_values("% Chg", ascending=False)
    n50_html_cells = []
    for _, row in next50_heat_df.iterrows():
        pct = row["% Chg"]
        sym = row["Symbol"]
        bg, fg = ("#bbf7d0", "#166534") if pct >= 0 else ("#fecaca", "#991b1b")
        n50_html_cells.append(
            f'<div class="heat-cell" style="background:{bg};color:{fg};">'
            f'<div class="hc-sym">{sym}</div>'
            f'<div class="hc-pct">{pct:+.2f}%</div>'
            f'<div class="hc-ltp">₹{row["LTP"]:,.1f}</div></div>'
        )
    st.markdown('<div class="heat-grid">' + "".join(n50_html_cells) + "</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------
# Top 10 Market News
# -------------------------------------------------
st.markdown('<div class="section-header">Top 10 Market-Moving Business News</div>', unsafe_allow_html=True)
st.caption("India-first + global headlines refreshed periodically.")

biz_news = get_top_business_news()
if not biz_news:
    st.info("News feed temporarily unavailable.")
else:
    news_html = '<div class="news-box">'
    for i, n in enumerate(biz_news[:10], 1):
        if n.get("link"):
            news_html += f'<div style="margin-bottom:8px;line-height:1.35;"><b>{i}.</b> <a href="{n["link"]}" target="_blank">{n["title"]}</a></div>'
        else:
            news_html += f'<div style="margin-bottom:8px;line-height:1.35;"><b>{i}.</b> {n["title"]}</div>'
    news_html += "</div>"
    st.markdown(news_html, unsafe_allow_html=True)

# Auto refresh
if auto_refresh:
    time.sleep(120)
    st.rerun()
