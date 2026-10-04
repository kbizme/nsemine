# ⚡ nsemine

## **High-Performance, Asynchronous Python Interface for NSEIndia & NiftyIndices Websites.**

[![PyPI Version](https://img.shields.io/pypi/v/nsemine?style=for-the-badge&color=007ACC)](https://pypi.org/project/nsemine/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)

**A clean, fast, and resilient library designed for algorithmic traders, developers, and quantitative researchers to extract equities, F&O, indices, and market depth without getting blocked or rate-limited.**

---

## 🚀 Key Features

**⚡ Async-Native Engine:** Built on top of `asyncio` and high-speed C-bindings (`curl_cffi`) with Chrome TLS fingerprint impersonation to bypass Akamai Web Application Firewalls (WAF).

**🏎️ Throttled Batch Concurrency:** Fetch hundreds of live stock quotes simultaneously using managed event loops (`nest_asyncio` safe) and token stampede guards.

**📊 Vectorized Pre-processing:** Leverages `pandas` and `numpy` vectorized transformations to parse incoming payloads into clean, typed DataFrames (`Int64` volume casting, float conversions).

**🔒 Smart Session Warmup:** Automatic sequential cookie acquisition (`nsit`, `bm_sv`) and lock-guarded session re-priming on token expiration.

**🌐 Comprehensive Data Coverage:** Access a wide range of NSE data, including live quotes, tick-by-tick intraday data, option chain metadata, market depth, advance/decline dynamics, and historical data across Equities and F&O, all within a single unified library.

**💾 Intelligent Caching:** Minimizes API requests with the intelligent built-in caching mechanism. Reduce your reliance on the NSE API and save you from getting blocked by the NSE Anti-Scraper Bots Protection.. [WIP]

**🔄 Unparalleled Data Flexibility:** &nbsp; `nsemine` empowers you with the complete data manipulation. Choose between the raw, unfiltered API response for maximum customization, OR leverage its efficiently processed data structures for streamlined analysis and immediate insights.

**✨ Clean and Intuitive API:**  &nbsp;Designed for simplicity and ease of use, the library provides a clean and intuitive API with proper data types, allowing developers to quickly integrate NSE data into their projects.

**🚫🪲 Robust Error Handling:**  &nbsp;Built with robust error handling to ensure your applications remain stable and resilient, even in challenging network conditions.

---

## 📦 Installation

Install `nsemine` via PyPI:

```bash
pip install nsemine
```

Or install the latest development build directly from GitHub:

```bash
pip install "git+https://github.com/kbizme/nsemine.git"
```

---

## 🏁 Quick Start

```python
from datetime import datetime
from nsemine import live, historical, nse, fno

# 1. Fetch single stock quote
quote = live.get_stock_live_quotes(stock_symbol="TCS")

# 2. Fetch multiple stock quotes concurrently in a single call
df_batch = live.get_multiple_stock_live_quotes(
    symbols=['TCS', 'HDFCBANK', 'INFY', 'RELIANCE', 'SBIN'],
    max_concurrent=15
)

# 3. Get live index pricing
nifty = live.get_index_live_price(index="NIFTY 50")

# 4. Fetch historical daily data
hist_df = historical.get_stock_historical_data(
    stock_symbol="TCS", 
    start_datetime=datetime(2025, 1, 1), 
    interval="D"
)
```

---

## 📚 API Reference

```
nsemine/
├── 📈 live.py          # Real-time quotes, multi-stock batching, indices, and intraday ticks
├── 📜 historical.py    # Historical OHLC charts for equities and indices
├── ⚙️ nse.py           # Market status, master lists, gainers/losers, and 52-week data
└── 🎯 fno.py           # Open Interest spurts, option chain details, and sentiment analytics
```

---

## Module 1: `live.py`

#### `get_stock_live_quotes(stock_symbol, series='EQ', raw=False)`
Fetches real-time quote metrics for an individual stock.

```python
# Clean dictionary response
quote = live.get_stock_live_quotes(stock_symbol="TCS")

# Unfiltered raw JSON payload
raw_quote = live.get_stock_live_quotes(stock_symbol="INFY", raw=True)
```
* **Parameters:** `stock_symbol` *(str)*, `series` *(str, default 'EQ')*, `raw` *(bool, default False)*
* **Returns:** `dict | None`

---

#### `get_multiple_stock_live_quotes(symbols, series='EQ', raw=False, df=True, max_concurrent=25)`
**[NEW]** Concurrent batch fetch engine with token-stampede guards and automatic event loop adaptation.

```python
# High-speed batch retrieval into a Pandas DataFrame
symbols = ["TCS", "HDFCBANK", "INFY", "RELIANCE", "TATAMOTORS", "M&M"]
df_quotes = live.get_multiple_stock_live_quotes(
    symbols=symbols,
    series="EQ",
    max_concurrent=15
)

# Return as dict-of-dicts instead of DataFrame
dict_quotes = live.get_multiple_stock_live_quotes(
    symbols=symbols,
    df=False
)
```
* **Parameters:** `symbols` *(list | set | tuple)*, `series` *(str)*, `raw` *(bool)*, `df` *(bool)*, `max_concurrent` *(int)*
* **Returns:** `pandas.DataFrame | dict`

---

#### `get_index_live_price(index='NIFTY 50', raw=False)`
Retrieves live pricing and day ranges for an index.

```python
# NIFTY 50 live quote
nifty_quote = live.get_index_live_price(index="NIFTY 50")

# BANK NIFTY raw payload
bank_nifty_raw = live.get_index_live_price(index="NIFTY BANK", raw=True)
```
* **Parameters:** `index` *(str)*, `raw` *(bool)*
* **Returns:** `dict | None`

---

#### `get_all_indices_live_snapshot(raw=False)`
Fetches real-time snapshots across all tracked NSE market indices.

```python
# DataFrame containing advances, declines, and percent changes across all indices
indices_snapshot = live.get_all_indices_live_snapshot()
```
* **Parameters:** `raw` *(bool)*
* **Returns:** `pandas.DataFrame | dict | None`

---

#### `get_all_securities_live_snapshot(series=None, raw=False)`
Captures live price and volume data across all active NSE traded equities.

```python
# Snapshot of all equity securities
all_equities = live.get_all_securities_live_snapshot(series="EQ")
```
* **Parameters:** `series` *(str | list | None)*, `raw` *(bool)*
* **Returns:** `pandas.DataFrame | dict | None`

---

#### `get_index_constituents_live_snapshot(index='NIFTY 50', raw=False)`
Fetches live constituent stock quotes and market weights for a given index.

```python
# NIFTY 50 constituent weightages and LTPs
nifty_constituents = live.get_index_constituents_live_snapshot(index="NIFTY 50")
```
* **Parameters:** `index` *(str)*, `raw` *(bool)*
* **Returns:** `pandas.DataFrame | dict | None`

---

#### `get_fno_indices_live_snapshot(df=True)`
Fetches live data for derivative underlying index tickers (`NIFTY`, `BANKNIFTY`, `FINNIFTY`, `MIDCPNIFTY`).

```python
# F&O underlying index prices as DataFrame
fno_indices = live.get_fno_indices_live_snapshot(df=True)
```
* **Parameters:** `df` *(bool, default True)*
* **Returns:** `pandas.DataFrame | dict | None`

---

#### `get_stock_intraday_tick_by_tick_data(stock_symbol, candle_interval=None, raw=False)`
Fetches current trading session tick data or aggregates ticks into custom minute candles.

```python
# Raw tick-by-tick time-series
ticks = live.get_stock_intraday_tick_by_tick_data(stock_symbol="INFY")

# Resample ticks into 5-minute OHLC candles
ohlc_5m = live.get_stock_intraday_tick_by_tick_data(
    stock_symbol="INFY", 
    candle_interval=5
)
```
* **Parameters:** `stock_symbol` *(str)*, `candle_interval` *(int | None)*, `raw` *(bool)*
* **Returns:** `pandas.DataFrame | dict | None`

---

## Module 2: `historical.py`

#### `get_stock_historical_data(stock_symbol, start_datetime, end_datetime=datetime.now(), interval=1, raw=False)`
Fetches historical chart OHLCV data for an equity symbol.

```python
from datetime import datetime

# Daily historical candles
df_daily = historical.get_stock_historical_data(
    stock_symbol="TCS",
    start_datetime=datetime(2025, 1, 1),
    interval="D"
)

# 15-minute intraday historical candles
df_15m = historical.get_stock_historical_data(
    stock_symbol="TCS",
    start_datetime=datetime(2025, 2, 1),
    end_datetime=datetime(2025, 2, 15),
    interval=15
)
```
* **Parameters:** `stock_symbol` *(str)*, `start_datetime` *(datetime)*, `end_datetime` *(datetime)*, `interval` *(int | str)*, `raw` *(bool)*
* **Returns:** `pandas.DataFrame | dict | None`

---

#### `get_index_historical_data(index, start_datetime, end_datetime=datetime.now(), interval='3', raw=False)`
Fetches historical chart data for an index symbol.

```python
# Daily historical data for NIFTY 50
nifty_hist = historical.get_index_historical_data(
    index="NIFTY 50",
    start_datetime=datetime(2025, 1, 1),
    interval="D"
)
```
* **Parameters:** `index` *(str)*, `start_datetime` *(datetime)*, `end_datetime` *(datetime)*, `interval` *(int | str)*, `raw` *(bool)*
* **Returns:** `pandas.DataFrame | dict | None`

---

## Module 3: `nse.py`

| Function | Description | Return Type |
| --- | --- | --- |
| `get_market_status(market_name=None)` | Current market status (CM, FNO, CD, COM) | `bool \| dict` |
| `get_market_stats()` | Advances/declines, 52w highs/lows, circuit breakers | `dict` |
| `get_holiday_lists()` | Annual NSE capital market trading holidays | `pandas.DataFrame` |
| `get_all_equities_list()` | Master list of all NSE equity listings | `pandas.DataFrame` |
| `get_all_sme_stocks_list()` | Master list of NSE SME listed securities | `pandas.DataFrame` |
| `get_fno_stocks_lists()` | Underlying stock symbols eligible for F&O trading | `pandas.DataFrame` |
| `get_pre_open_data(key="NIFTY")` | Pre-market session discovery prices | `pandas.DataFrame` |
| `get_securities_at_52_weeks_high()` | Stocks trading at 52-week highs | `pandas.DataFrame` |
| `get_securities_at_52_weeks_low()` | Stocks trading at 52-week lows | `pandas.DataFrame` |
| `get_todays_gainers(key="ALL")` | Top intraday percentage gainers | `pandas.DataFrame` |
| `get_todays_losers(key="ALL")` | Top intraday percentage losers | `pandas.DataFrame` |

---

## Module 4: `fno.py`

#### `get_oi_spurts(raw=False, sentiment_analysis=True)`
Extracts open interest (OI) spurts merged with live constituent price action to compute derivative build-up sentiment.

```python
# Retrieve OI spurts with automatic sentiment labels
# (Long Buildup, Short Buildup, Short Covering, Long Unwinding)
oi_df = fno.get_oi_spurts(sentiment_analysis=True)
```
* **Parameters:** `raw` *(bool)*, `sentiment_analysis` *(bool)*
* **Returns:** `pandas.DataFrame | dict | None`

---

#### `get_stock_option_details(symbol, only_expiry=False, only_strikes=False, raw=False)`
Retrieves active contract expiry dates and available strike price chains for F&O equity underlyings.

```python
# Get expiry dates and strike arrays for TCS options
option_info = fno.get_stock_option_details(symbol="TCS")

# Get list of expiry dates only
expiries = fno.get_stock_option_details(symbol="TCS", only_expiry=True)

# Get strike price grid only
strikes = fno.get_stock_option_details(symbol="TCS", only_strikes=True)
```
* **Parameters:** `symbol` *(str)*, `only_expiry` *(bool)*, `only_strikes` *(bool)*, `raw` *(bool)*
* **Returns:** `dict | list | None`

---

## ⚠️ Disclaimer & Anti-Scraping Guidelines

* **Educational Use Only:** `nsemine` is intended for financial research, educational purposes, and personal trading algorithms. Use at your discretion and accountability.
* **Rate Limits:** Keep `max_concurrent` between `10` and `20` during live market hours to avoid Akamai rate-limiting policies. Avoid infinite tight polling loops without sleeping intervals.

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to check the [issues page](https://github.com/kbizme/nsemine/issues) or submit a pull request.

Made with ❤️ for the Indian Algorithmic Trading & Investing Community.