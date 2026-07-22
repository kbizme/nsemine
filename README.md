## Simplest, Cleanest and Efficient Python Library to Scrape Stocks, FnO & Indices Data From The NSEIndia(New) and NiftyIndices Website.

`nsemine` is a Python library designed to provide a clean and straightforward interface for scraping data from the National Stock Exchange of India (NSE) and the Nifty Indices website. It aims to simplify the process of retrieving various market data, including indices, stock information, futures & options data, and general NSE-related utilities. This library is built to be efficient and user-friendly, catering to **developers**, **traders**, **investors** who need reliable NSE data for financial analysis, algorithmic trading, and data visualization.

## Features

* **Asynchronous Data Retrieval:**  &nbsp;Experience non-blocking, asynchronous data retrieval for optimal performance. Leverage the power of `asyncio` to fetch market data without delays, ensuring your applications remain responsive.

* **High-Speed Data Acquisition:**  &nbsp;Utilize the speed and efficiency of `aiohttp` and `requests` under the hood. This library is designed for rapid data acquisition, enabling you to get the latest market insights quickly.

* **Unparalleled Data Flexibility:** &nbsp; `nsemine` empowers you with the complete data manipulation. Choose between the raw, unfiltered API response for maximum customization, OR leverage our intelligently processed data structures for streamlined analysis and immediate insights.

* **Intelligent Built-in Caching:**  &nbsp;Minimize API requests with the intelligent built-in caching mechanism. Reduce your reliance on the NSE API and save you from getting blocked by the NSE Anti-Scraper Robots.

* **Clean and Intuitive API:**  &nbsp;Designed for simplicity and ease of use, the library provides a clean and intuitive API, allowing developers to quickly integrate NSE data into their projects.

* **Comprehensive Data Coverage:**  &nbsp;Access a wide range of NSE data, including indices, stocks, futures, and options, all within a single, unified library.

* **Robust Error Handling:**  &nbsp;Built with robust error handling to ensure your applications remain stable and resilient, even in challenging network conditions.

## Installation

You can install `nsemine` by pip or via github.

>  ``pip install nsemine``

OR

>``pip install git+https://github.com/kbizme/nsemine.git``

## Why I Built This Library

Well, there are several Python libraries available for scraping NSE data, I developed this library to address specific needs that were not adequately met by the existing solutions. I have used this library in my project. You can use it in yours.

* **Custom Data Requirements:**  &nbsp;&nbsp;``nsemine`` is tailored to retrieve specific data points and formats that were essential for the project, which may not be available in other libraries.

*  **Unique Data Structures:** The project required data in a particular structure and format, which this library delivers directly, eliminating the need for extensive post-processing.

* **Data Availability:**&nbsp;&nbsp;  ``nsemine`` is designed to access and provide data that may not be available or easily accessible through other existing NSE scraping libraries.

* **Performance and Reliability:** Optimized for speed and stability, ensuring reliable data retrieval, especially for real-time and high-frequency data. It uses ``numpy`` and ``pandas`` vectorized operations for faster data pre-processing. Most of the possible errors are handled with Exceptions, thus, even if any error occurs the application will remain stable.

* **Ease of Use:**  &nbsp;&nbsp;``nsemine`` aims to provide a simple and intuitive interface, making it easy for developers to integrate NSE data into their applications. This library is designed to offer a more specialized and efficient solution for users who require precise and customized NSE data.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bug fixes, feature requests, or improvements.

## Documentation

_Work in progress..._ Meanwhile, you may explore the library. ReadTheDocs style documentation will be added upon complete library build.

Basic Usage Example:
`from nsemine import nse, live, historical, fno`

1. get live stock and index quotes
 - quotes = `live.get_stock_live_quotes(stock_symbol='TCS')`
 - index_quote = `live.get_index_live_price(index='NIFTY 50')`

2. You can download stock and index historical data from the `historical` module.
3. NSE related any data is available on the `nse` module.
4. FNO related data functions are available on `fno` module [in development].

TIP:  You may get all the available function in each modules, by using a dot afte the module name, like this -> live.   or -> nse.   [Your IDE may highlight all the available functions, all functions contains comprehensive docstring]
This is a workaround while the full documentation is ready.

## WARNING

Still in Maturing phase, so expect frequent updates..

# Documentation

Basic import:

```python
from datetime import datetime
from nsemine import live, historical, nse, fno
```

## Module 1:  `live.py` 

#### `get_stock_live_quotes(stock_symbol: str, series: str | None = None, raw: bool = False)`

Fetches the live quote for a stock symbol.

- `stock_symbol`: NSE stock symbol, such as `"TCS"` or `"INFY"`.
- `series`: NSE series to query. Defaults to `"EQ"` when not provided.
- `raw`: When `True`, returns the raw NSE JSON response. When `False`, returns a cleaned dictionary.
- Returns: `dict` for quote data, or `None` if the request or processing fails.

Example:

```python
quote = live.get_stock_live_quotes("TCS")
raw_quote = live.get_stock_live_quotes("TCS", raw=True)
```

#### `get_index_live_price(index: str = "NIFTY 50", raw: bool = False)`

Fetches live price data for a single NSE index.

- `index`: Index name, such as `"NIFTY 50"` or `"NIFTY BANK"`.
- `raw`: When `True`, returns the raw index watch JSON response.
- Returns: a dictionary with `symbol`, `open`, `high`, `low`, `close`, `previous_close`, `change`, `changepct`, `year_high`, `year_low`, and sometimes `datetime`; returns `None` if the index is not found or an error occurs.

Example:

```python
nifty = live.get_index_live_price()
bank_nifty_raw = live.get_index_live_price("NIFTY BANK", raw=True)
```

#### `get_all_indices_live_snapshot(raw: bool = False)`

Fetches a live snapshot of all available NSE indices.

- `raw`: When `True`, returns the raw JSON response.
- Returns: a `pandas.DataFrame` with columns including `key`, `index`, `symbol`, `open`, `high`, `low`, `close`, `previous_close`, `change`, `changepct`, `year_high`, `year_low`, `advances`, `declines`, `unchanged`, `one_week_ago`, `one_month_ago`, and `one_year_ago`; returns `None` on failure.
- Note: processed output drops rows containing missing values.

Example:

```python
indices = live.get_all_indices_live_snapshot()
```

#### `get_all_securities_live_snapshot(series: str | list | None = None, raw: bool = False)`

Fetches a live snapshot for all NSE securities.

- `series`: Optional series filter, such as `"EQ"` or `["EQ", "SM"]`.
- `raw`: When `True`, returns the raw JSON response.
- Returns: a `pandas.DataFrame` with `symbol`, `series`, `close`, `previous_close`, `change`, `changepct`, `volume`, `traded_value`, and `market_cap`; returns `None` on failure.
- Note: processed `volume`, `traded_value`, and `market_cap` are scaled to absolute values.

Example:

```python
all_securities = live.get_all_securities_live_snapshot()
eq_securities = live.get_all_securities_live_snapshot(series="EQ")
```

#### `get_index_constituents_live_snapshot(index: str = "NIFTY 50", raw: bool = False)`

Fetches live constituent data for an NSE index.

- `index`: Index name, such as `"NIFTY 50"`, `"NIFTY BANK"`, or `"NIFTY NEXT 50"`.
- `raw`: When `True`, returns the raw JSON response.
- Returns: a `pandas.DataFrame` with `symbol`, `ltp`, `previous_close`, `change`, `changepct`, `weightage`, `volume`, and `turnover`; returns `None` on failure.
- Note: NSE-provided `volume` and `turnover` units are preserved.

Example:

```python
constituents = live.get_index_constituents_live_snapshot("NIFTY 50")
```

#### `get_fno_indices_live_snapshot(df: bool = True)`

Fetches live data for the NSE F&O indices.

- `df`: When `True`, returns a `pandas.DataFrame`. When `False`, returns a dictionary keyed by derivative symbols such as `NIFTY`, `BANKNIFTY`, `FINNIFTY`, `MIDCPNIFTY`, and `NIFTYNXT50`.
- Returns: index snapshot data with `datetime`, `open`, `high`, `low`, `close`, `previous_close`, `change`, `changepct`, `year_high`, and `year_low`; returns `None` on failure.

Example:

```python
fno_indices = live.get_fno_indices_live_snapshot()
fno_indices_dict = live.get_fno_indices_live_snapshot(df=False)
```

#### `get_stock_intraday_tick_by_tick_data(stock_symbol: str, candle_interval: int | None = None, raw: bool = False)`

Fetches current-day intraday tick data for a stock and can convert it into OHLC candles.

- `stock_symbol`: NSE stock symbol.
- `candle_interval`: Optional candle interval in minutes. If omitted, tick data is returned.
- `raw`: When `True` and `candle_interval` is not provided, returns the raw JSON response.
- Returns: a tick `pandas.DataFrame`, an OHLC `pandas.DataFrame` when `candle_interval` is provided, raw JSON when requested, or `None` on failure.

Example:

```python
ticks = live.get_stock_intraday_tick_by_tick_data("INFY")
five_minute = live.get_stock_intraday_tick_by_tick_data("INFY", candle_interval=5)
```

## Module 2: `historical.py`

#### `get_stock_historical_data(stock_symbol: str, start_datetime: datetime, end_datetime: datetime = datetime.now(), interval: int | str = 1, raw: bool = False)`

Fetches historical chart data for an equity symbol.

- `stock_symbol`: NSE stock symbol.
- `start_datetime`: Start of the requested period.
- `end_datetime`: End of the requested period. Defaults to the time at module import.
- `interval`: Intraday interval in minutes, or `"D"`, `"W"`, or `"M"` for daily, weekly, or monthly data.
- `raw`: When `True`, returns the raw chart API response.
- Returns: a processed `pandas.DataFrame`, raw dictionary, or `None` on failure.

Example:

```python
df = historical.get_stock_historical_data("TCS", datetime(2025, 1, 1), interval="D")
```

#### `get_index_historical_data(index: str, start_datetime: datetime, end_datetime: datetime = datetime.now(), interval: int | str = "3", raw: bool = False)`

Fetches historical chart data for an NSE index.

- `index`: Index name, such as `"NIFTY 50"` or `"NIFTY BANK"`.
- `start_datetime`: Start of the requested period.
- `end_datetime`: End of the requested period. Defaults to the time at module import.
- `interval`: Intraday interval in minutes, or `"D"`, `"W"`, or `"M"` for daily, weekly, or monthly data.
- `raw`: When `True`, returns the raw chart API response.
- Returns: a processed `pandas.DataFrame`, raw dictionary, or `None` on failure.

Example:

```python
df = historical.get_index_historical_data("NIFTY 50", datetime(2025, 1, 1), interval="D")
```

## Module 3: `nse.py`

#### `get_market_status(market_name: str | None = None)`

Fetches current NSE market status.

- `market_name`: Optional market code. Supported shortcuts include `CM`, `CUR`, `COM`, `DB`, and `CURF`.
- Returns: raw market status list when no market is supplied, `True` or `False` for a matched market, the raw list when no shortcut matches, or `None` on failure.

Example:

```python
status = nse.get_market_status()
is_cm_open = nse.get_market_status("CM")
```

#### `get_market_stats()`

Fetches NSE market statistics such as yearly highs/lows, circuit-breaker counts, and positive/negative stock counts.

- Returns: a dictionary containing market statistics with `asOnDate` converted to `datetime`, or `None` on failure.

#### `get_holiday_lists()`

Fetches NSE capital market holidays.

- Returns: a `pandas.DataFrame` with `date`, `day`, and `description`, or `None` on failure.

#### `get_all_indices_list()`

Fetches the list of available NSE indices.

- Returns: a `pandas.DataFrame` with `trading_index` and `full_name`, or `None` on failure.

#### `get_all_equities_list(raw: bool = False)`

Fetches the NSE equity master list.

- `raw`: When `True`, returns the raw CSV-loaded DataFrame.
- Returns: a processed `pandas.DataFrame` with `symbol`, `name`, `series`, `date_of_listing`, `isin_number`, and `face_value`, or `None` on failure.

#### `get_all_sme_stocks_list(raw: bool = False)`

Fetches NSE SME-listed securities.

- `raw`: When `True`, returns the raw CSV-loaded DataFrame.
- Returns: a processed `pandas.DataFrame` with `symbol`, `name`, `series`, `date_of_listing`, `isin_number`, and `face_value`, or `None` on failure.

#### `get_fno_stocks_lists(raw: bool = False)`

Fetches NSE F&O underlying stock symbols.

- `raw`: When `True`, returns the raw JSON response.
- Returns: a `pandas.DataFrame` with `name` and `symbol`, or `None` on failure.

#### `get_pre_open_data(key: str = "NIFTY", raw: bool = False)`

Fetches NSE pre-open market data.

- `key`: Pre-open group key, such as `"NIFTY"`, `"BANKNIFTY"`, `"SME"`, `"FO"`, `"OTHERS"`, or `"ALL"`.
- `raw`: When `True`, returns the raw JSON response.
- Returns: a `pandas.DataFrame` with `datetime`, `symbol`, `previous_close`, `close`, `change`, `changepct`, `volume`, `turnover`, `market_cap`, `year_high`, and `year_low`, or `None` on failure.

#### `get_securities_at_52_weeks_high(raw: bool = False, need_timestamp: bool = False)`

Fetches securities trading at a 52-week high.

- `raw`: When `True`, returns the raw JSON response.
- `need_timestamp`: When `True`, returns `(df, timestamp)`.
- Returns: a `pandas.DataFrame`, `(DataFrame, datetime)`, raw dictionary, or `None`.

#### `get_securities_at_52_weeks_low(raw: bool = False, need_timestamp: bool = False)`

Fetches securities trading at a 52-week low.

- `raw`: When `True`, returns the raw JSON response.
- `need_timestamp`: When `True`, returns `(df, timestamp)`.
- Returns: a `pandas.DataFrame`, `(DataFrame, datetime)`, raw dictionary, or `None`.

#### `get_securities_above_previous_close(raw: bool = False, need_timestamp: bool = False)`

Fetches securities currently trading above their previous close.

- `raw`: When `True`, returns the raw JSON response.
- `need_timestamp`: When `True`, returns `(df, timestamp)`.
- Returns: a processed `pandas.DataFrame`, `(DataFrame, datetime)`, raw dictionary, or `None`.

#### `get_securities_below_previous_close(raw: bool = False, need_timestamp: bool = False)`

Fetches securities currently trading below their previous close.

- `raw`: When `True`, returns the raw JSON response.
- `need_timestamp`: When `True`, returns `(df, timestamp)`.
- Returns: a processed `pandas.DataFrame`, `(DataFrame, datetime)`, raw dictionary, or `None`.

#### `get_securities_same_as_previous_close(raw: bool = False, need_timestamp: bool = False)`

Fetches securities currently trading at the same price as their previous close.

- `raw`: When `True`, returns the raw JSON response.
- `need_timestamp`: When `True`, returns `(df, timestamp)`.
- Returns: a processed `pandas.DataFrame`, `(DataFrame, datetime)`, raw dictionary, or `None`.

#### `get_most_liquid_stocks(raw: bool = False)`

Fetches the top 20 NSE stocks by traded volume.

- `raw`: When `True`, returns the raw JSON response.
- Returns: a `pandas.DataFrame` with `datetime`, `symbol`, `open`, `high`, `low`, `close`, `previous_close`, `change`, `changepct`, `volume`, `traded_value`, `year_high`, and `year_low`, or `None`.

#### `get_most_value_traded_stocks(raw: bool = False)`

Fetches the top 20 NSE stocks by traded value.

- `raw`: When `True`, returns the raw JSON response.
- Returns: a `pandas.DataFrame` with `datetime`, `symbol`, `open`, `high`, `low`, `close`, `previous_close`, `change`, `changepct`, `volume`, `traded_value`, `year_high`, and `year_low`, or `None`.

#### `get_todays_gainers(key: str = "ALL", raw: bool = False)`

Fetches top gainers for the current trading session.

- `key`: Group selector. Supported values include `ALL`, `NIFTY`, `NIFTYNEXT50`, `NIFTYNXT50`, `BANKNIFTY`, `FNO`, `GT20`, and `LT20`.
- `raw`: When `True`, returns the raw JSON response.
- Returns: a processed movers `pandas.DataFrame`, or `None` on failure.

#### `get_todays_losers(key: str = "ALL", raw: bool = False)`

Fetches top losers for the current trading session.

- `key`: Group selector. Supported values include `ALL`, `NIFTY`, `NIFTYNEXT50`, `NIFTYNXT50`, `BANKNIFTY`, `FNO`, `GT20`, and `LT20`.
- `raw`: When `True`, returns the raw JSON response.
- Returns: a processed movers `pandas.DataFrame`, or `None` on failure.

## Module 4: `fno.py` [WIP]

#### `get_oi_spurts(raw: bool = False, sentiment_analysis: bool = True)`

Fetches NSE open-interest spurt data.

- `raw`: When `True`, returns the raw JSON response.
- `sentiment_analysis`: When `True`, merges OI data with NIFTY 500 live constituent prices and adds `market_action` and `interpretation`.
- Returns: a `pandas.DataFrame`, raw dictionary, or `None` on failure.
- Sentiment labels include `Long Buildup`, `Short Buildup`, `Short Covering`, `Long Unwinding`, and `Neutral`.

Example:

```python
oi = fno.get_oi_spurts()
oi_without_sentiment = fno.get_oi_spurts(sentiment_analysis=False)
```

#### `get_stock_option_details(symbol: str, only_expiry: bool = False, only_strikes: bool = False, raw: bool = False)`

Fetches available stock option expiry dates and strike prices for a symbol.

- `symbol`: F&O stock symbol, such as `"TCS"` or `"AUBANK"`.
- `only_expiry`: When `True`, returns only available expiry dates as `datetime.date` values.
- `only_strikes`: When `True`, returns only available strike prices as integers.
- `raw`: When `True`, returns the raw JSON response.
- Returns: a dictionary containing `expiry_dates` and `strike_prices`, a list of expiry dates, a list of strike prices, raw dictionary, or `None`.

Example:

```python
details = fno.get_stock_option_details("TCS")
expiries = fno.get_stock_option_details("TCS", only_expiry=True)
strikes = fno.get_stock_option_details("TCS", only_strikes=True)
```
