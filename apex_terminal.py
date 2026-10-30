# APEX MARKET TERMINAL — UPDATED BUILD 2026-10-30 (v7.6.16)

# v7.6.16:

# 1) UNIFIED Instant Snapshot + Options Matrix into a single CSS Grid with align-items: stretch:

#    both rectangles now share identical height, width, padding, background, and borders.

# 2) Options meta line enlarged from 9px to 12px for high legibility without eye strain.

# 3) Mobile-responsive Open Interest chart with auto-margins, liquid strike clamping, and adaptive legend.

# 4) ALL prior features, scrapers, tickers, Renko scanner, Corporate Actions, and Built-Up cycles retained 100%.



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



            /* === Dashboard polish === */

            .dash-topbar {

                display: flex; align-items: center; justify-content: space-between;

                padding: 10px 4px 14px 4px; margin-bottom: 4px;

                border-bottom: 1px solid rgba(99,102,241,0.25);

            }

            .dash-brand {

                display: flex; align-items: center; gap: 10px;

            }

            .dash-brand .logo {

                width: 36px; height: 36px; border-radius: 10px;

                background: linear-gradient(135deg, #6366f1, #a855f7);

                display: flex; align-items: center; justify-content: center;

                font-size: 18px; font-weight: 800; color: #fff;

            }

            .dash-brand h1 {

                font-size: 22px !important; margin: 0 !important; padding: 0 !important;

                background: linear-gradient(90deg, #a5b4fc, #c4b5fd, #f0abfc);

                -webkit-background-clip: text; -webkit-text-fill-color: transparent;

                font-weight: 800 !important; line-height: 1.15;

            }

            .dash-brand .tagline {

                font-size: 11px; color: #94a3b8; letter-spacing: 0.4px;

            }

            .dash-live {

                display: flex; align-items: center; gap: 8px;

                font-size: 12px; color: #cbd5e1;

            }

            .live-dot {

                width: 8px; height: 8px; border-radius: 50%;

                background: #34d399; box-shadow: 0 0 8px #34d399;

                animation: pulse 1.6s ease-in-out infinite;

            }

            @keyframes pulse {

                0%, 100% { opacity: 1; }

                50% { opacity: 0.45; }

            }

            .panel-card {

                background: linear-gradient(145deg, rgba(30,41,59,0.92), rgba(15,23,42,0.96));

                border: 1px solid rgba(99,102,241,0.28);

                border-radius: 12px;

                padding: 14px 16px;

                margin-bottom: 12px;

                box-shadow: 0 4px 18px rgba(0,0,0,0.28);

            }

            .panel-title {

                font-size: 13px; font-weight: 700; color: #c7d2fe;

                letter-spacing: 0.3px; text-transform: uppercase;

                margin-bottom: 10px; display: flex; align-items: center; gap: 6px;

            }

            .metric-card {

                transition: transform 0.15s ease, border-color 0.15s ease;

            }

            .metric-card:hover {

                transform: translateY(-2px);

                border-color: rgba(129,140,248,0.55) !important;

            }

            .section-header {

                font-size: 16px !important; font-weight: 700;

                background: linear-gradient(90deg, #818cf8, #c084fc);

                -webkit-background-clip: text; -webkit-text-fill-color: transparent;

                margin-bottom: 10px; margin-top: 4px;

                padding-bottom: 4px;

                border-bottom: 1px solid rgba(99,102,241,0.15);

            }

            /* Tighter dataframe look */

            div[data-testid="stDataFrame"] {

                border-radius: 10px; overflow: hidden;

                border: 1px solid rgba(148,163,184,0.18);

            }

            /* Soft divider */

            .dash-divider {

                height: 1px; background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent);

                margin: 14px 0;

            }



            /* === v7.6.16: Unified Equal-Height Card Grid === */

            .equal-height-row {

                display: grid;

                grid-template-columns: repeat(2, minmax(0, 1fr));

                gap: 16px;

                align-items: stretch;

                width: 100%;

                margin-top: 4px;

                margin-bottom: 8px;

            }

            .equal-card-wrapper {

                display: flex;

                flex-direction: column;

                height: 100%;

            }

            .equal-card-header {

                font-size: 12px;

                font-weight: 600;

                line-height: 1.35;

                min-height: 20px;

                margin-bottom: 4px;

                color: #c7d2fe;

                padding-left: 2px;

            }

            .equal-card-box {

                flex: 1 1 auto;

                background: #eaf6ed !important;

                border: 1px solid #d3e9d8 !important;

                border-radius: 12px;

                padding: 14px 16px;

                color: #26332b !important;

                box-sizing: border-box;

                display: flex;

                flex-direction: column;

                justify-content: space-between;

                min-height: 185px;

            }

            .equal-card-box .panel-title {

                color: #386b49 !important;

                font-size: 13px;

                font-weight: 700;

                letter-spacing: 0.3px;

                text-transform: uppercase;

                margin-bottom: 8px;

                display: flex;

                align-items: center;

                gap: 6px;

            }

            .opt-scroll-table {

                width: 100%;

                max-height: 140px;

                overflow-y: auto;

                overflow-x: hidden;

                border-radius: 6px;

            }

            .opt-table {

                width: 100%;

                border-collapse: collapse;

                font-size: 11px;

                color: #26332b;

            }

            .opt-table th {

                position: sticky;

                top: 0;

                background: #eaf6ed;

                padding: 4px 8px;

                font-size: 10px;

                font-weight: 600;

                color: #386b49;

                border-bottom: 1px solid #d3e9d8;

                z-index: 1;

            }

            .opt-table td {

                padding: 3.5px 8px;

            }

            @media (max-width: 850px) {

                .equal-height-row {

                    grid-template-columns: 1fr;

                    gap: 12px;

                }

            }



            /* Responsive Heatmap Grid */

            .heat-grid {

                display: grid; grid-template-columns: repeat(5, minmax(0, 1fr));

                gap: 6px; width: 100%;

            }

            .heat-grid .heat-cell {

                width: auto !important; margin: 0 !important; padding: 8px 2px !important;

                min-height: 74px; display: flex; flex-direction: column;

                align-items: center; justify-content: center; gap: 2px;

                box-sizing: border-box; overflow: hidden; line-height: 1.2;

            }

            .heat-grid .hc-sym {

                font-size: clamp(11px, 2.9vw, 13px); font-weight: 700;

                white-space: nowrap; max-width: 100%; letter-spacing: -0.2px;

            }

            .heat-grid .hc-pct { font-size: clamp(11px, 3.0vw, 13px); font-weight: 600; white-space: nowrap; }

            .heat-grid .hc-ltp { font-size: clamp(10px, 2.6vw, 12px); font-weight: 500; opacity: 0.92; white-space: nowrap; }

            @media (max-width: 900px) { .heat-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }

            @media (max-width: 600px) { .heat-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; } }



            /* Index cards responsive grid */

            .index-grid {

                display: grid;

                grid-template-columns: repeat(6, minmax(0, 1fr));

                gap: 8px;

                width: 100%;

            }

            .index-grid .metric-card {

                min-height: 72px !important;

                padding: 6px 4px !important;

                overflow: hidden;

            }

            .index-grid .index-title {

                font-size: 9px !important;

                white-space: nowrap;

                overflow: hidden;

                text-overflow: ellipsis;

                max-width: 100%;

                display: block;

            }

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



            /* Results date-strip */

            .res-date-strip {

                display: grid;

                grid-template-columns: repeat(auto-fit, minmax(72px, 1fr));

                gap: 6px;

                width: 100%;

            }

            .res-day {

                background: rgba(30,41,59,0.75);

                border: 1px solid rgba(99,102,241,0.28);

                border-radius: 8px;

                padding: 6px 4px;

                text-align: center;

                min-height: 64px;

            }

            .res-day .rd-date {

                font-size: 11px; font-weight: 700; color: #c7d2fe;

                margin-bottom: 4px; white-space: nowrap;

            }

            .res-day .rd-syms {

                font-size: 10px; font-weight: 600; color: #e2e8f0;

                line-height: 1.25; word-break: break-word;

            }

            .res-day.empty .rd-syms { color: #64748b; font-weight: 500; }

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

            .equal-height-row {

                display: grid;

                grid-template-columns: repeat(2, minmax(0, 1fr));

                gap: 16px;

                align-items: stretch;

                width: 100%;

                margin-top: 4px;

                margin-bottom: 8px;

            }

            .equal-card-wrapper { display: flex; flex-direction: column; height: 100%; }

            .equal-card-header {

                font-size: 12px; font-weight: 600; line-height: 1.35;

                min-height: 20px; margin-bottom: 4px; color: #3730a3;

                padding-left: 2px;

            }

            .equal-card-box {

                flex: 1 1 auto;

                background: #eaf6ed !important;

                border: 1px solid #d3e9d8 !important;

                border-radius: 12px;

                padding: 14px 16px;

                color: #26332b !important;

                box-sizing: border-box;

                display: flex;

                flex-direction: column;

                justify-content: space-between;

                min-height: 185px;

            }

            .equal-card-box .panel-title {

                color: #386b49 !important; font-size: 13px; font-weight: 700;

                letter-spacing: 0.3px; text-transform: uppercase; margin-bottom: 8px;

            }

            .opt-scroll-table {

                width: 100%; max-height: 140px; overflow-y: auto; overflow-x: hidden; border-radius: 6px;

            }

            .opt-table { width: 100%; border-collapse: collapse; font-size: 11px; color: #26332b; }

            .opt-table th {

                position: sticky; top: 0; background: #eaf6ed;

                padding: 4px 8px; font-size: 10px; font-weight: 600;

                color: #386b49; border-bottom: 1px solid #d3e9d8; z-index: 1;

            }

            .opt-table td { padding: 3.5px 8px; }

            @media (max-width: 850px) { .equal-height-row { grid-template-columns: 1fr; gap: 12px; } }

            

            .index-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; width: 100%; }

            .metric-card-up { background: #eaf6ed !important; border: 1px solid #d3e9d8 !important; }

            .metric-card-down { background: #fbeeee !important; border: 1px solid #f0d6d6 !important; }

            .metric-card-up .index-title, .metric-card-down .index-title { color: #52615a !important; }

            .metric-card-up .index-price, .metric-card-down .index-price { color: #26332b !important; }

            .metric-card-up .index-change { color: #386b49 !important; }

            .metric-card-down .index-change { color: #8a4545 !important; }

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

                hist = t.history(period=period, interval=interval, prepost=True) if interval else t.history(period=period)

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

                    prev = float(daily["Close"].iloc[-2]) if daily is not None and len(daily) >= 2 else float(hist["Close"].iloc[-2]) if len(hist) > 1 else price

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

            "FX_IDC": "forex", "OANDA": "forex", "HSI": "hongkong", "TSE": "japan", "SSE": "china",

            "KRX": "korea", "ASX": "australia", "TWSE": "taiwan", "LSE": "uk", "FTSE": "uk"

        }

        region = region_map.get(exchange, "america")

        url = f"https://scanner.tradingview.com/{region}/scan"

        payload = {"symbols": {"tickers": [tv_symbol], "query": {"types": []}}, "columns": ["close", "change", "change_abs"]}

        headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json", "Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/"}

        r = requests.post(url, json=payload, headers=headers, timeout=6)

        if r.status_code != 200: return None

        rows = r.json().get("data", [])

        if not rows or not rows[0].get("d"): return None

        vals = rows[0]["d"]

        price, pct, change = vals[0], vals[1], vals[2]

        if price is None or float(price) <= 0: return None

        if change is None and pct is not None: change = float(price) * float(pct) / 100

        if pct is None and change is not None: pct = (float(change) / (float(price) - float(change)) * 100) if float(price) != float(change) else 0

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

            "Accept-Language": "en-US,en;q=0.9",

            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",

        }

        r = requests.get(url, headers=headers, timeout=6)

        if r.status_code != 200: return None

        html = r.text

        def extract(pattern):

            m = re.search(pattern, html, flags=re.I | re.S)

            return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else None



        price_text = extract(r'data-test=["\']instrument-price-last["\'][^>]*>(.*?)</') or (re.search(r'["\']last["\']\s*:\s*["\']?([0-9,]+\.?[0-9]*)', html, flags=re.I).group(1) if re.search(r'["\']last["\']\s*:\s*["\']?([0-9,]+\.?[0-9]*)', html, flags=re.I) else None)

        if not price_text: return None



        def number(value):

            if not value: return None

            cleaned = re.sub(r"[^0-9.+-]", "", value.replace(",", ""))

            try: return float(cleaned) if cleaned not in ("", "+", "-") else None

            except ValueError: return None



        price = number(price_text)

        change = number(extract(r'data-test=["\']instrument-price-change["\'][^>]*>(.*?)</')) or 0.0

        pct = number(extract(r'data-test=["\']instrument-price-change-percent["\'][^>]*>(.*?)</')) or 0.0

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

        headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}

        r = requests.get(url, headers=headers, timeout=8)

        if r.status_code != 200: return None

        html = r.text

        m_price = re.search(r'Actual\s*</[^>]*>\s*([0-9,]+(?:\.[0-9]+)?)', html, re.I | re.S) or re.search(r'traded at\s+([0-9,]+(?:\.[0-9]+)?)', html, re.I)

        price = float(m_price.group(1).replace(",", "")) if m_price else None

        m_chg = re.search(r'Daily Change\s*</[^>]*>\s*([+-]?[0-9,]+(?:\.[0-9]+)?)\s+([+-]?[0-9.]+)\s*%', html, re.I | re.S)

        change, pct = (float(m_chg.group(1).replace(",", "")), float(m_chg.group(2))) if m_chg else (0.0, 0.0)

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

        headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}

        r = requests.get(url, headers=headers, timeout=8)

        if r.status_code != 200: return None

        html = r.text

        m = re.search(r'id=["\']market_last["\'][^>]*>([^<]+)', html, re.I)

        price = float(re.sub(r"[^0-9.]", "", m.group(1))) if m else None

        if price is None or not (20.0 <= price <= 250.0): return None

        cm = re.search(r'id=["\']market_daily_chg["\'][^>]*>([^<]+)', html, re.I)

        change = float(re.sub(r"[^0-9.+-]", "", cm.group(1))) if cm else 0.0

        pct = (change / (price - change) * 100) if (price - change) else 0.0

        src = f"TradingEconomics ({slug})"

        ts = _ist_now_label()

        return {

            "price": round(price, 2), "change": round(change, 2), "pct": round(pct, 2),

            "source": src, "source_short": _source_short(src), "source_time_label": ts, "fetched_at": ts,

        }

    except Exception:

        return None



@st.cache_data(ttl=45, show_spinner=False)

def fetch_investing_brent():

    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}

    try:

        r = requests.get("https://in.investing.com/commodities/brent-oil", headers=headers, timeout=8)

        if r.status_code == 200:

            m = re.search(r'data-test=["\']instrument-price-last["\'][^>]*>(.*?)</', r.text)

            if m:

                p = float(re.sub(r"[^0-9.]", "", m.group(1)))

                if 50.0 <= p <= 200.0:

                    ts = _ist_now_label()

                    return {"price": round(p, 2), "change": 0.0, "pct": 0.0, "source": "Investing.com (Brent)", "source_short": "I", "source_time_label": ts, "fetched_at": ts}

    except Exception:

        pass

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

    "^NDX": "^NDX", "^DJI": "^DJI", "^IXIC": "^IXIC", "^TWII": "^TWII", "^FTSE": "^FTSE"

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

    slug = INVESTING_SLUGS.get(slug_key)

    if slug:

        inv = fetch_investing_quote(slug)

        if inv: return inv

    oil_keys = {"BZ=F", "CL=F", "CRUDE OIL BRENT", "CRUDE OIL WTI"}

    if key not in oil_keys and slug_key not in oil_keys:

        y_ticker = yahoo_ticker or YAHOO_FALLBACK.get(key) or YAHOO_FALLBACK.get(slug_key)

        if y_ticker:

            yq = fetch_yahoo_quote(y_ticker)

            if yq: return yq

    return None



@st.cache_data(ttl=45, show_spinner=False)

def fetch_gift_nifty_50():

    try:

        r = requests.get("https://upstox.com/gift-nifty/", headers={"User-Agent": "Mozilla/5.0"}, timeout=8)

        if r.status_code == 200:

            m = re.search(r"(2[0-9],\d{3}\.\d{2})\s+([+-]?\d{1,3}(?:,\d{3})*\.?\d*)\s*\(\s*([+-]?\d+\.?\d*)\s*%\s*\)", r.text)

            if m:

                ts = _ist_now_label()

                return {"price": float(m.group(1).replace(",", "")), "change": float(m.group(2).replace(",", "")), "pct": float(m.group(3)), "source": "Upstox GIFT Nifty", "source_short": "U", "source_time_label": f"U {ts}", "fetched_at": ts}

    except Exception:

        pass

    quote = fetch_tradingview_quote("NSEIX:NIFTY1!")

    if quote:

        quote["source"] = "TradingView (NSEIX:NIFTY1!)"

        quote["source_short"] = "T"

        return quote

    return None



@st.cache_data(ttl=45, show_spinner=False)

def fetch_midcap_select():

    try:

        inv = fetch_investing_quote("indices/nifty-midcap-select")

        if inv and inv.get("price"):

            inv["source"] = "Investing.com Nifty Midcap Select"

            inv["source_short"] = "I"

            return inv

    except Exception:

        pass

    return None



# -------------------------------------------------

# Header

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



# Main Controls

universe = get_stock_universe()

dropdown_universe = sorted(universe, key=lambda sym: (-NIFTY50_WEIGHT.get(sym, 0.0), sym))

col1, col2, col3 = st.columns([2.2, 1.2, 1])

with col1:

    selected = st.selectbox("🔍 Select Stock (NSE)", options=dropdown_universe, index=0, key="selected")

with col2:

    auto_refresh = st.checkbox("🔄 Auto-refresh every 2 min", value=False)

with col3:

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚡ Fast Refresh", use_container_width=True):

        st.rerun()



# -------------------------------------------------

# UNIFIED EQUAL-HEIGHT CARDS: SNAPSHOT + OPTIONS MATRIX

# -------------------------------------------------

st.markdown("---")

summary = get_stock_summary_analytics(selected)

news_items = get_stock_news(selected)

stock_sent = get_option_sentiment(selected) or {}

stock_pcr = stock_sent.get("pcr")

stock_mp = stock_sent.get("max_pain")

stock_pcr_src = stock_sent.get("source") or ""



_spot_for_opt = float(summary["current"]) if summary and summary.get("current") else 0.0

_chain_full = fetch_option_chain_full(selected, _spot_for_opt)

_opt_matrix = get_options_chain(_spot_for_opt, selected)



# 1) Build Left Card HTML (Snapshot)

snap_card_content = ""

if summary:

    bias_color = "#1f8a4c" if summary["bias"] == "BULLISH" else "#c0392b" if summary["bias"] == "BEARISH" else "#b7791f"

    chg_color = "#1f8a4c" if summary["change"] >= 0 else "#c0392b"

    pcr_text = f"<b>PCR (OI):</b> {stock_pcr:.3f}" if stock_pcr is not None else "<b>PCR (OI):</b> —"

    mp_text = f"<b>Max Pain:</b> ₹{stock_mp:,.0f}" if stock_mp is not None else "<b>Max Pain:</b> —"

    

    bars = summary.get("last5_bars") or []

    cells = []

    if bars:

        for b in bars:

            bg = "#059669" if b.get("color") == "green" else "#dc2626"

            pct_val = b.get("pct", 0)

            cells.append(

                f'<div style="display:inline-block;width:44px;text-align:center;margin:0 2px;">'

                f'<div style="width:14px;height:24px;background:{bg};border-radius:2px;margin:0 auto 3px auto;"></div>'

                f'<div style="font-size:10px;color:#52615a;">{b.get("date", "")}</div>'

                f'<div style="font-size:10px;font-weight:700;color:#26332b;">{b.get("close", 0)}</div>'

                f'<div style="font-size:10px;font-weight:600;color:#3b4a42;">{pct_val:+.1f}%</div></div>'

            )

    bar_html = f'<div style="display:flex;align-items:flex-end;gap:1px;margin-top:6px;">{"".join(cells)}</div>'



    snap_card_content = f"""

    <div>

        <div class="panel-title">📌 {selected} • Instant Snapshot</div>

        <div style="display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12px;line-height:1.35;margin-bottom:6px;">

            <div><b>LTP:</b> ₹{summary['current']:,.2f} <span style="color:{chg_color}">({summary['change']:+.2f} | {summary['pct']:+.2f}%)</span></div>

            <div><b>Day H/L:</b> ₹{summary['day_high']:,.2f} / ₹{summary['day_low']:,.2f}</div>

            <div><b>5D Avg:</b> ₹{summary['avg_5d']:,.2f}</div>

            <div><b>5D H/L:</b> ₹{summary['high_5d']:,.2f} / ₹{summary['low_5d']:,.2f}</div>

            <div><b>5D VWAP:</b> ₹{summary['vwap_5d']:,.2f} {'✅' if summary['above_vwap'] else '❌'}</div>

            <div><b>Bias:</b> <span style="color:{bias_color};font-weight:700;">{summary['bias']}</span></div>

            <div>{pcr_text}</div>

            <div>{mp_text}</div>

        </div>

    </div>

    <div style="margin-top:4px;">{bar_html}</div>

    """

else:

    snap_card_content = f"<div class='panel-title'>📌 {selected} • Instant Snapshot</div><div>Data temporarily unavailable</div>"



# 2) Build Right Card HTML (Options Matrix)

_exp_lbl = _chain_full.get("expiry") or "—"

_src_lbl = _chain_full.get("source") or "Feed"

_mp_lbl = f" · Max pain {_chain_full.get('max_pain')}" if _chain_full.get("max_pain") else ""



opt_header_text = (

    f"ATM ±6 · exp {_exp_lbl} · {_src_lbl} · Spot ₹{_spot_for_opt:,.2f}{_mp_lbl}"

    if _spot_for_opt else f"ATM ±6 · exp {_exp_lbl}"

)



opt_card_content = ""

if _opt_matrix is None or _opt_matrix.empty:

    opt_card_content = "<div style='padding:20px;text-align:center;color:#52615a;'>Option premiums temporarily unavailable.</div>"

else:

    rows_td = []

    for _, r in _opt_matrix.iterrows():

        is_atm = bool(r.get("_is_atm"))

        row_bg = "background:#c8e6c9;color:#1b5e20;font-weight:700;" if is_atm else ""

        rows_td.append(

            f"<tr style='{row_bg}'>"

            f"<td style='text-align:right;'>₹{float(r['Call Price (CE)']):,.2f}</td>"

            f"<td style='text-align:center;font-weight:600;'>₹{float(r['Strike Price']):,.0f}</td>"

            f"<td style='text-align:right;'>₹{float(r['Put Price (PE)']):,.2f}</td>"

            f"</tr>"

        )

    opt_card_content = f"""

    <div class="opt-scroll-table">

        <table class="opt-table">

            <thead>

                <tr>

                    <th style="text-align:right;">Call (CE)</th>

                    <th style="text-align:center;">Strike</th>

                    <th style="text-align:right;">Put (PE)</th>

                </tr>

            </thead>

            <tbody>

                {''.join(rows_td)}

            </tbody>

        </table>

    </div>

    <div style="font-size:10px;color:#52615a;text-align:right;margin-top:4px;">Centered around current ATM</div>

    """



# 3) Render Single HTML Grid

st.markdown(f"""

<div class="equal-height-row">

    <div class="equal-card-wrapper">

        <div class="equal-card-header" style="visibility:hidden;">.</div>

        <div class="equal-card-box">

            {snap_card_content}

        </div>

    </div>

    <div class="equal-card-wrapper">

        <div class="equal-card-header">{opt_header_text}</div>

        <div class="equal-card-box">

            {opt_card_content}

        </div>

    </div>

</div>

""", unsafe_allow_html=True)



if news_items:

    with st.expander(f"📰 Latest News on {selected}", expanded=False):

        for n in news_items:

            st.markdown(f"- [{n['title']}]({n['link']})" if n.get("link") else f"- {n['title']}")



# -------------------------------------------------

# Open Interest Chart (Mobile Responsive)

# -------------------------------------------------

_oi_rows = _chain_full.get("rows") or []

if _oi_rows:

    st.markdown(f"""

    <div class="analysis-box panel-card" style="margin-top:12px;background:#eaf6ed;border:1px solid #d3e9d8;border-radius:12px;padding:12px;">

        <div class="panel-title" style="color:#386b49;font-weight:700;margin-bottom:4px;">📊 Open Interest by Strike · {selected} · exp {_exp_lbl}</div>

    """, unsafe_allow_html=True)

    

    oi_df = pd.DataFrame(_oi_rows)

    und = float(_chain_full.get("underlying") or _spot_for_opt or 0)

    

    if und > 0 and len(oi_df) > 14:

        oi_df["dist"] = (oi_df["strike"] - und).abs()

        plot_df = oi_df.sort_values("dist").head(14).sort_values("strike").drop(columns=["dist"]).copy()

    else:

        plot_df = oi_df.copy()

        

    fig_oi = go.Figure()

    fig_oi.add_trace(go.Bar(

        x=plot_df["strike"], y=plot_df["ce_oi"], name="Call OI",

        marker_color="#059669", opacity=0.9

    ))

    fig_oi.add_trace(go.Bar(

        x=plot_df["strike"], y=plot_df["pe_oi"], name="Put OI",

        marker_color="#dc2626", opacity=0.9

    ))

    

    shapes, annotations = [], []

    atm_v = _chain_full.get("atm")

    mp_v = _chain_full.get("max_pain")

    

    if atm_v:

        shapes.append(dict(type="line", x0=atm_v, x1=atm_v, y0=0, y1=1, yref="paper", line=dict(color="#d97706", width=2, dash="dash")))

        annotations.append(dict(x=atm_v, y=1.05, yref="paper", text=f"ATM {atm_v}", showarrow=False, font=dict(size=11, color="#d97706")))

    if mp_v and mp_v != atm_v:

        shapes.append(dict(type="line", x0=mp_v, x1=mp_v, y0=0, y1=1, yref="paper", line=dict(color="#7c3aed", width=2, dash="dot")))

        annotations.append(dict(x=mp_v, y=1.05, yref="paper", text=f"MP {mp_v}", showarrow=False, font=dict(size=11, color="#7c3aed")))

        

    fig_oi.update_layout(

        barmode="group",

        height=320,

        margin=dict(l=10, r=10, t=32, b=40),

        template="plotly_white",

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(255,255,255,0.4)",

        font=dict(color="#1e293b", size=11),

        legend=dict(

            orientation="h", yanchor="bottom", y=1.02, x=1, xanchor="right",

            font=dict(size=11, color="#1e293b")

        ),

        shapes=shapes,

        annotations=annotations,

        xaxis=dict(

            title=dict(text="Strike", font=dict(size=11)),

            tickmode="linear",

            tickangle=-45,

            automargin=True,

            showgrid=True,

            gridcolor="rgba(0,0,0,0.06)"

        ),

        yaxis=dict(

            title=dict(text="OI", font=dict(size=11)),

            automargin=True,

            showgrid=True,

            gridcolor="rgba(0,0,0,0.06)"

        ),

        dragmode=False

    )

    st.plotly_chart(fig_oi, use_container_width=True, config=PLOTLY_CONFIG)

    st.markdown("</div>", unsafe_allow_html=True)



# -------------------------------------------------

# Market Indices + Global Instruments

# -------------------------------------------------

st.markdown('<div class="section-header">Market Indices & Global Instruments</div>', unsafe_allow_html=True)



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

    "CRUDE OIL WTI": ("live", "CL=F", ("TVC:USOIL", "NYMEX:CL1!"), "CL=F", None),

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



def _fetch_instrument_card(name_meta):

    name, meta = name_meta

    mode, key, tv_symbols, inv_key, yahoo_tk = meta

    try:

        if mode == "gift": data = fetch_gift_nifty_50()

        elif mode == "midselect": data = fetch_midcap_select()

        elif mode == "cash": data = fetch_index_quote(key)

        else: data = fetch_live_instrument(key, tv_symbols, inv_key, yahoo_tk)

    except Exception:

        data = None

    return name, data



_instrument_data = {}

with ThreadPoolExecutor(max_workers=12) as _pool:

    for _name, _data in _pool.map(_fetch_instrument_card, items):

        _instrument_data[_name] = _data



_cards_html = ['<div class="index-grid">']

for name, meta in items:

    mode, key, tv_symbols, inv_key, yahoo_tk = meta

    data = _instrument_data.get(name)

    if data:

        sign = "+" if data["change"] >= 0 else ""

        color = "pos" if data["change"] >= 0 else "neg"

        card_cls = "metric-card metric-card-up" if data["change"] >= 0 else "metric-card metric-card-down"

        price_str = f"{data['price']:.2f}%" if name in yield_keys else (f"₹{data['price']:,.2f}" if (mode in ("cash", "gift", "midselect") and name not in vix_keys) else f"{data['price']:,.2f}")

        change_str = f"{sign}{data['change']:.2f}"

        short = data.get("source_short") or _source_short(data.get("source", ""))

        existing = (data.get("source_time_label") or "").strip()

        time_label = existing if (existing and short and existing.upper().startswith(short.upper() + " ")) else (f"{short} {existing or _ist_now_label()}")

        display_name = name if len(name) <= 18 else (name[:16] + "…")

        _cards_html.append(

            f'<div class="{card_cls}">'

            f'<div class="index-title" title="{name}">{display_name}</div>'

            f'<div class="index-price">{price_str}</div>'

            f'<div class="index-change {color}">{change_str} ({sign}{float(data.get("pct", 0)):.2f}%)</div>'

            f'<div style="font-size:7px;color:#8a8a8a;margin-top:2px;">{time_label}</div>'

            f'</div>'

        )

    else:

        display_name = name if len(name) <= 18 else (name[:16] + "…")

        _cards_html.append(

            f'<div class="metric-card">'

            f'<div class="index-title" title="{name}">{display_name}</div>'

            f'<div class="index-price" style="font-size:12px; color:#94a3b8; padding-top:8px;">Unavailable</div>'

            f'</div>'

        )

_cards_html.append("</div>")

st.markdown("".join(_cards_html), unsafe_allow_html=True)



st.markdown("---")



# -------------------------------------------------

# Global Opening Commentary & Index Analytics

# -------------------------------------------------

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



china_asia = get_china_asia_context()

deep = get_china_asia_deep_take(china_asia)

st.markdown("#### 🌏 Asia & Global Scenario Take")

for p in china_asia: st.markdown(f"• {p}")

for d in deep: st.markdown(f"→ {d}")



st.markdown("---")



# -------------------------------------------------

# Market Breadth, PCR, Max Pain & IV

# -------------------------------------------------

st.markdown('<div class="section-header">📊 Market Breadth, PCR, Max Pain & IV</div>', unsafe_allow_html=True)

bullish_cnt, bearish_cnt = get_market_breadth(universe)

nifty_sent = get_option_sentiment("NIFTY") or {}

bank_sent = get_option_sentiment("BANKNIFTY") or {}



b1, b2, b3, b4 = st.columns(4)

b1.metric("🟢 Bullish Stocks", bullish_cnt)

b2.metric("🔴 Bearish Stocks", bearish_cnt)

b3.metric("Nifty PCR (OI)", f"{nifty_sent.get('pcr'):.3f}" if nifty_sent.get("pcr") else "—")

b4.metric("Bank Nifty PCR (OI)", f"{bank_sent.get('pcr'):.3f}" if bank_sent.get("pcr") else "—")



m1, m2, m3, m4 = st.columns(4)

m1.metric("Nifty Max Pain", f"{nifty_sent.get('max_pain'):,.0f}" if nifty_sent.get("max_pain") else "—")

m2.metric("Nifty ATM IV", f"{nifty_sent.get('atm_iv'):.1f}%" if nifty_sent.get("atm_iv") else "—")

m3.metric("Bank Nifty Max Pain", f"{bank_sent.get('max_pain'):,.0f}" if bank_sent.get("max_pain") else "—")

m4.metric("Bank Nifty ATM IV", f"{bank_sent.get('atm_iv'):.1f}%" if bank_sent.get("atm_iv") else "—")



st.markdown("---")



# -------------------------------------------------

# Stock Analytics & Interactive Price Charts

# -------------------------------------------------

st.markdown(f'<div class="section-header">📌 {selected} • Technical & Renko Charts</div>', unsafe_allow_html=True)

metrics = fetch_stock_data(selected)

if metrics is None:

    st.error(f"Unable to fetch data for {selected}.NS")

    st.stop()



m1, m2, m3, m4 = st.columns(4)

m1.metric("Last Traded Price", f"₹{metrics['ltp']:,.2f}")

m2.metric("Day High", f"₹{metrics['prev_high']:,.2f}")

m3.metric("Day Low", f"₹{metrics['prev_low']:,.2f}")

m4.metric("Previous Close", f"₹{metrics['prev_close']:,.2f}")



timeframe = st.radio("Timeframe", ["Daily", "1 Hour", "30 Minutes", "15 Minutes"], index=0, horizontal=True)

interval = {"Daily": "1d", "1 Hour": "1h", "30 Minutes": "30m", "15 Minutes": "15m"}[timeframe]

period = "3mo" if timeframe == "Daily" else ("1mo" if timeframe == "1 Hour" else "5d")

candle_df = get_ohlc_data(selected, interval=interval, period=period)



if candle_df is not None and not candle_df.empty:

    candle_df["EMA20"] = calculate_ema(candle_df["Close"], 20)

    candle_df["EMA50"] = calculate_ema(candle_df["Close"], 50)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.72, 0.28])

    fig.add_trace(go.Candlestick(x=candle_df["Date"], open=candle_df["Open"], high=candle_df["High"], low=candle_df["Low"], close=candle_df["Close"], name="OHLC"), row=1, col=1)

    fig.add_trace(go.Scatter(x=candle_df["Date"], y=candle_df["EMA20"], name="EMA 20", line=dict(color="#fbbf24", width=1.8)), row=1, col=1)

    fig.add_trace(go.Scatter(x=candle_df["Date"], y=candle_df["EMA50"], name="EMA 50", line=dict(color="#60a5fa", width=2.0)), row=1, col=1)

    fig.add_trace(go.Bar(x=candle_df["Date"], y=candle_df["Volume"], name="Volume", opacity=0.6), row=2, col=1)

    fig.update_layout(height=480, xaxis_rangeslider_visible=False, template="plotly_dark" if st.session_state.theme == "dark" else "plotly_white", margin=dict(l=10, r=10, t=30, b=10))

    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)



    # Renko Chart

    base_atr = get_daily_atr(selected, 14, 7) or metrics["ltp"] * 0.005

    box_size = base_atr / 6.0 if interval == "1h" else (base_atr / 12.0 if interval == "30m" else (base_atr / 24.0 if interval == "15m" else base_atr))

    renko_df = generate_renko(candle_df, box_size)

    if not renko_df.empty:

        fig_r = go.Figure(data=[go.Candlestick(x=renko_df["Brick"], open=renko_df["Open"], high=renko_df["High"], low=renko_df["Low"], close=renko_df["Close"])])

        fig_r.update_layout(height=380, title=f"{selected} Renko ({timeframe}) • Box ₹{box_size:.2f}", xaxis_rangeslider_visible=False, template="plotly_dark" if st.session_state.theme == "dark" else "plotly_white", margin=dict(l=10, r=10, t=40, b=10))

        st.plotly_chart(fig_r, use_container_width=True, config=PLOTLY_CONFIG)



st.markdown("---")



# -------------------------------------------------

# Intraday Renko Signal Scanner

# -------------------------------------------------

st.markdown('<div class="section-header">🎯 Intraday Renko Signals</div>', unsafe_allow_html=True)

with st.spinner("Scanning Renko universe across timeframes..."):

    signal_df = scan_renko_universe(tuple(universe))



if not signal_df.empty:

    def format_signal(row):

        base = {"BUY": "🟢 BUY", "BULLISH": "🟩 BULLISH", "SELL": "🔴 SELL", "BEARISH": "🟥 BEARISH"}.get(row["Signal"], row["Signal"])

        return f"⚡{base}" if row["Just Entered"] else base



    display_df = signal_df.copy()

    display_df["Signal"] = display_df.apply(format_signal, axis=1)

    display_df["Confidence"] = display_df["Confidence"].apply(lambda x: f"{int(x)}%" if pd.notnull(x) else "—")

    cols = ["Stock", "Timeframe", "Signal", "Confidence", "Price", "EMA 20", "Entry", "Exit", "Box Size", "Last Brick Time", "Age Minutes"]

    st.dataframe(display_df[cols], use_container_width=True, hide_index=True)

else:

    st.info("No stocks currently meet two-brick signal criteria.")



st.markdown("---")



# -------------------------------------------------

# Top Gainers / Losers & Most Active

# -------------------------------------------------

st.markdown('<div class="section-header">🏆 Top Gainers & Losers</div>', unsafe_allow_html=True)

gainers, losers = get_top_movers(universe)

gcol, lcol = st.columns(2)

with gcol:

    st.markdown("##### 🟢 Top Gainers")

    if gainers is not None: st.dataframe(gainers, use_container_width=True, hide_index=True)

with lcol:

    st.markdown("##### 🔴 Top Losers")

    if losers is not None: st.dataframe(losers, use_container_width=True, hide_index=True)



st.markdown("---")



# -------------------------------------------------

# Nifty 50 Heatmap

# -------------------------------------------------

st.markdown('<div class="section-header">🗺️ Nifty 50 Heatmap</div>', unsafe_allow_html=True)

heat_df = get_nifty50_heatmap(universe)

if not heat_df.empty:

    html_cells = []

    for _, row in heat_df.sort_values("% Chg", ascending=False).iterrows():

        pct = row["% Chg"]

        bg = "#10b981" if pct >= 2 else ("#34d399" if pct >= 0.5 else ("#94a3b8" if pct > -0.5 else ("#f87171" if pct > -2 else "#ef4444")))

        html_cells.append(f'<div class="heat-cell" style="background:{bg};"><div class="hc-sym">{row["Symbol"]}</div><div class="hc-pct">{pct:+.2f}%</div><div class="hc-ltp">₹{row["LTP"]:,.1f}</div></div>')

    st.markdown('<div class="heat-grid">' + "".join(html_cells) + "</div>", unsafe_allow_html=True)



st.markdown("---")



# -------------------------------------------------

# Built-up Cycle (F&O Pack)

# -------------------------------------------------

st.markdown('<div class="section-header">🧱 Built-up Cycle · Most Active F&O Stocks</div>', unsafe_allow_html=True)

bu_df, bu_labels = get_fno_builtup(universe, top_n=30)

if not bu_df.empty:

    day_hdr = "".join(f"<th>{d}</th>" for d in bu_labels)

    rows_html = []

    for _, r in bu_df.iterrows():

        cells = f'<td><span class="bu-cell bu-{"lb" if r["Today"]=="LB" else ("sb" if r["Today"]=="SB" else "sc")}"></span></td>'

        rows_html.append(f'<tr><td style="text-align:left;font-weight:600;">{r["Symbol"]}</td>{cells}</tr>')

    st.markdown(f'<div class="builtup-wrap"><table class="builtup-table"><thead><tr><th style="text-align:left;">SYMBOL</th>{day_hdr}</tr></thead><tbody>{"".join(rows_html)}</tbody></table></div>', unsafe_allow_html=True)



st.markdown("---")



# -------------------------------------------------

# Corporate Actions & Results Calendar

# -------------------------------------------------

st.markdown('<div class="section-header">📋 Corporate Actions & Results</div>', unsafe_allow_html=True)

ca_df = get_corporate_actions(universe)

if not ca_df.empty:

    st.dataframe(ca_df, use_container_width=True, hide_index=True)



st.markdown("---")



# -------------------------------------------------

# Top 6 Business News

# -------------------------------------------------

st.markdown('<div class="section-header">📰 Top 6 Market-Moving Business News</div>', unsafe_allow_html=True)

biz_news = get_top_business_news()

if biz_news:

    news_html = '<div class="news-box">'

    for i, n in enumerate(biz_news[:6], 1):

        news_html += f'<div style="margin-bottom:8px;"><b>{i}.</b> <a href="{n["link"]}" target="_blank">{n["title"]}</a></div>'

    news_html += "</div>"

    st.markdown(news_html, unsafe_allow_html=True)



# Auto refresh

if auto_refresh:

    time.sleep(120)

    st.rerun()
