# APEX MARKET TERMINAL — UPDATED BUILD 2026-10-30 (v7.6.2b)
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

            /* === v7.4 Dashboard polish === */
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

            /* === v7.5: Instant Snapshot box — soft light green (same as index "up" cards) === */
            .snapshot-box {
                background: #eaf6ed !important;
                border: 1px solid #d3e9d8 !important;
                box-shadow: none !important;
                color: #26332b !important;
            }
            .snapshot-box .panel-title { color: #386b49 !important; }

            /* === v7.6: Heatmap — equal-size responsive grid (5 cols desktop / 4 tablet / 3 mobile) === */
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

            /* === v7.6.2: Index cards responsive grid (6 / 3 / 2) — mobile 2-per-row === */
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

            /* === v7.4 Dashboard polish (light) === */
            .dash-topbar {
                display: flex; align-items: center; justify-content: space-between;
                padding: 10px 4px 14px 4px; margin-bottom: 4px;
                border-bottom: 1px solid #c7d2fe;
            }
            .dash-brand {
                display: flex; align-items: center; gap: 10px;
            }
            .dash-brand .logo {
                width: 36px; height: 36px; border-radius: 10px;
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                display: flex; align-items: center; justify-content: center;
                font-size: 18px; font-weight: 800; color: #fff;
            }
            .dash-brand h1 {
                font-size: 22px !important; margin: 0 !important; padding: 0 !important;
                background: linear-gradient(90deg, #4f46e5, #7c3aed, #a855f7);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                font-weight: 800 !important; line-height: 1.15;
            }
            .dash-brand .tagline {
                font-size: 11px; color: #64748b; letter-spacing: 0.4px;
            }
            .dash-live {
                display: flex; align-items: center; gap: 8px;
                font-size: 12px; color: #475569;
            }
            .live-dot {
                width: 8px; height: 8px; border-radius: 50%;
                background: #059669; box-shadow: 0 0 6px #34d399;
            }
            .panel-card {
                background: #ffffff;
                border: 1px solid #c7d2fe;
                border-radius: 12px;
                padding: 14px 16px;
                margin-bottom: 12px;
                box-shadow: 0 2px 12px rgba(99,102,241,0.08);
            }
            .panel-title {
                font-size: 13px; font-weight: 700; color: #4338ca;
                letter-spacing: 0.3px; text-transform: uppercase;
                margin-bottom: 10px; display: flex; align-items: center; gap: 6px;
            }
            .section-header {
                font-size: 16px !important;
                border-bottom: 1px solid #e0e7ff;
                padding-bottom: 4px;
            }
            div[data-testid="stDataFrame"] {
                border-radius: 10px; overflow: hidden;
                border: 1px solid #e2e8f0;
            }
            .dash-divider {
                height: 1px; background: linear-gradient(90deg, transparent, #c7d2fe, transparent);
                margin: 14px 0;
            }

            /* === v7.5: Instant Snapshot box — soft light green (same as index "up" cards) === */
            .snapshot-box {
                background: #eaf6ed !important;
                border: 1px solid #d3e9d8 !important;
                box-shadow: none !important;
                color: #26332b !important;
            }
            .snapshot-box .panel-title { color: #386b49 !important; }

            /* === v7.6: Heatmap — equal-size responsive grid (5 cols desktop / 4 tablet / 3 mobile) === */
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

            /* === v7.6.2: Index cards responsive grid (6 / 3 / 2) — mobile 2-per-row === */
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

            /* Results date-strip (light) */
            .res-date-strip {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(72px, 1fr));
                gap: 6px;
                width: 100%;
            }
            .res-day {
                background: #ffffff;
                border: 1px solid #c7d2fe;
                border-radius: 8px;
                padding: 6px 4px;
                text-align: center;
                min-height: 64px;
                box-shadow: 0 1px 4px rgba(99,102,241,0.06);
            }
            .res-day .rd-date {
                font-size: 11px; font-weight: 700; color: #4338ca;
                margin-bottom: 4px; white-space: nowrap;
            }
            .res-day .rd-syms {
                font-size: 10px; font-weight: 600; color: #0f172a;
                line-height: 1.25; word-break: break-word;
            }
            .res-day.empty .rd-syms { color: #94a3b8; font-weight: 500; }
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

@st.cache_data(ttl=60)
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


@st.cache_data(ttl=60)
def fetch_index_quote(ticker: str):
    """Yahoo for Indian cash indices (Nifty, Bank Nifty, Midcaps, Sensex, VIX)."""
    return fetch_yahoo_quote(ticker)

@st.cache_data(ttl=60, show_spinner=False)
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

@st.cache_data(ttl=60, show_spinner=False)
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


@st.cache_data(ttl=60, show_spinner=False)
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



@st.cache_data(ttl=45, show_spinner=False)
def fetch_tradingeconomics_commodity(slug: str):
    """TradingEconomics commodity page — final source for Brent / WTI.
    slug examples: 'commodity/brent-crude-oil', 'commodity/crude-oil'
    Parses id=market_last and nearby daily change.
    """
    try:
        url = f"https://tradingeconomics.com/{slug}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            return None
        html = r.text

        def number(value):
            if value is None:
                return None
            cleaned = re.sub(r"[^0-9.+-]", "", str(value).replace(",", ""))
            try:
                return float(cleaned) if cleaned not in ("", "+", "-") else None
            except ValueError:
                return None

        price = None
        m = re.search(r'id=["\']market_last["\'][^>]*>([^<]+)', html, re.I)
        if m:
            price = number(m.group(1))
        if price is None:
            m = re.search(r'TEChartsMeta\s*=\s*\[\s*\{[^\]]*?"last"\s*:\s*([0-9.]+)', html, re.I)
            if m:
                price = number(m.group(1))
        if price is None:
            m = re.search(r'(?:Brent|Crude)\s+rose\s+to\s+([0-9.]+)', html, re.I)
            if m:
                price = number(m.group(1))
        if price is None or price <= 0:
            return None
        # Crude band sanity
        if not (20.0 <= price <= 250.0):
            return None

        change = pct = 0.0
        # Prefer block near market_last
        block_m = re.search(
            r'id=["\']market_last["\'][^>]*>.*?</span>(.{0,500})',
            html, re.I | re.S,
        )
        block = block_m.group(1) if block_m else html
        cm = re.search(
            r'id=["\']market_daily_chg["\'][^>]*>([^<]+)',
            block, re.I,
        )
        if not cm:
            cm = re.search(r'id=["\']market_daily_chg["\'][^>]*>([^<]+)', html, re.I)
        if cm:
            change = number(cm.group(1)) or 0.0
        pm = re.search(
            r'Daily\s*Change[^0-9+-]{0,40}([+-]?[0-9.]+)\s+([+-]?[0-9.]+)\s*%',
            re.sub(r"<[^>]+>", " ", block if block_m else html),
            re.I,
        )
        if pm:
            if change == 0.0:
                change = number(pm.group(1)) or 0.0
            pct = number(pm.group(2)) or 0.0
        elif price and change:
            # approximate pct if only absolute change found
            prev = price - change
            pct = (change / prev * 100) if prev else 0.0

        src = f"TradingEconomics ({slug})"
        ts = _ist_now_label()
        return {
            "price": round(float(price), 2),
            "change": round(float(change), 2),
            "pct": round(float(pct), 2),
            "source": src,
            "source_short": _source_short(src),
            "source_time_label": ts,
            "fetched_at": ts,
        }
    except Exception:
        return None


@st.cache_data(ttl=45, show_spinner=False)
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
    "CL=F": None,          # TE final for WTI (no Yahoo)
    "BZ=F": None,          # TE final for Brent (no Yahoo)
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

@st.cache_data(ttl=60, show_spinner=False)
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
            if key in ("BZ=F", "CL=F", "CRUDE OIL BRENT", "CRUDE OIL WTI") or (investing_key or key) in ("BZ=F", "CL=F"):
                if not (50.0 <= float(quote.get("price") or 0) <= 200.0):
                    quote = None
                # Prefer TE for oil: skip TV so TE path runs (TV often lags / wrong contract)
                quote = None
            if quote:
                return quote
    slug_key = investing_key or key
    # 2) TradingEconomics for oil (Brent + WTI) — preferred live source
    _oil_te = {
        "BZ=F": "commodity/brent-crude-oil",
        "CL=F": "commodity/crude-oil",
        "CRUDE OIL BRENT": "commodity/brent-crude-oil",
        "CRUDE OIL WTI": "commodity/crude-oil",
    }
    if key in _oil_te or slug_key in _oil_te:
        teq = fetch_tradingeconomics_commodity(_oil_te.get(key) or _oil_te.get(slug_key))
        if teq:
            return teq
    # 3) Investing.com for Brent page (secondary)
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
    # 4) TradingEconomics commodities — final for Brent & WTI (no Yahoo)
    te_commodity_map = {
        "BZ=F": "commodity/brent-crude-oil",
        "CL=F": "commodity/crude-oil",
        "CRUDE OIL BRENT": "commodity/brent-crude-oil",
        "CRUDE OIL WTI": "commodity/crude-oil",
    }
    te_c_slug = te_commodity_map.get(key) or te_commodity_map.get(slug_key)
    if te_c_slug:
        teq = fetch_tradingeconomics_commodity(te_c_slug)
        if teq:
            return teq
    # 5) Yahoo Finance — never for oil (BZ=F / CL=F)
    oil_keys = {"BZ=F", "CL=F", "CRUDE OIL BRENT", "CRUDE OIL WTI"}
    if key not in oil_keys and slug_key not in oil_keys:
        y_ticker = yahoo_ticker or YAHOO_FALLBACK.get(key) or YAHOO_FALLBACK.get(slug_key)
        if y_ticker:
            yq = fetch_yahoo_quote(y_ticker)
            if yq:
                return yq
        # Last-ditch Yahoo only for non-oil tickers
        if key and key not in ("GIFT_NIFTY", "US_TECH_FUT", "US_30_FUT", "BZ=F", "CL=F") and (
            "=" in key or key.startswith("^") or key.endswith(".SS")
        ):
            yq = fetch_yahoo_quote(key)
            if yq:
                return yq
    # 6) TradingEconomics final fallback for US indices
    te_map = {"US_TECH_FUT": "us100:ind", "US_30_FUT": "indu:ind", "^NDX": "us100:ind", "^DJI": "indu:ind"}
    te_slug = te_map.get(key)
    if te_slug:
        teq = fetch_tradingeconomics_quote(te_slug)
        if teq:
            return teq
    return None

@st.cache_data(ttl=45, show_spinner=False)
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


@st.cache_data(ttl=45, show_spinner=False)
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


@st.cache_data(ttl=60)
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

@st.cache_data(ttl=300, show_spinner=False)
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

@st.cache_data(ttl=600, show_spinner=False)
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

@st.cache_data(ttl=120)
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
    """Live Renko signal. Signal rules unchanged; only box-size ladder updated:
    Daily ATR (existing) → 1H = D/6 → 30M = D/12 → 15M = D/24.
    """
    if timeframe == "1 Hour":
        interval, period, tail_n = "1h", "1mo", 120
    elif timeframe == "15 Minutes":
        interval, period, tail_n = "15m", "5d", 180
    else:  # 30 Minutes (default)
        interval, period, tail_n = "30m", "5d", 150
    candles = get_ohlc_data(symbol, interval=interval, period=period)
    if candles is None or candles.empty or len(candles) < 22:
        return None
    candles = candles.tail(tail_n).copy().reset_index(drop=True)

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
        if interval == "1h":
            bar_length = pd.Timedelta(hours=1)
        elif interval == "15m":
            bar_length = pd.Timedelta(minutes=15)
        else:
            bar_length = pd.Timedelta(minutes=30)
        if last_time + bar_length > pd.Timestamp.now(tz="Asia/Kolkata") and len(candles) > 1:
            candles = candles.iloc[:-1].reset_index(drop=True)
    if len(candles) < 22:
        return None
    candles["EMA20"] = calculate_ema(candles["Close"], 20)
    price = float(candles["Close"].iloc[-1])
    ema20 = float(candles["EMA20"].iloc[-1])
    # ATR source unchanged (prefer last-7 avg of ATR14, fallback last-14)
    daily_atr = get_daily_atr(symbol, 14, 7) or get_daily_atr(symbol, 14, 14) or (price * 0.005)
    # Box-size ladder only change: Daily / 6 / 12 / 24
    if interval == "1h":
        box_size = daily_atr / 6.0
    elif interval == "30m":
        box_size = daily_atr / 12.0
    else:  # 15m
        box_size = daily_atr / 24.0
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
    # Confidence % (independent of signal rules): higher TF + fresh brick + clear EMA edge
    # Base by timeframe (1H more structural than 15m for positional read)
    tf_base = {"1 Hour": 72, "30 Minutes": 62, "15 Minutes": 52}.get(timeframe, 55)
    # Freshness: just-entered boost; older decays
    if age_minutes <= 10:
        age_adj = 12
    elif age_minutes <= 20:
        age_adj = 8
    elif age_minutes <= 45:
        age_adj = 3
    elif age_minutes <= 90:
        age_adj = -4
    else:
        age_adj = -10
    # EMA distance (in box units) — clearer separation = higher confidence
    ema_dist_boxes = abs(price - ema20) / max(box_size, 1e-6)
    if ema_dist_boxes >= 1.5:
        ema_adj = 10
    elif ema_dist_boxes >= 0.75:
        ema_adj = 5
    elif ema_dist_boxes >= 0.25:
        ema_adj = 0
    else:
        ema_adj = -8  # very close to EMA → weaker
    # BUY/SELL (above/below EMA) slightly preferred over plain BULLISH/BEARISH
    side_adj = 4 if action in ("BUY", "SELL") else 0
    confidence = int(max(25, min(95, tf_base + age_adj + ema_adj + side_adj)))
    return {
        "Stock": symbol, "Timeframe": timeframe, "Signal": action, "Renko": direction,
        "Price": round(price, 2), "EMA 20": round(ema20, 2),
        "Entry": round(entry, 2), "Exit": round(exit_price, 2),
        "Box Size": round(float(box_size), 2),
        "Last Brick Time": last_brick_ts.strftime("%d %b %H:%M"),
        "Last Brick TS": last_brick_ts, "Age Minutes": round(age_minutes, 1),
        "Just Entered": just_entered,
        "Confidence": confidence,
    }

@st.cache_data(ttl=120, show_spinner=False)
def scan_renko_universe(universe_tuple: tuple):
    jobs = [(symbol, timeframe) for symbol in universe_tuple
            for timeframe in ("1 Hour", "30 Minutes", "15 Minutes")]
    rows = []
    with ThreadPoolExecutor(max_workers=14) as pool:
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
    # Display order (action-first, then TF, then age):
    #   BUY/BULLISH group first:  15m (newest age) → 30m → 1H
    #   then SELL/BEARISH group:  15m (newest age) → 30m → 1H
    # Within each TF+signal: lowest Age Minutes on top
    side_order = {"BUY": 0, "BULLISH": 1, "SELL": 2, "BEARISH": 3}
    tf_order = {"15 Minutes": 0, "30 Minutes": 1, "1 Hour": 2}
    result_df["_side"] = result_df["Signal"].map(side_order).fillna(9)
    result_df["_tf"] = result_df["Timeframe"].map(tf_order).fillna(9)
    result_df = result_df.sort_values(
        by=["_side", "_tf", "Age Minutes", "Last Brick TS"],
        ascending=[True, True, True, False],
        kind="stable"
    ).drop(columns=["_side", "_tf"]).reset_index(drop=True)
    return result_df




@st.cache_data(ttl=60)
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

@st.cache_data(ttl=90)
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

@st.cache_data(ttl=90, show_spinner=False)
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

@st.cache_data(ttl=90)
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

@st.cache_data(ttl=90)
def get_stock_summary_analytics(symbol: str):
    try:
        t = yf.Ticker(f"{symbol}.NS")
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = datetime.now(ist)
        end_d = (now_ist + pd.Timedelta(days=2)).date()
        start_d = (now_ist - pd.Timedelta(days=30)).date()

        hist = None
        for kwargs in (
            dict(start=start_d.isoformat(), end=end_d.isoformat(), interval="1d", auto_adjust=True),
            dict(period="1mo", interval="1d", auto_adjust=True),
            dict(period="1mo"),
        ):
            try:
                h = t.history(**kwargs)
                if h is not None and not h.empty and len(h.dropna(subset=["Close"])) >= 5:
                    hist = h
                    break
            except Exception:
                continue
        if hist is None or hist.empty:
            return None

        hist = hist.dropna(subset=["Close"]).copy()
        try:
            hist = hist[np.isfinite(hist["Close"].astype(float))]
        except Exception:
            pass
        if hist.empty or len(hist) < 5:
            return None

        # Normalize index → naive IST calendar dates
        try:
            idx = pd.to_datetime(hist.index)
            if getattr(idx, "tz", None) is not None:
                idx = idx.tz_convert("Asia/Kolkata").tz_localize(None)
            hist = hist.copy()
            hist.index = idx
            hist = hist.groupby(hist.index.date).last()
            hist.index = pd.to_datetime(hist.index)
        except Exception:
            pass
        hist = hist.sort_index()

        # ---- Patch stale Yahoo daily history with fast_info latest close ----
        # Yahoo often lags 1 NSE session. Before open on day D, previous_close is D-1 close.
        def _last_completed_session_date(now):
            """Most recent weekday that should already have a full daily bar."""
            d = now.date()
            # Before ~18:00 IST, treat "today" as incomplete → use yesterday
            if now.hour < 18:
                d = d - pd.Timedelta(days=1)
            # Roll back weekends
            while d.weekday() >= 5:  # Sat=5 Sun=6
                d = d - pd.Timedelta(days=1)
            return d

        expected_last = _last_completed_session_date(now_ist)
        hist_last_date = hist.index[-1].date() if hasattr(hist.index[-1], "date") else pd.Timestamp(hist.index[-1]).date()

        if hist_last_date < expected_last:
            info_prev = info_last = None
            try:
                fi = t.fast_info
                info_last = getattr(fi, "last_price", None) or getattr(fi, "regular_market_price", None)
                info_prev = getattr(fi, "previous_close", None)
            except Exception:
                pass
            try:
                if info_last is None or info_prev is None:
                    info = t.info or {}
                    if info_last is None:
                        info_last = info.get("currentPrice") or info.get("regularMarketPrice")
                    if info_prev is None:
                        info_prev = info.get("previousClose") or info.get("regularMarketPreviousClose")
            except Exception:
                pass

            hist_last_close = float(hist["Close"].iloc[-1])
            patch_close = None
            # Prefer previous_close when it differs from hist (classic 1-day lag case)
            for candidate in (info_prev, info_last):
                try:
                    c = float(candidate)
                    if np.isfinite(c) and c > 0 and abs(c - hist_last_close) > 1e-6:
                        patch_close = c
                        break
                except (TypeError, ValueError):
                    continue

            if patch_close is not None:
                # Append one synthetic daily bar for the missing session
                new_idx = pd.Timestamp(expected_last)
                # Avoid duplicate index
                if new_idx.date() not in {pd.Timestamp(x).date() for x in hist.index}:
                    row = {
                        "Open": patch_close,
                        "High": patch_close,
                        "Low": patch_close,
                        "Close": patch_close,
                        "Volume": 0.0,
                    }
                    # Keep only columns that exist
                    row = {k: v for k, v in row.items() if k in hist.columns}
                    hist = pd.concat([hist, pd.DataFrame([row], index=[new_idx])])
                    hist = hist.sort_index()

        last5 = hist.tail(5).copy()
        if len(last5) < 5:
            return None

        current = float(last5["Close"].iloc[-1])
        prev_close = float(last5["Close"].iloc[-2]) if len(last5) > 1 else current
        day_high = float(last5["High"].iloc[-1]) if "High" in last5.columns else current
        day_low = float(last5["Low"].iloc[-1]) if "Low" in last5.columns else current
        avg_5d = float(last5["Close"].mean())
        high_5d = float(last5["High"].max()) if "High" in last5.columns else current
        low_5d = float(last5["Low"].min()) if "Low" in last5.columns else current
        last5["TP"] = (last5.get("High", last5["Close"]) + last5.get("Low", last5["Close"]) + last5["Close"]) / 3
        vol_sum = float(last5["Volume"].sum()) if "Volume" in last5.columns else 0.0
        vwap_5d = float((last5["TP"] * last5["Volume"]).sum() / vol_sum) if vol_sum > 0 else avg_5d
        change = current - prev_close
        pct = (change / prev_close) * 100 if prev_close else 0.0
        bias = (
            "BULLISH" if current > vwap_5d and current > avg_5d
            else "BEARISH" if current < vwap_5d and current < avg_5d
            else "NEUTRAL"
        )

        bars = []
        closes = [float(x) for x in last5["Close"].tolist()]
        dates = [pd.Timestamp(d).strftime("%d %b") for d in last5.index]
        prior_close = None
        if len(hist) >= 6:
            try:
                prior_close = float(hist["Close"].iloc[-6])
                if not np.isfinite(prior_close) or prior_close == 0:
                    prior_close = None
            except Exception:
                prior_close = None
        for i, c_f in enumerate(closes):
            if i > 0:
                prev_c = closes[i - 1]
            else:
                prev_c = prior_close if prior_close is not None else c_f
            if not np.isfinite(prev_c) or prev_c == 0:
                prev_c = c_f
            dlt = c_f - prev_c
            p = (dlt / prev_c * 100) if prev_c else 0.0
            if not np.isfinite(p):
                p = 0.0
            color = "green" if p > 0.15 else ("red" if p < -0.15 else "grey")
            bars.append({
                "date": dates[i],
                "close": round(c_f, 2),
                "pct": round(float(p), 2),
                "color": color,
            })

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
            "bias": bias,
            "last5_bars": bars,
        }
    except Exception:
        return None


# ---------- Upcoming results (next ~10 days) helper ----------
# Primary source: Moneycontrol Results Calendar (NIFTY 50 index filter id=9)
# https://www.moneycontrol.com/markets/earnings/results-calendar/?activeDate=YYYY-MM-DD&id=9&name=NIFTY+50
# Data is embedded in Next.js __NEXT_DATA__ → pageProps.resultCalendarData
@st.cache_data(ttl=600, show_spinner=False)
def get_upcoming_results(universe: list, days: int = 10):
    """Nifty-50 (or universe) earnings over the next `days` calendar days.

    Primary: Moneycontrol results-calendar with index id=9 (NIFTY 50).
    Fallback: light NSE board-meeting / corporate-action purpose filter.
    """
    from datetime import timedelta
    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).date()
    cutoff = today + timedelta(days=max(1, int(days)))
    uni_set = set(s.upper() for s in universe)

    # Moneycontrol stockName / short name → NSE symbol (Nifty-50 focused)
    NAME_TO_SYM = {
        "RELIANCE INDUSTRIES": "RELIANCE", "RELIANCE": "RELIANCE",
        "HDFC BANK": "HDFCBANK", "ICICI BANK": "ICICIBANK", "INFOSYS": "INFY",
        "TATA CONSULTANCY SERVICES": "TCS", "TCS": "TCS",
        "LARSEN & TOUBRO": "LT", "LARSEN AND TOUBRO": "LT",
        "ITC": "ITC", "BHARTI AIRTEL": "BHARTIARTL", "STATE BANK OF INDIA": "SBIN",
        "KOTAK MAHINDRA BANK": "KOTAKBANK", "AXIS BANK": "AXISBANK",
        "BAJAJ FINANCE": "BAJFINANCE", "BAJAJ FINSERV": "BAJAJFINSV",
        "HINDUSTAN UNILEVER": "HINDUNILVR", "HCL TECHNOLOGIES": "HCLTECH",
        "SUN PHARMACEUTICAL INDUSTRIES": "SUNPHARMA", "SUN PHARMA": "SUNPHARMA",
        "MARUTI SUZUKI INDIA": "MARUTI", "MARUTI SUZUKI": "MARUTI",
        "TATA MOTORS": "TATAMOTORS", "TATA MOTORS PASSENGER VEHICLES": "TATAMOTORS",
        "TATA STEEL": "TATASTEEL", "NTPC": "NTPC", "POWER GRID CORPORATION OF INDIA": "POWERGRID",
        "POWER GRID": "POWERGRID", "TITAN COMPANY": "TITAN", "TITAN": "TITAN",
        "ASIAN PAINTS": "ASIANPAINT", "ULTRATECH CEMENT": "ULTRACEMCO",
        "NESTLE INDIA": "NESTLEIND", "TATA CONSUMER PRODUCTS": "TATACONSUM",
        "TECH MAHINDRA": "TECHM", "WIPRO": "WIPRO", "JSW STEEL": "JSWSTEEL",
        "HINDALCO INDUSTRIES": "HINDALCO", "HINDALCO": "HINDALCO",
        "GRASIM INDUSTRIES": "GRASIM", "GRASIM": "GRASIM",
        "ADANI ENTERPRISES": "ADANIENT", "ADANI PORTS AND SPECIAL ECONOMIC ZONE": "ADANIPORTS",
        "ADANI PORTS": "ADANIPORTS", "ONGC": "ONGC", "OIL & NATURAL GAS CORPORATION": "ONGC",
        "COAL INDIA": "COALINDIA", "BAJAJ AUTO": "BAJAJ-AUTO",
        "HERO MOTOCORP": "HEROMOTOCO", "EICHER MOTORS": "EICHERMOT",
        "DR REDDY'S LABORATORIES": "DRREDDY", "DR REDDYS LABORATORIES": "DRREDDY",
        "CIPLA": "CIPLA", "DIVI'S LABORATORIES": "DIVISLAB", "DIVIS LABORATORIES": "DIVISLAB",
        "APOLLO HOSPITALS ENTERPRISE": "APOLLOHOSP", "APOLLO HOSPITALS": "APOLLOHOSP",
        "SBI LIFE INSURANCE COMPANY": "SBILIFE", "SBI LIFE": "SBILIFE",
        "HDFC LIFE INSURANCE COMPANY": "HDFCLIFE", "HDFC LIFE": "HDFCLIFE",
        "BRITANNIA INDUSTRIES": "BRITANNIA", "BRITANNIA": "BRITANNIA",
        "INDUSIND BANK": "INDUSINDBK", "BEL": "BEL", "BHARAT ELECTRONICS": "BEL",
        "TRENT": "TRENT", "ETERNAL": "ETERNAL", "ZOMATO": "ETERNAL",
        "MAX HEALTHCARE INSTITUTE": "MAXHEALTH", "MAX HEALTHCARE": "MAXHEALTH",
        "SHRIRAM FINANCE": "SHRIRAMFIN", "HAVELLS INDIA": "HAVELLS",
        "BPCL": "BPCL", "BHARAT PETROLEUM": "BPCL", "M&M": "M&M",
        "MAHINDRA & MAHINDRA": "M&M", "MAHINDRA AND MAHINDRA": "M&M",
    }

    def _resolve_symbol(stock_name: str, sc_id: str = "") -> str:
        raw = (stock_name or "").strip()
        if not raw:
            return ""
        key = re.sub(r"\s+", " ", raw).upper().strip()
        if key in NAME_TO_SYM:
            return NAME_TO_SYM[key]
        # strip common suffixes
        key2 = re.sub(r"\s+(LTD|LIMITED|INDIA|INDUSTRIES|COMPANY|CORPORATION)\.?$", "", key).strip()
        if key2 in NAME_TO_SYM:
            return NAME_TO_SYM[key2]
        # direct universe hit
        compact = re.sub(r"[^A-Z0-9]", "", key)
        for u in uni_set:
            if u == compact or u in compact or compact in u:
                return u
        # token overlap: prefer longest universe symbol match against name tokens
        for u in sorted(uni_set, key=len, reverse=True):
            if u.replace("-", "") in compact:
                return u
        return ""

    def _parse_mc_date(date_str: str, active_iso: str = ""):
        """Parse '7 Nov' / '07 Nov' using active_iso year, or ISO date."""
        if active_iso:
            try:
                return datetime.strptime(active_iso[:10], "%Y-%m-%d").date()
            except ValueError:
                pass
        s = (date_str or "").strip()
        if re.match(r"\d{4}-\d{2}-\d{2}", s):
            try:
                return datetime.strptime(s[:10], "%Y-%m-%d").date()
            except ValueError:
                return None
        year = today.year
        for fmt in ("%d %b", "%d %B", "%d-%b", "%d-%B"):
            try:
                d = datetime.strptime(s, fmt).date().replace(year=year)
                # if far in the past relative to today, roll year forward
                if d < today - timedelta(days=30):
                    d = d.replace(year=year + 1)
                return d
            except ValueError:
                continue
        return None

    out = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.moneycontrol.com/markets/earnings/results-calendar/",
    }

    def _fetch_mc_page(active_date: str):
        url = (
            "https://www.moneycontrol.com/markets/earnings/results-calendar/"
            f"?activeDate={active_date}&id=9&name=NIFTY+50"
        )
        try:
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code != 200 or not r.text:
                return None
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.S)
            if not m:
                return None
            payload = json.loads(m.group(1))
            return payload.get("props", {}).get("pageProps", {}).get("resultCalendarData")
        except Exception:
            return None

    # Seed page = today (Moneycontrol returns a ~9-day strip of counts)
    seed = _fetch_mc_page(today.isoformat())
    dates_to_fetch = []
    if seed:
        strip = (seed.get("dateStripData") or {}).get("list") or []
        for row in strip:
            try:
                # [displayDate, earningCount, isoDate]
                iso = str(row[2]) if len(row) > 2 else ""
                cnt = int(row[1]) if str(row[1]).isdigit() or isinstance(row[1], (int, float)) else 0
                d = _parse_mc_date("", iso) if iso else None
                if d and today <= d <= cutoff and cnt > 0:
                    dates_to_fetch.append(iso[:10])
            except Exception:
                continue
        # Always include seed active date list
        active = seed.get("activeDate") or today.isoformat()
        if active not in dates_to_fetch:
            # still parse seed table if within window
            d0 = _parse_mc_date("", active)
            if d0 and today <= d0 <= cutoff:
                dates_to_fetch.insert(0, active[:10])
    if not dates_to_fetch:
        # Brute next `days` calendar dates (weekdays only) as fallback schedule
        for i in range(0, max(1, int(days)) + 1):
            d = today + timedelta(days=i)
            if d.weekday() < 5:
                dates_to_fetch.append(d.isoformat())

    seen = set()
    pages = {}
    if seed:
        pages[str(seed.get("activeDate") or today.isoformat())[:10]] = seed
    for iso in dates_to_fetch[:14]:
        if iso in pages:
            rcd = pages[iso]
        else:
            rcd = _fetch_mc_page(iso)
            if rcd:
                pages[iso] = rcd
        if not rcd:
            continue
        active_iso = str(rcd.get("activeDate") or iso)[:10]
        for item in (rcd.get("tableData") or {}).get("list") or []:
            try:
                name = item.get("stockName") or item.get("stockShortName") or ""
                sc_id = item.get("scId") or ""
                sym = _resolve_symbol(name, sc_id)
                if not sym:
                    # keep row with cleaned name token if it looks like a Nifty name
                    sym = re.sub(r"[^A-Z0-9]", "", name.upper())[:12] or name[:12].upper()
                if uni_set and sym not in uni_set:
                    # still show if name resolved poorly but was on NIFTY 50 filtered page
                    # Prefer keeping Moneycontrol NIFTY-50 rows even if symbol map misses
                    pass
                purpose = item.get("resultType") or "Results"
                time_txt = item.get("time") or ""
                if time_txt and "not available" not in time_txt.lower():
                    purpose = f"{purpose} · {time_txt}"
                d = _parse_mc_date(item.get("date") or "", active_iso)
                if d is not None and not (today <= d <= cutoff):
                    continue
                key = (sym, active_iso, purpose)
                if key in seen:
                    continue
                seen.add(key)
                out.append({
                    "Symbol": sym if sym else name,
                    "Purpose": str(purpose)[:100],
                    "Date": d.strftime("%d %b %Y") if d else active_iso,
                    "SortDate": d or (today + timedelta(days=365)),
                    "Source": "Moneycontrol",
                    "Type": "Result",
                    "Company": name,
                })
            except Exception:
                continue

    # ---- Light NSE fallback if MC empty ----
    if not out:
        headers_nse = nse_session_headers()
        session = requests.Session()
        try:
            session.get("https://www.nseindia.com", headers=headers_nse, timeout=6)
            for url in (
                "https://www.nseindia.com/api/corporates-corporateActions?index=equities",
                "https://www.nseindia.com/api/corporates-financial-results?index=equities",
            ):
                try:
                    r = session.get(url, headers=headers_nse, timeout=10)
                    if r.status_code != 200:
                        continue
                    data = r.json()
                    rows = data if isinstance(data, list) else (
                        data.get("data") or data.get("corporateActions") or data.get("results") or []
                    )
                    for item in rows:
                        if not isinstance(item, dict):
                            continue
                        sym = (item.get("symbol") or item.get("Symbol") or "").strip().upper()
                        if not sym or (uni_set and sym not in uni_set):
                            continue
                        purpose = (item.get("purpose") or item.get("subject") or item.get("period") or "Results")
                        low = purpose.lower()
                        if not any(k in low for k in ("result", "financial", "earnings", "quarter", "board")):
                            continue
                        date_raw = (item.get("exDate") or item.get("boardMeetingDate")
                                    or item.get("date") or item.get("fromDate") or "")
                        out.append({
                            "Symbol": sym,
                            "Purpose": str(purpose)[:100],
                            "Date": str(date_raw)[:16] or "—",
                            "SortDate": today + timedelta(days=365),
                            "Source": "NSE",
                            "Type": "Result",
                            "Company": sym,
                        })
                except Exception:
                    continue
        except Exception:
            pass
        finally:
            try:
                session.close()
            except Exception:
                pass

    if not out:
        return pd.DataFrame()
    df = pd.DataFrame(out)
    df = df.drop_duplicates(subset=["Symbol", "Purpose", "Date"])
    df = df.sort_values(["SortDate", "Symbol"]).reset_index(drop=True)
    if "SortDate" in df.columns:
        df = df.drop(columns=["SortDate"])
    return df.head(40)


# ---------- Aaj Ki Taaza Khabar — pictorial digest (PNG) ----------
def build_taaza_khabar_image(
    biz_news,
    nifty_an=None,
    bank_an=None,
    sensex_q=None,
    gold_q=None,
    fii_txt="—",
    dii_txt="—",
):
    """
    Build a single downloadable/display PNG in the style of a daily market digest:
    title strip + market snapshot (Nifty / BNF / Sensex / Gold / FII / DII) + top 10 headlines.
    Returns (png_bytes, error_message).
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
    except Exception as e:
        return None, f"Pillow not available: {e}"

    W, H = 900, 1280
    img = Image.new("RGB", (W, H), "#0f172a")
    draw = ImageDraw.Draw(img)

    def font(size, bold=False):
        # DejaVu is commonly present on Linux; fall back to default
        for name in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ):
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue
        return ImageFont.load_default()

    f_title = font(36, True)
    f_sub = font(14, False)
    f_h = font(13, True)
    f_body = font(12, False)
    f_small = font(11, False)
    f_num = font(14, True)

    # Header band
    draw.rectangle([0, 0, W, 110], fill="#1e1b4b")
    draw.text((28, 22), "AAJ KI TAAZA KHABAR", fill="#c4b5fd", font=f_title)
    from datetime import datetime as _dt
    import pytz as _pz
    ist = _pz.timezone("Asia/Kolkata")
    now_s = _dt.now(ist).strftime("%A, %d %b %Y  ·  %H:%M IST")
    draw.text((28, 70), f"Stock Market  |  Economy  |  Business   ·   {now_s}", fill="#94a3b8", font=f_sub)

    # Snapshot strip
    y0 = 125
    draw.rounded_rectangle([16, y0, W - 16, y0 + 100], radius=12, fill="#1e293b", outline="#334155")

    def _snap(label, val, chg, x):
        draw.text((x, y0 + 12), label, fill="#94a3b8", font=f_small)
        draw.text((x, y0 + 34), val, fill="#f8fafc", font=f_h)
        col = "#34d399" if (chg or "").startswith("+") or (chg or "").startswith("▲") else (
            "#f87171" if (chg or "").startswith("-") or (chg or "").startswith("▼") else "#cbd5e1"
        )
        draw.text((x, y0 + 58), chg or "", fill=col, font=f_small)

    def _fmt_idx(an, prefix="₹"):
        if not an:
            return "—", ""
        p = an.get("current") or an.get("price")
        pct = an.get("pct")
        ch = an.get("change")
        if p is None:
            return "—", ""
        val = f"{prefix}{p:,.0f}" if prefix == "₹" else f"{p:,.2f}"
        c = f"{ch:+.0f} ({pct:+.2f}%)" if ch is not None and pct is not None else (f"{pct:+.2f}%" if pct is not None else "")
        return val, c

    n_val, n_chg = _fmt_idx(nifty_an)
    b_val, b_chg = _fmt_idx(bank_an)
    s_val, s_chg = _fmt_idx(sensex_q) if isinstance(sensex_q, dict) else ("—", "")
    if isinstance(sensex_q, dict) and "price" in sensex_q:
        s_val = f"₹{sensex_q['price']:,.0f}"
        s_chg = f"{sensex_q.get('change', 0):+.0f} ({sensex_q.get('pct', 0):+.2f}%)"
    g_val, g_chg = "—", ""
    if isinstance(gold_q, dict) and gold_q.get("price"):
        g_val = f"{gold_q['price']:,.0f}"
        g_chg = f"{gold_q.get('change', 0):+.0f} ({gold_q.get('pct', 0):+.2f}%)"

    xs = [28, 170, 320, 480, 620, 760]
    _snap("NIFTY 50", n_val, n_chg, xs[0])
    _snap("BANK NIFTY", b_val, b_chg, xs[1])
    _snap("SENSEX", s_val, s_chg, xs[2])
    _snap("GOLD", g_val, g_chg, xs[3])
    _snap("FII", str(fii_txt)[:14], "", xs[4])
    _snap("DII", str(dii_txt)[:14], "", xs[5])

    # News block
    y = y0 + 120
    draw.text((28, y), "TOP MARKET-MOVING HEADLINES", fill="#a5b4fc", font=f_h)
    y += 28
    items = list(biz_news or [])[:10]
    if not items:
        items = [{"title": "Headlines temporarily unavailable — refresh during market hours."}]

    for i, n in enumerate(items, 1):
        title = (n.get("title") or "").strip()
        # wrap title
        max_chars = 95
        if len(title) > max_chars:
            title = title[: max_chars - 1] + "…"
        # card background
        card_h = 78
        draw.rounded_rectangle([16, y, W - 16, y + card_h], radius=10, fill="#1e293b", outline="#334155")
        # number badge
        draw.ellipse([28, y + 24, 54, y + 50], fill="#6366f1")
        draw.text((34, y + 28), f"{i}", fill="#ffffff", font=f_num)
        # title text (simple two-line wrap)
        words = title.split()
        line1, line2 = "", ""
        for w in words:
            trial = (line1 + " " + w).strip()
            if len(trial) <= 78:
                line1 = trial
            else:
                line2 = (line2 + " " + w).strip()
        draw.text((66, y + 18), line1, fill="#f1f5f9", font=f_body)
        if line2:
            if len(line2) > 78:
                line2 = line2[:77] + "…"
            draw.text((66, y + 40), line2, fill="#cbd5e1", font=f_body)
        y += card_h + 8
        if y > H - 60:
            break

    # Footer
    draw.text((28, H - 36), "Apex Market Terminal  ·  Not financial advice  ·  Confirm with your broker", fill="#64748b", font=f_small)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), None


# ---------- Most Active (Value / Volume) from NSE + fallbacks ----------
@st.cache_data(ttl=90, show_spinner=False)
def get_most_active(by: str = "value"):
    """Top most-active equities by value or volume.
    Primary: NSE live-analysis API. Fallback: Yahoo ranking of Nifty-50 by volume/value
    (NSE often returns 403 from cloud/datacenter IPs — fallback keeps the panel alive).
    """
    headers = nse_session_headers()
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
                    # NSE totalTradedValue is typically in ₹; convert to Lakh when looks like full rupees
                    try:
                        val_f = float(val) if val else 0.0
                    except Exception:
                        val_f = 0.0
                    if val_f > 1e6:  # likely full ₹ → show in Lakh
                        val_f = val_f / 1e5
                    out.append({
                        "Symbol": str(sym).strip(),
                        "LTP": round(float(ltp), 2) if ltp else 0,
                        "% Chg": round(float(chg), 2) if chg else 0,
                        "Volume": int(float(vol)) if vol else 0,
                        "Value (₹ Lakh)": round(val_f, 2),
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

    # ---- Fallback: rank Nifty-50 universe via Yahoo (volume / approx value) ----
    try:
        uni = list(get_stock_universe()) if "get_stock_universe" in globals() else []
        if not uni:
            uni = ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN", "BHARTIARTL",
                   "ITC", "LT", "AXISBANK", "KOTAKBANK", "HINDUNILVR", "BAJFINANCE", "ASIANPAINT"]
        tickers = [f"{s}.NS" for s in uni]
        data = yf.download(tickers, period="5d", group_by="ticker", progress=False, threads=True)
        rows = []
        for sym in uni:
            try:
                tk = f"{sym}.NS"
                hist = None
                if hasattr(data, "columns") and getattr(data.columns, "nlevels", 1) > 1:
                    if tk in data.columns.get_level_values(0):
                        hist = data[tk]
                elif hasattr(data, "columns") and "Close" in data.columns:
                    hist = data
                if hist is None or hist.empty:
                    continue
                hist = hist.dropna(subset=["Close"])
                if hist.empty:
                    continue
                last = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else last
                ltp = float(last["Close"])
                prevc = float(prev["Close"]) if prev is not None else ltp
                vol = float(last["Volume"]) if "Volume" in last.index and pd.notnull(last["Volume"]) else 0.0
                pct = ((ltp - prevc) / prevc * 100) if prevc else 0.0
                val_lakh = (ltp * vol) / 1e5 if vol else 0.0
                rows.append({
                    "Symbol": sym,
                    "LTP": round(ltp, 2),
                    "% Chg": round(pct, 2),
                    "Volume": int(vol),
                    "Value (₹ Lakh)": round(val_lakh, 2),
                })
            except Exception:
                continue
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        if by == "volume":
            df = df.sort_values("Volume", ascending=False)
        else:
            df = df.sort_values("Value (₹ Lakh)", ascending=False)
        return df.head(10).reset_index(drop=True)
    except Exception:
        return pd.DataFrame()

# ---------- Nifty 50 Heatmap ----------
@st.cache_data(ttl=120, show_spinner=False)
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
                # Intraday move vs open of last bar when available (refresh-to-refresh uses session)
                day_open = float(hist["Open"].iloc[-1]) if "Open" in hist.columns else prev
                intraday_pct = (last - day_open) / day_open * 100 if day_open else 0
                rows.append({
                    "Symbol": sym,
                    "LTP": round(last, 2),
                    "% Chg": round(pct, 2),
                    "Intraday %": round(intraday_pct, 2),
                })
            except Exception:
                continue
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()

# ---------- Corporate Actions (Nifty 50) ----------
@st.cache_data(ttl=300, show_spinner=False)
def get_corporate_actions(universe: list):
    """Forthcoming corporate actions for Nifty-50 names.
    Primary: NSE corporates-corporateActions API.
    Fallback: Moneycontrol corporate-action calendar (HTML parse) when NSE returns 403.
    """
    headers = nse_session_headers()
    session = requests.Session()
    uni_set = set(s.upper() for s in universe)
    out = []
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=6)
        session.get("https://www.nseindia.com/companies-listing/corporate-filings-actions", headers=headers, timeout=6)
        for url in (
            "https://www.nseindia.com/api/corporates-corporateActions?index=equities",
            "https://www.nseindia.com/api/corporates-corporateActions",
        ):
            try:
                r = session.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    continue
                data = r.json()
                rows = data if isinstance(data, list) else (data.get("data") or data.get("corporateActions") or [])
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
                        "Purpose": (purpose[:80] if purpose else "—"),
                        "Ex-Date": str(ex_date)[:16],
                        "Record Date": str(rec_date)[:16],
                        "Face Value": face,
                    })
                if out:
                    break
            except Exception:
                continue
    except Exception:
        pass
    finally:
        try:
            session.close()
        except Exception:
            pass

    # ---- Fallback: Moneycontrol equity corporate actions page (best-effort scrape) ----
    if not out:
        try:
            mc_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            }
            # Recent corporate actions list
            mc_url = "https://www.moneycontrol.com/stocks/marketstats/nse_ca_latest.php"
            r = requests.get(mc_url, headers=mc_headers, timeout=10)
            if r.status_code == 200 and r.text:
                html = r.text
                # Simple row scrape: look for symbol-like tokens + purpose keywords
                # Tables vary; parse <tr> blocks with multiple <td>
                rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, flags=re.I | re.S)
                for row in rows[:80]:
                    cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, flags=re.I | re.S)
                    cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
                    if len(cells) < 3:
                        continue
                    # Heuristic: first cell often company/symbol
                    raw0 = cells[0]
                    sym = re.sub(r"[^A-Z0-9]", "", raw0.upper())[:12]
                    if not sym or (uni_set and sym not in uni_set and not any(sym.startswith(u[:4]) for u in uni_set)):
                        # try to match any universe name inside
                        matched = None
                        up = " ".join(cells).upper()
                        for u in uni_set:
                            if u in up or u[:5] in up:
                                matched = u
                                break
                        if not matched:
                            continue
                        sym = matched
                    purpose = cells[1] if len(cells) > 1 else "—"
                    ex_date = cells[2] if len(cells) > 2 else ""
                    rec_date = cells[3] if len(cells) > 3 else ""
                    out.append({
                        "Symbol": sym,
                        "Purpose": (purpose[:80] if purpose else "—"),
                        "Ex-Date": str(ex_date)[:16],
                        "Record Date": str(rec_date)[:16],
                        "Face Value": "",
                    })
        except Exception:
            pass

    if not out:
        return pd.DataFrame()
    df = pd.DataFrame(out).drop_duplicates(subset=["Symbol", "Purpose", "Ex-Date"])
    return df.head(25)

# ---------- Top 5 market-moving business news (30-min cache) ----------
@st.cache_data(ttl=1800, show_spinner=False)
def get_top_business_news():
    """Top India + global market-moving headlines. Prefers ET / Moneycontrol / FT / Bloomberg / TE context via Google News RSS."""
    items = []
    queries = [
        "(India+OR+Nifty+OR+Sensex+OR+RBI+OR+FII+OR+Budget+OR+GST)+when:1d",
        "(Federal+Reserve+OR+US+inflation+OR+Treasury+OR+crude+oil+OR+geopolitics)+when:1d",
        "(site:economictimes.indiatimes.com+OR+site:moneycontrol.com)+(market+OR+nifty+OR+stocks)+when:1d",
        "(China+OR+Japan+OR+Hong+Kong+OR+Asia+markets+OR+trade+deal)+when:1d",
        "(Bloomberg+OR+Financial+Times+OR+Trading+Economics)+(India+OR+Asia+OR+Fed+OR+oil)+when:1d",
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
                low = title.lower()
                score = 0
                for kw in ["fed", "rate", "oil", "crude", "treasury", "china", "india", "nifty",
                           "sensex", "trade", "war", "sanction", "inflation", "gdp", "stimulus",
                           "yen", "dollar", "bitcoin", "gold", "geopolit", "deal", "rbi", "fii",
                           "budget", "gst", "sebi", "ipo", "earnings", "rupee", "bond"]:
                    if kw in low:
                        score += 1
                # Boost known India-relevant outlets in title suffix
                for src in ["economic times", "moneycontrol", "bloomberg", "financial times",
                            "reuters", "trading economics", "mint", "business standard"]:
                    if src in low:
                        score += 2
                if score >= 1:
                    seen.add(title)
                    items.append({"title": title, "link": link, "score": score})
        except Exception:
            continue
    items.sort(key=lambda x: -x["score"])
    return items[:6]

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
@st.cache_data(ttl=150, show_spinner=False)
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



def assess_builtup_deep(bu_df: pd.DataFrame):
    """
    Independent assessment of Built-up cycle table.
    Combines today code + recent day streak + price%/OI% proxy — not only colour cells.
    Returns list of recommendation strings + short bias summary.
    """
    if bu_df is None or bu_df.empty:
        return [], "No built-up data to assess."
    long_candidates = []
    short_candidates = []
    cover_candidates = []
    unwind_caution = []
    for _, r in bu_df.iterrows():
        sym = r.get("Symbol", "")
        today = r.get("Today", "NA")
        days = list(r.get("Days") or [])
        pct = float(r.get("Price%") or 0)
        oi = float(r.get("OI%") or 0)
        # Streak counts in recent days (newest first in Days)
        recent = ([today] + days)[:5]
        lb_n = sum(1 for c in recent if c == "LB")
        sb_n = sum(1 for c in recent if c == "SB")
        sc_n = sum(1 for c in recent if c == "SC")
        lu_n = sum(1 for c in recent if c == "LU")
        # Score-style heuristics
        if today == "LB" and lb_n >= 2 and pct > 0.3 and oi > 0:
            long_candidates.append((sym, pct, oi, lb_n, "Sustained long build-up (multi-day LB + price↑ + vol↑)"))
        elif today == "LB" and pct > 0.5:
            long_candidates.append((sym, pct, oi, lb_n, "Fresh long build-up today with positive price"))
        if today == "SB" and sb_n >= 2 and pct < -0.3 and oi > 0:
            short_candidates.append((sym, pct, oi, sb_n, "Sustained short build-up (multi-day SB + price↓ + vol↑)"))
        elif today == "SB" and pct < -0.5:
            short_candidates.append((sym, pct, oi, sb_n, "Fresh short build-up today with negative price"))
        if today == "SC" and (sc_n >= 2 or pct > 0.4):
            cover_candidates.append((sym, pct, oi, sc_n, "Short covering bias — bounce risk / squeeze watch"))
        if today == "LU" and lu_n >= 2:
            unwind_caution.append((sym, pct, oi, lu_n, "Long unwinding streak — avoid fresh longs until stabilises"))
    # Rank
    long_candidates.sort(key=lambda x: (-x[3], -x[1]))
    short_candidates.sort(key=lambda x: (-x[3], x[1]))
    cover_candidates.sort(key=lambda x: (-x[1], -x[3]))
    # HTML colour tags so the assessment box is easy to scan
    lines = []
    if long_candidates:
        top = long_candidates[:5]
        body = ", ".join(f"{s} ({note}; {p:+.1f}% / OI {o:+.0f}%)" for s, p, o, n, note in top)
        lines.append(
            f'<span style="color:#059669;font-weight:700;">🟢 LONG bias:</span> '
            f'<span style="color:#34d399;">{body}</span>'
        )
    if short_candidates:
        top = short_candidates[:5]
        body = ", ".join(f"{s} ({note}; {p:+.1f}% / OI {o:+.0f}%)" for s, p, o, n, note in top)
        lines.append(
            f'<span style="color:#dc2626;font-weight:700;">🔴 SHORT bias:</span> '
            f'<span style="color:#f87171;">{body}</span>'
        )
    if cover_candidates:
        top = cover_candidates[:4]
        body = ", ".join(f"{s} ({note})" for s, p, o, n, note in top)
        lines.append(
            f'<span style="color:#2563eb;font-weight:700;">🔵 Short covering:</span> '
            f'<span style="color:#60a5fa;">{body}</span>'
        )
    if unwind_caution:
        top = unwind_caution[:4]
        body = ", ".join(f"{s} ({note})" for s, p, o, n, note in top)
        lines.append(
            f'<span style="color:#a3a30a;font-weight:700;">🟡 Long unwinding:</span> '
            f'<span style="color:#fbbf24;">{body}</span>'
        )
    if not lines:
        lines.append(
            '<span style="color:#94a3b8;">Mixed / transitional built-up — no dominant multi-day LB or SB cluster.</span>'
        )
    # Overall tone
    n_lb = sum(1 for _, r in bu_df.iterrows() if r.get("Today") == "LB")
    n_sb = sum(1 for _, r in bu_df.iterrows() if r.get("Today") == "SB")
    n_sc = sum(1 for _, r in bu_df.iterrows() if r.get("Today") == "SC")
    n_lu = sum(1 for _, r in bu_df.iterrows() if r.get("Today") == "LU")
    tone = (
        f"Today’s active set mix: LB {n_lb} · SB {n_sb} · SC {n_sc} · LU {n_lu}. "
    )
    if n_lb + n_sc > n_sb + n_lu + 3:
        tone += "Skew leans constructive (long build-up / short covering dominant)."
    elif n_sb + n_lu > n_lb + n_sc + 3:
        tone += "Skew leans defensive (short build-up / long unwinding dominant)."
    else:
        tone += "No clear one-way skew — stock-pick on multi-day streaks rather than broad beta."
    return lines, tone


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
    st.caption("Data: TV → Investing → TE (oil) → Yahoo • NSE  |  ⚡ Fast Refresh = soft quote clear (Renko stays warm)\nUI v7.6.2b — results date-strip · index grid 2-col mobile · download-btn fix")

# -------------------------------------------------
# Header + Time (dashboard top bar)
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
dropdown_universe = sorted(universe, key=lambda sym: (-NIFTY50_WEIGHT.get(sym, 0.0), sym))
col1, col2, col3 = st.columns([2.2, 1.2, 1])
with col1:
    selected = st.selectbox("🔍 Select Stock (NSE)", options=dropdown_universe, index=0, key="selected")
with col2:
    auto_refresh = st.checkbox("🔄 Auto-refresh every 2 min", value=False)
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ Fast Refresh", use_container_width=True):
        # Soft clear ONLY live quotes + selected stock snapshot (keeps universe / news /
        # Renko scan / corporate warm → much faster than full reload)
        for _fn in (
            fetch_yahoo_quote, fetch_index_quote, fetch_tradingview_quote,
            fetch_investing_quote, fetch_live_instrument, fetch_gift_nifty_50,
            fetch_midcap_select, fetch_investing_brent, fetch_tradingeconomics_quote,
            fetch_tradingeconomics_commodity, fetch_stock_data, get_option_sentiment,
            get_options_chain, get_stock_summary_analytics, get_index_analytics,
            get_nifty50_heatmap, get_most_active, get_market_breadth, get_top_movers,
            get_fno_builtup,
        ):
            try:
                _fn.clear()
            except Exception:
                pass
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
    # v7.5: light-green snapshot box → dark, high-contrast text colours
    bias_color = "#1f8a4c" if summary["bias"] == "BULLISH" else "#c0392b" if summary["bias"] == "BEARISH" else "#b7791f"
    chg_color = "#1f8a4c" if summary['change'] >= 0 else "#c0392b"
    pcr_html = f"<div><b>PCR (OI):</b> {stock_pcr:.3f}" + (f" <span style='font-size:11px;color:#52615a;'>({stock_pcr_src})</span>" if stock_pcr_src else "") + "</div>" if stock_pcr is not None else "<div><b>PCR (OI):</b> —</div>"
    mp_html = f"<div><b>Max Pain:</b> ₹{stock_mp:,.0f}</div>" if stock_mp is not None else "<div><b>Max Pain:</b> —</div>"
    # Compact vertical last-5 bars — left cluster, small footprint
    bars = summary.get("last5_bars") or []
    bar_html = ""
    if bars:
        # Scale bar height by relative close range within the 5 days.
        # Guard against NaN / Inf / zero-span (yfinance missing bars → ValueError on int(nan)).
        closes = []
        for b in bars:
            try:
                c = float(b.get("close"))
                if np.isfinite(c):
                    closes.append(c)
            except (TypeError, ValueError):
                continue
        if closes:
            lo, hi = min(closes), max(closes)
            span = hi - lo
            if not np.isfinite(span) or span <= 0:
                span = 1.0
        else:
            lo, span = 0.0, 1.0
        cells = []
        for b in bars:
            bg = "#059669" if b.get("color") == "green" else ("#dc2626" if b.get("color") == "red" else "#64748b")
            try:
                c = float(b.get("close", 0))
                if not np.isfinite(c):
                    h = 16
                else:
                    h = 10 + int(22 * max(0.0, min(1.0, (c - lo) / span)))
            except (TypeError, ValueError, OverflowError):
                h = 16
            # Readable price under bar (slightly larger for eyes)
            try:
                close_val = float(b.get("close", 0))
                price_txt = f'{close_val:,.0f}' if close_val >= 100 else f'{close_val:.1f}'
            except (TypeError, ValueError):
                price_txt = "—"
            try:
                pct_val = float(b.get("pct", 0))
                pct_txt = f"{pct_val:+.1f}%"
            except (TypeError, ValueError):
                pct_txt = "—"
            cells.append(
                f'<div style="display:inline-block;width:48px;margin-right:4px;text-align:center;vertical-align:bottom;">'
                f'<div style="height:36px;display:flex;align-items:flex-end;justify-content:center;">'
                f'<div style="width:14px;height:{h}px;background:{bg};border-radius:2px;"></div></div>'
                f'<div style="font-size:10px;color:#52615a;line-height:1.15;margin-top:3px;">{b.get("date", "")}</div>'
                f'<div style="font-size:10px;font-weight:700;color:#26332b;line-height:1.15;">{price_txt}</div>'
                f'<div style="font-size:10px;font-weight:600;color:#3b4a42;line-height:1.15;">{pct_txt}</div></div>'
            )
        bar_html = (
            '<div style="margin-top:8px;display:flex;align-items:flex-end;gap:2px;">'
            '<div style="font-size:11px;font-weight:600;color:#52615a;writing-mode:horizontal-tb;margin-right:6px;align-self:center;">5D</div>'
            f'{"".join(cells)}</div>'
        )
    st.markdown(f"""
    <div class="analysis-box panel-card snapshot-box" style="margin-top:4px;">
        <div class="panel-title">📌 {selected} • Instant Snapshot</div>
        <div style="display:flex; flex-wrap:wrap; gap:14px 18px; font-size:13px; align-items:flex-start;">
            <div style="flex:1 1 auto; min-width:220px;">
                <div style="display:flex; flex-wrap:wrap; gap:14px 18px;">
                    <div><b>LTP:</b> ₹{summary['current']:,.2f} <span style="color:{chg_color}">({summary['change']:+.2f} | {summary['pct']:+.2f}%)</span></div>
                    <div><b>Day H/L:</b> ₹{summary['day_high']:,.2f} / ₹{summary['day_low']:,.2f}</div>
                    <div><b>5D Avg:</b> ₹{summary['avg_5d']:,.2f}</div>
                    <div><b>5D High/Low:</b> ₹{summary['high_5d']:,.2f} / ₹{summary['low_5d']:,.2f}</div>
                    <div><b>5D VWAP:</b> ₹{summary['vwap_5d']:,.2f} {'✅ Above' if summary['above_vwap'] else '❌ Below'}</div>
                    <div><b>Bias:</b> <span style="color:{bias_color}; font-weight:700;">{summary['bias']}</span></div>
                    {pcr_html}
                    {mp_html}
                </div>
            </div>
            <div style="flex:0 0 auto;">{bar_html}</div>
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

# Parallel fetch all index cards (major speed win vs sequential HTTP)
def _fetch_instrument_card(name_meta):
    name, meta = name_meta
    mode, key, tv_symbols, inv_key, yahoo_tk = meta
    try:
        if mode == "gift":
            data = fetch_gift_nifty_50()
        elif mode == "midselect":
            data = fetch_midcap_select()
        elif mode == "cash":
            data = fetch_index_quote(key)
        else:
            data = fetch_live_instrument(key, tv_symbols, inv_key, yahoo_tk)
    except Exception:
        data = None
    return name, data

_instrument_data = {}
with ThreadPoolExecutor(max_workers=12) as _pool:
    for _name, _data in _pool.map(_fetch_instrument_card, items):
        _instrument_data[_name] = _data

# v7.6.2: single responsive CSS grid (6 desktop / 3 tablet / 2 mobile) instead of st.columns(6)
_cards_html = ['<div class="index-grid">']
for name, meta in items:
    mode, key, tv_symbols, inv_key, yahoo_tk = meta
    data = _instrument_data.get(name)
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
        short = data.get("source_short") or _source_short(data.get("source", ""))
        existing = (data.get("source_time_label") or "").strip()
        if existing and short and existing.upper().startswith(short.upper() + " "):
            time_label = existing
        else:
            ts = existing or data.get("fetched_at") or _ist_now_label()
            time_label = f"{short} {ts}" if short else ts
        time_html = (
            f'<div style="font-size:7px;color:#8a8a8a;text-align:center;'
            f'margin-top:2px;line-height:1.1;">{time_label}</div>'
        )
        # Truncate very long display names for mobile ellipsis safety
        display_name = name if len(name) <= 18 else (name[:16] + "…")
        _cards_html.append(
            f'<div class="{card_cls}">'
            f'<div class="index-title" title="{name}">{display_name}</div>'
            f'<div class="index-price">{price_str}</div>'
            f'<div class="index-change {color}">{change_str} ({sign}{float(data.get("pct", 0)):.2f}%)</div>'
            f'{time_html}'
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
def _fetch_macro(spec):
    label, key, tv_symbols, inv_key, yahoo_tk = spec
    try:
        return label, fetch_live_instrument(key, tv_symbols, inv_key, yahoo_tk)
    except Exception:
        return label, None

macro_quotes = {}
with ThreadPoolExecutor(max_workers=8) as _mpool:
    for _label, _q in _mpool.map(_fetch_macro, macro_specs):
        macro_quotes[_label] = _q

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
    timeframe = st.radio("Timeframe", ["Daily", "1 Hour", "30 Minutes", "15 Minutes"], index=0, horizontal=True)
with tf_col2:
    if timeframe == "Daily":
        period = st.select_slider("Chart Period", ["1mo", "3mo", "6mo", "1y"], value="3mo")
    elif timeframe == "1 Hour":
        period = "1mo"
        st.caption(f"Period: **{period}**")
    else:
        period = "5d"
        st.caption(f"Period: **{period}**")

interval = {"Daily": "1d", "1 Hour": "1h", "30 Minutes": "30m", "15 Minutes": "15m"}[timeframe]
candle_df = get_ohlc_data(selected, interval=interval, period=period)

if candle_df is None or candle_df.empty:
    st.info("Chart data temporarily unavailable")
else:
    if timeframe == "1 Hour":
        candle_df = candle_df.tail(80).reset_index(drop=True)
    elif timeframe == "30 Minutes":
        candle_df = candle_df.tail(100).reset_index(drop=True)
    elif timeframe == "15 Minutes":
        candle_df = candle_df.tail(120).reset_index(drop=True)
    candle_df["EMA20"] = calculate_ema(candle_df["Close"], 20)
    candle_df["EMA50"] = calculate_ema(candle_df["Close"], 50)
    use_sequential = timeframe in ["1 Hour", "30 Minutes", "15 Minutes"]
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
    base = daily_atr_7 if daily_atr_7 and daily_atr_7 > 0 else (daily_atr_14 or metrics["ltp"] * 0.005)
    if timeframe == "Daily":
        box_size = daily_atr_14 if daily_atr_14 and daily_atr_14 > 0 else metrics["ltp"] * 0.005
        box_label = f"ATR(14) ≈ ₹{box_size:.2f}"
    elif timeframe == "1 Hour":
        box_size = base / 6.0
        box_label = f"Daily ATR / 6 ≈ ₹{box_size:.2f}"
    elif timeframe == "30 Minutes":
        box_size = base / 12.0
        box_label = f"Daily ATR / 12 ≈ ₹{box_size:.2f}"
    else:  # 15 Minutes
        box_size = base / 24.0
        box_label = f"Daily ATR / 24 ≈ ₹{box_size:.2f}"
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
st.markdown('<div class="section-header">🎯 Intraday Renko Signals • BUY/Bullish (15m→30m→1H) then SELL/Bearish (15m→30m→1H)</div>', unsafe_allow_html=True)
st.caption("Only stocks with the latest two Renko bricks in the same direction are listed. BUY/SELL requires close above/below 20 EMA. ⚡ = Just entered (≤ 20 min). Order: all BUY then BULLISH by TF 15m→30m→1H (newest age on top), then all SELL then BEARISH same. Box size: Daily ATR ÷ 6 (1H) ÷ 2 (30M) ÷ 2 (15M).")

scan_col1, scan_col2 = st.columns([1, 4])
with scan_col1:
    if st.button("🔄 Scan All Stocks", use_container_width=True):
        # Keep OHLC/ATR warm — only invalidate scan result for a fast re-run
        scan_renko_universe.clear()
        st.rerun()
with scan_col2:
    st.caption(f"Scanning {len(universe)} Nifty 50 stocks across 15-minute, 30-minute and 1-hour timeframes.")

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

    cols_to_show = ["Stock", "Timeframe", "Signal", "Confidence", "Price", "EMA 20", "Entry", "Exit", "Box Size", "Last Brick Time", "Age Minutes"]
    for col in ["Price", "EMA 20", "Entry", "Exit", "Box Size"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: round(float(x), 2) if pd.notnull(x) else x)

    if "Confidence" in display_df.columns:
        display_df["Confidence"] = display_df["Confidence"].apply(lambda x: f"{int(x)}%" if pd.notnull(x) else "—")
    styled = display_df[cols_to_show].style.apply(highlight_just_entered, axis=1).format({
        "Price": "{:.2f}", "EMA 20": "{:.2f}", "Entry": "{:.2f}", "Exit": "{:.2f}", "Box Size": "{:.2f}", "Age Minutes": "{:.1f}"
    })
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption("⚡ = Just entered (≤20 min) • Yellow = fresh • Confidence % = live (TF + age + EMA edge)")
    # Pre-build CSV bytes + stable key — avoids Streamlit Cloud "not connected to a server" on DownloadButton
    _csv_df = signal_df.drop(columns=["Last Brick TS", "Just Entered"], errors="ignore").copy()
    for _c in list(_csv_df.columns):
        if str(_csv_df[_c].dtype).startswith("datetime"):
            _csv_df[_c] = _csv_df[_c].astype(str)
    _csv_bytes = _csv_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download signal list (CSV)",
        data=_csv_bytes,
        file_name="intraday_renko_signals.csv",
        mime="text/csv",
        key="dl_renko_signals_csv",
    )


st.markdown("---")

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

# Options chain uses cache TTL — no forced 30s full-page rerun (speed pack)


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
st.caption("Top 10 by traded value and by volume. Source: NSE live-analysis → Yahoo Nifty-50 fallback when NSE blocks (403).")

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
        st.info("Most-active value list temporarily unavailable (NSE 403 / throttle). Yahoo fallback also empty — try Fast Refresh after market open.")
with mac2:
    st.markdown("##### 📦 Most Active by Volume")
    if not ma_vol.empty:
        st.dataframe(
            ma_vol.style.format({"LTP": "₹{:,.2f}", "% Chg": "{:+.2f}%", "Volume": "{:,.0f}", "Value (₹ Lakh)": "{:,.2f}"}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Most-active volume list temporarily unavailable (NSE 403 / throttle). Yahoo fallback also empty — try Fast Refresh after market open.")

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
    prev_map = st.session_state.get("heatmap_prev_pct") or {}
    new_map = {}
    html_cells = []
    for _, row in heat_df.iterrows():
        pct = row["% Chg"]
        sym = row["Symbol"]
        new_map[sym] = pct
        # colour scale (day % change)
        if pct >= 2:
            bg = "#10b981"
        elif pct >= 1:
            bg = "#34d399"
        elif pct >= 0.3:
            bg = "#6ee7b7"
        elif pct > -0.3:
            bg = "#94a3b8"
        elif pct > -1:
            bg = "#fca5a5"
        elif pct > -2:
            bg = "#f87171"
        else:
            bg = "#ef4444"
        # Refresh-to-refresh direction arrow (intraday movement of the day-% figure)
        arrow = ""
        if sym in prev_map:
            delta = pct - float(prev_map[sym])
            if delta > 0.05:
                arrow = ' <span style="font-size:10px;">▲</span>'
            elif delta < -0.05:
                arrow = ' <span style="font-size:10px;">▼</span>'
            else:
                arrow = ' <span style="font-size:10px;opacity:0.5;">●</span>'
        html_cells.append(
            f'<div class="heat-cell" style="background:{bg};">'
            f'<div class="hc-sym">{sym}{arrow}</div>'
            f'<div class="hc-pct">{pct:+.2f}%</div>'
            f'<div class="hc-ltp">₹{row["LTP"]:,.1f}</div></div>'
        )
    st.session_state.heatmap_prev_pct = new_map
    st.markdown('<div class="heat-grid">' + "".join(html_cells) + "</div>", unsafe_allow_html=True)
    st.caption("▲ / ▼ = day-% moved up / down vs previous refresh on this session (intraday path). Colour = full-day % change.")

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

    # Deep independent assessment below the colour grid
    bu_lines, bu_tone = assess_builtup_deep(bu_df)
    st.markdown("#### 🧠 Built-up deep assessment & recommendation")
    st.caption("Independent read of the grid: multi-day streaks + price% + volume/OI proxy — not colour cells alone.")
    assess_html = '<div class="analysis-box">'
    assess_html += f'<div style="margin-bottom:8px;">{bu_tone}</div>'
    for line in bu_lines:
        assess_html += f'<div style="margin-bottom:6px;">{line}</div>'
    assess_html += (
        '<div style="margin-top:8px;font-size:12px;color:#94a3b8;">'
        'Use multi-day LB with rising price for long bias; multi-day SB with falling price for short bias. '
        'SC after a decline can squeeze; LU after a rally often marks distribution. Not advice — confirm with price action.'
        '</div></div>'
    )
    st.markdown(assess_html, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------
# Corporate Actions + Upcoming Results (Nifty 50)  — v7.6.2 display
# -------------------------------------------------
st.markdown('<div class="section-header">📋 Corporate Actions & Upcoming Results — Nifty 50</div>', unsafe_allow_html=True)
st.caption(
    "Dividends, bonuses, splits, rights + Nifty 50 earnings/results over the next 10 days. "
    "Results: Moneycontrol NIFTY 50 results-calendar (id=9). Actions: NSE → Moneycontrol fallback."
)

ca_df = get_corporate_actions(universe)
res_df = get_upcoming_results(universe, days=10)

if ca_df.empty and (res_df is None or res_df.empty):
    st.info(
        "No upcoming corporate actions / results for Nifty 50 right now "
        "(NSE often returns 403 from cloud IPs; Moneycontrol fallback also empty). "
        "Try again during market hours or from a home network."
    )
else:
    # --- Corporate actions (compact list, no expander) ---
    if not ca_df.empty:
        ca_html = (
            '<div class="ca-box">'
            '<div style="font-weight:700;margin-bottom:8px;">📌 Corporate actions '
            '(dividends · bonuses · splits · rights)</div>'
        )
        for _, row in ca_df.iterrows():
            ca_html += (
                f'<div style="margin-bottom:6px;">'
                f'<b>{row.get("Symbol", "")}</b> — {row.get("Purpose", "—")} '
                f'| Ex: {row.get("Ex-Date", "—")} | Record: {row.get("Record Date", "—")}'
                f'</div>'
            )
        ca_html += "</div>"
        st.markdown(ca_html, unsafe_allow_html=True)

    # --- Upcoming results: 10-day rolling date strip + symbols under each date ---
    if res_df is not None and not res_df.empty:
        from datetime import timedelta as _td
        _ist = pytz.timezone("Asia/Kolkata")
        _today = datetime.now(_ist).date()
        # Build 10-day window starting today
        day_list = [_today + _td(days=i) for i in range(10)]
        # Group symbols by date
        by_date = {d: [] for d in day_list}
        purposes = []
        for _, row in res_df.iterrows():
            sym = str(row.get("Symbol") or "").strip().upper()
            if not sym:
                continue
            d_raw = row.get("Date") or ""
            d_obj = None
            # Prefer SortDate-like parsing via common formats in the Date column
            for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y"):
                try:
                    d_obj = datetime.strptime(str(d_raw).strip()[:16], fmt).date()
                    break
                except Exception:
                    continue
            if d_obj is None:
                # try day-month only with current/next year
                for fmt in ("%d %b", "%d %B"):
                    try:
                        tmp = datetime.strptime(str(d_raw).strip()[:12], fmt).date().replace(year=_today.year)
                        if tmp < _today - _td(days=20):
                            tmp = tmp.replace(year=_today.year + 1)
                        d_obj = tmp
                        break
                    except Exception:
                        continue
            if d_obj is None:
                continue
            # Snap into nearest day in our 10-day window if within range
            if d_obj in by_date:
                if sym not in by_date[d_obj]:
                    by_date[d_obj].append(sym)
            purpose = str(row.get("Purpose") or "Results")
            purposes.append(purpose.lower())

        # Simple heading: if everything looks like Q2 / quarterly results, label as Q2
        q2ish = sum(1 for p in purposes if "q2" in p or "quarter" in p or "result" in p)
        if purposes and q2ish >= max(1, int(0.6 * len(purposes))):
            heading = "📊 Q2 Results — next 10 days"
        else:
            heading = "📊 Upcoming Results — next 10 days"

        cells = []
        for d in day_list:
            syms = by_date.get(d) or []
            label = d.strftime("%d %b")  # e.g. 30 Oct
            if syms:
                sym_txt = ", ".join(syms)
                empty_cls = ""
            else:
                sym_txt = "—"
                empty_cls = " empty"
            cells.append(
                f'<div class="res-day{empty_cls}">'
                f'<div class="rd-date">{label}</div>'
                f'<div class="rd-syms">{sym_txt}</div>'
                f'</div>'
            )
        res_html = (
            '<div class="ca-box">'
            f'<div style="font-weight:700;margin-bottom:10px;">{heading}</div>'
            '<div class="res-date-strip">' + "".join(cells) + '</div>'
            '</div>'
        )
        st.markdown(res_html, unsafe_allow_html=True)
    else:
        st.caption("No Nifty 50 results found in the next 10 days from available sources.")

st.markdown("---")

# -------------------------------------------------
# Top 5 Business News (30-min refresh)
# -------------------------------------------------
st.markdown('<div class="section-header">📰 Top 6 Market-Moving Business News</div>', unsafe_allow_html=True)
st.caption("India-first + global headlines (ET / Moneycontrol / Bloomberg / FT / Trading Economics context via Google News). Auto-refreshes every 30 minutes.")

biz_news = get_top_business_news()

# Top 6 linked list (quick scan)
if not biz_news:
    st.info("News feed temporarily unavailable.")
else:
    news_html = '<div class="news-box">'
    for i, n in enumerate(biz_news[:6], 1):
        if n.get("link"):
            news_html += f'<div style="margin-bottom:8px;"><b>{i}.</b> <a href="{n["link"]}" target="_blank">{n["title"]}</a></div>'
        else:
            news_html += f'<div style="margin-bottom:8px;"><b>{i}.</b> {n["title"]}</div>'
    news_html += "</div>"
    st.markdown(news_html, unsafe_allow_html=True)

# Auto refresh
if auto_refresh:
    time.sleep(120)
    st.rerun()
