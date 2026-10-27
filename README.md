# Apex Market Terminal

Live Indian equities & indices terminal built with **Streamlit**.  
Focus: Nifty 50, Renko intraday signals, options sentiment (PCR / max pain), breadth, built-up cycle, and global macro context.

**Current build:** `v7.2` (2026-10-27)

---

## Quick start

```bash
pip install streamlit yfinance pandas numpy plotly pytz requests
streamlit run apex_market_terminal_v7.2.txt
# (rename to .py if you prefer)
```

Data sources (priority varies by instrument): TradingView → Investing.com → TradingEconomics (oil) → Yahoo Finance · NSE option chain / corporate filings.

---

## Main modules

| Area | What it does |
|------|----------------|
| **Stock snapshot** | LTP, day H/L, 5D avg / high-low / VWAP, bias, equity PCR & max pain, **last-5-session mini bars** |
| **VWAP × PCR screen** | Top 5 above 5D VWAP with **lowest PCR**; top 5 below VWAP with **highest PCR**; independent positional analysis (expiry / ~1 month) |
| **Indices & globals** | Nifty, Bank Nifty, Sensex, GIFT Nifty, VIX, US futures, yields, crude, metals, Asia, etc. |
| **Global bias** | Rule-based day bias from Nifty VWAP, GIFT, US/Asia moves, DXY, crude |
| **Breadth / PCR / IV** | Nifty 50 bullish vs bearish count; index PCR, max pain, ATM IV |
| **Charts** | Candles + EMA20/50; **Renko** with box ladder Daily ATR → /6 (1H) → /12 (30m) → /24 (15m) |
| **Renko scanner** | Live BUY / BULLISH / SELL / BEARISH on 15m → 30m → 1H; **Confidence %** |
| **Simulation analytics** | Historical replay of same rules; Qualified (≥+2) vs Failed (stop first); 7/15/30/60d |
| **Options matrix** | ATM ±2 CE/PE (nearest expiry) |
| **Gainers / losers / most active** | Nifty 50 movers + NSE all-equity value & volume leaders |
| **Heatmap** | Nifty 50 day % colour + **▲/▼ vs previous refresh** |
| **Built-up cycle** | LB / SB / SC / LU grid + deep assessment |
| **Corporate actions + results** | Forthcoming actions; best-effort **results ~next 7 days** |
| **News** | Top 6 India-first headlines + **Visual Daily Brief** (up to 10 cards) |

---

## Version history

### v7.2 — 2026-10-27
### v7.2.1 patch (same day)

- Snapshot **vertical** 5-day bars (left cluster, compact).
- VWAP × PCR section **compact** labels.
- Renko **scan faster**: longer OHLC/ATR cache, 14 workers, Scan button no longer clears warm OHLC/ATR.
- Built-up deep assessment **colour-coded** (🟢 long / 🔴 short / 🔵 short covering / 🟡 long unwinding).
- Replaced expander “Visual Daily Brief” with **pictorial PNG** “Aaj Ki Taaza Khabar” (snapshot strip + top 10) + download.


**Snapshot & positional**

1. **Last-5-session price bars** inside the stock Instant Snapshot box (green / red / grey, date, close, %).
2. **New section: 5D VWAP × PCR Screen**
   - Above 5D VWAP + lowest equity PCR → top 5 (constructive / long bias).
   - Below 5D VWAP + highest PCR → top 5 (cautious / short bias).
   - Independent positional analysis (near expiry for longs, ~1 month for shorts).
   - **Not** the same as the Renko intraday scanner; intentionally separate so day/1H/30m/15m signals stay clean.

**Renko scanner**

3. **Confidence %** column on every live signal.
   - Live base: timeframe (1H > 30m > 15m) + brick age + EMA distance + BUY/SELL vs plain BULLISH/BEARISH.
   - **Blended with simulation Hit+2 rates** by TF × Signal when the 30d (or fallback) sample has enough trades (± up to ~12 pts).
   - Improves as simulation cache warms (scan / refresh / ongoing use).
   - **Sort order unchanged:** BUY → BULLISH (15m → 30m → 1H, newest age on top), then SELL → BEARISH same TF order.
4. Clarified behaviour: live table only shows **current** two consecutive same-direction bricks. Failed signals disappear when bricks reverse; outcomes live in Simulation Analytics only.
5. **No Daily Renko positional scanner** added — VWAP × PCR is the single positional layer (avoids double signals and missed/conflicting reads).

**Heatmap**

6. **▲ / ▼ / ●** on each cell vs **previous refresh in this session** (intraday path of the day-% figure). Colour scale still = full-day % change.

**Corporate & news**

7. **Upcoming results** (~7 days) alongside corporate actions (best-effort NSE endpoints).
8. News layout: **Top 6 headlines** (left) + **Visual Daily Brief** expander with up to 10 digest-style cards (right).

**Other**

9. Session state for heatmap previous-% and Renko confidence weights.
10. Refresh / soft-clear list includes new caches (`get_vwap_pcr_screen`, `get_upcoming_results`, heatmap, etc.).

---

### v7.1 — 2026-10-25

Built on v7 core:

1. Chart timeframe radio: **15 Minutes** (Renko box = Daily ATR / 24).
2. Scanner display order: **BUY / BULLISH first** (15m → 30m → 1H, age newest on top), then **SELL / BEARISH** same TF order.
3. **Simulation:** track Qualified (≥+2 before stop) vs Failed (2-brick stop first); outcome log for 7 / 15 / 30 / 60d; 30d logic-change prompt from tracked outcomes.
4. **Built-up:** deep assessment box under the colour grid (sustain LB/SB, SC bounce, LU caution).
5. **News:** top 6, India-first queries (ET / Moneycontrol / Bloomberg / FT / Trading Economics context via Google News).

**v7 core retained:** 15m scanner TF, box ladder D/6 → /12 → /24, signal rules unchanged.

---

### v7 core (retained through v7.1 / v7.2)

- Streamlit wide layout, dark/light theme CSS.
- Watchlist, auto-refresh (2 min), soft cache clear on “Refresh Now”.
- Multi-source live quotes (TV, Investing, TE for oil, Yahoo fallback).
- GIFT Nifty multi-source with timestamp preference.
- Stock & index 5-day analytics (VWAP, bias).
- Option sentiment: NSE chain → Quantsapp → NiftyTrader (PCR, max pain, ATM IV).
- Renko generation from OHLC; live signal = last two bricks same colour; BUY/SELL if close above/below EMA20.
- Box size ladder from daily ATR (7-day avg of ATR14 preferred).
- Options ATM ±2 matrix, top gainers/losers, most active (NSE), Nifty 50 heatmap.
- Built-up cycle (price % + volume proxy for OI %) for active F&O names.
- Corporate actions from NSE.
- Global opening commentary and rule-based day bias.

---

## Renko signal rules (unchanged since v7)

- Need **two consecutive bricks** in the same direction.
- **BUY** if both green and price **above** EMA20; else **BULLISH**.
- **SELL** if both red and price **below** EMA20; else **BEARISH**.
- Entry ≈ 2nd brick close; exit / stop context ≈ opposite side of 1st brick (simulation uses 2-brick stop, targets +2 / +3 / +4).
- Box size: **1H = ATR/6**, **30m = ATR/12**, **15m = ATR/24**.

Live list ≠ history: only **current** structure is shown. Simulation reconstructs past signals for quality stats and Confidence blend.

---

## Design choices (v7.2)

| Topic | Choice | Why |
|-------|--------|-----|
| Positional layer | 5D VWAP × equity PCR only | Multi-factor, expiry/month horizon; avoids stacking a Daily Renko scanner on the same names |
| Confidence | Live + sim Hit+2 blend | Improves every time simulation has enough TF×Signal samples; no manual recalibration |
| Heatmap arrows | Session refresh-to-refresh | Shows whether the day-% is still expanding or fading intraday |
| Results | Best-effort NSE | Same family as corporate actions; empty when exchange endpoints throttle |

---

## Disclaimer

Not financial advice. Prices and option data can lag or fail (NSE throttle, weekends, holidays). Always confirm with your broker before trading.

---

## File map

| File | Description |
|------|-------------|
| `apex_market_terminal_v7.2.txt` | Full Streamlit app (rename to `.py` to run) |
| `README.md` | This document — features + version changelog |
