# Apex Market Terminal

**Version:** v7.6.12 (build 2026-10-30)

Streamlit dashboard for Indian equities — live quotes, Renko, option chain (premiums + OI), market breadth, heatmap, corporate actions, and results calendar.

---

## Features

### Stock workspace
- **Stock selector** — NSE universe (Nifty 50 focused + watchlist)
- **Instant Snapshot** — LTP, day H/L, 5D avg / H/L / VWAP, bias, PCR, max pain, mini 5D bars, news expander
- **Options panel (ATM ±6)** — Call / Strike / Put from **Research360** (primary), Groww fallback  
  - Natural ascending strikes (e.g. 630 → 690 ATM → 750)  
  - ATM row highlighted and auto-scrolled into view  
  - Caption above table (expiry, source, spot, max pain)
- **Open Interest chart** — Full-chain Call OI vs Put OI bars, ATM & Max Pain lines with values  
  - Same current monthly expiry as the options table

### Market overview
- **Market Indices & Global Instruments** — India indices, GIFT Nifty, FX, US futures, yields, commodities, crypto  
  - Responsive cards (desktop multi-column; mobile ~2 per row)
- **Breadth / PCR / Max Pain / IV** where available
- **Nifty 50 Heatmap** — equal-size cells, soft green/red, mobile-friendly grid

### Technicals & scanners
- **Live Analytics** — candlestick + volume, Renko (ATR-based box ladder)
- **Renko scanner** — multi-stock signals with CSV download
- **Built-up cycle** table

### Corporate & news
- **Corporate actions** — dividends / actions (NSE + Moneycontrol merge; known-event safety net e.g. INFY)
- **Upcoming results** — 10-day rolling date strip with symbols under each date (no duplicate expander table)
- **Top gainers / losers**, most active, top news

### UX
- Dark / light theme
- **Fast Refresh** — soft-clears live quotes (Renko cache stays warm)
- Wide layout, mobile-aware grids

---

## Data sources

| Area | Source (priority) |
|------|-------------------|
| Equity / index quotes | Yahoo Finance, TradingView / Investing fallbacks |
| Option premiums + OI | **Research360 (Trendlyne API)** → Groww → NSE → Yahoo |
| Corporate actions | NSE + Moneycontrol (+ targeted backups) |
| Results calendar | Moneycontrol / NSE-style feeds |
| PCR / sentiment | QuantSapp and related feeds where available |

**Note:** NSE option-chain API often returns **403** from cloud hosts (e.g. Streamlit Cloud). Research360 is the primary path for live premiums and OI. Premiums are **never simulated**.

Option expiry logic uses **current / future monthly** series only (expired months rejected; ATM-band near-zero premiums skipped so stale series are not shown).

---

## Requirements

```text
streamlit
yfinance
pandas
numpy
plotly
requests
pytz
```

Python 3.10+ recommended.

---

## Run locally

```bash
pip install streamlit yfinance pandas numpy plotly requests pytz
streamlit run Apex_Market_Terminal_v7.6.12.txt
```

Or rename to `app.py`:

```bash
mv Apex_Market_Terminal_v7.6.12.txt app.py
streamlit run app.py
```

---

## Deploy (Streamlit Community Cloud)

1. Put the script in a GitHub repo (as `app.py` or set the main file in Cloud settings).
2. Add a `requirements.txt` with the packages above.
3. Deploy; use **Fast Refresh** in the app after deploy so option/quote caches reset.

---

## Version highlights (v7.6.x)

| Ver | Notes |
|-----|--------|
| **7.6.12** | Natural strike order; ATM auto-scroll into view; caption above options table |
| 7.6.11 | Removed green bar above options; smaller fonts |
| 7.6.10 | Compact options height; ATM / Max Pain **values** on OI chart |
| 7.6.9 | Options height closer to snapshot; high-contrast OI strike labels |
| 7.6.8 | Current-expiry only (no expired Oct 0.05 premiums); green panels |
| 7.6.7 | Snapshot + options side-by-side; full OI chart from Research360 |
| 7.6.6 | Research360 options primary |
| 7.6.5 | Groww options path; no random premiums |
| 7.6.4 | Removed fake/random option prices |
| 7.6.3 | Corporate actions merge + INFY dividend backup |
| 7.6.2 | Results date strip; indices responsive grid; download-button fix |

---

## Layout (stock section)

```text
[ Stock dropdown ]
[ Instant Snapshot  |  Options ATM ±6 table ]
[ Open Interest by Strike chart              ]
[ Market Indices & Global Instruments        ]
[ … rest of terminal unchanged … ]
```

---

## Disclaimer

For information and education only. Not investment advice. Market data can be delayed or unavailable; always confirm with your broker before trading.
