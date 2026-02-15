"""
*module*: `nsemine_lite.py` — An **All-Rounder** historical stock, index, future and options data downloader for NSE Exchange.\n
*author*: **Kartick Bhowmik** \n
*updated*: **15/02/2026 21:10** \n
"""
import os
import json
import time
import traceback
from datetime import datetime, timedelta
import requests
import pandas as pd

# -----------------------
# Configuration / URLs
# -----------------------
nse_chart_url = 'https://charting.nseindia.com/v1/charts/symbolHistoricalData'
first_boy = 'https://www.nseindia.com/get-quote/equity/RELIANCE/Reliance-Industries-Limited'
search_token_url = 'https://charting.nseindia.com/v1/exchanges/symbolsDynamic'


# default minimal headers (stable and simple)
default_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, br, zstd', 
    'Accept': '*/*', 
    "Referer": "https://charting.nseindia.com/",
}

# cookie filename stored in same folder as this module / notebook
COOKIE_FILE = "nse_cookie.json"
# cookie expiry window 
COOKIE_TTL = timedelta(hours=2)


# -----------------------
# Cookie manager (file-based)
# -----------------------
def _cookie_file_path():
    # using current working directory so it's alongside the notebook
    return os.path.join(os.getcwd(), COOKIE_FILE)

def save_cookie(cookie_dict: dict):
    """Save cookie dict with timestamp."""
    try:
        data = {
            "cookie": cookie_dict,
            "timestamp": datetime.now().isoformat()
        }
        with open(_cookie_file_path(), "w") as f:
            json.dump(data, f)
    except Exception:
        # don't crash on save
        traceback.print_exc()


def load_cookie():
    """Load cookie dict if fresh; otherwise return None."""
    try:
        path = _cookie_file_path()
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            data = json.load(f)
        ts = data.get("timestamp")
        if not ts:
            return None
        ts_dt = datetime.fromisoformat(ts)
        if datetime.now() - ts_dt < COOKIE_TTL:
            return data.get("cookie")
        # expired
        return None
    except Exception:
        return None

# -----------------------
# HTTP helper (session with cookie refresh)
# -----------------------
def _refresh_cookie(session: requests.Session) -> dict:
    """
    Load existing cookie if fresh.
    If missing or expired, hit the NSE 'first_boy' URL to acquire a new cookie.
    Save cookie to JSON file.
    """
    # trying to load existing cookie
    cookie = load_cookie()
    if cookie:
        session.cookies.update(cookie)
        return cookie

    # fetching fresh cookie from the first_boy
    try:
        resp = session.get(first_boy, headers=default_headers, timeout=15)
        cookie_dict = session.cookies.get_dict()

        if cookie_dict:
            filtered = {}
            for k in ("nsit", "nseappid"):
                if k in cookie_dict and cookie_dict[k] is not None:
                    filtered[k] = cookie_dict[k]

            # fallback to full cookie dict if filtered is empty
            if not filtered:
                filtered = cookie_dict

            save_cookie(filtered)
            session.cookies.update(filtered)
            return filtered

    except Exception:
        traceback.print_exc()

    return {}




def _http_get(url: str, payload: dict = None, headers: dict = None, max_retries: int = 2, timeout: int = 15):
    """
    Lightweight GET wrapper with session, cookie refresh, retries.
    Returns the requests.Response object or None.
    """
    session = requests.Session()
    # ensuring cookie have loaded or refreshed
    _refresh_cookie(session)

    if headers is None:
        headers = default_headers

    for attempt in range(max_retries):
        try:
            resp = session.get(url, headers=headers, params=payload, timeout=timeout, cookies=session.cookies.get_dict())
            resp.raise_for_status()
            # if server returns a JSON with empty/blocked content, still returning the response for caller to decide
            return resp
        except requests.exceptions.RequestException:
            # possible reason: cookie expired / server blocking
            # refreshing cookie once if received 403/401 or other request exceptions on first attempt
            if attempt == 0:
                # refresh cookie and retry
                _refresh_cookie(session)
            # exponential backoff
            time.sleep(1.5 ** attempt)
            continue
    # final attempt failed
    return None



def _http_post(url: str, payload: dict = None, headers: dict = None, max_retries: int = 2, timeout: int = 15):
    """
    Lightweight POST wrapper with session, cookie refresh, retries.
    Returns the requests.Response object or None.
    """
    session = requests.Session()
    # ensuring cookie have loaded or refreshed
    _refresh_cookie(session)

    if headers is None:
        headers = default_headers

    for attempt in range(max_retries):
        try:
            resp = session.post(url, headers=headers, json=payload, timeout=timeout, cookies=session.cookies.get_dict())
            resp.raise_for_status()
            # if server returns a JSON with empty/blocked content, still returning the response for caller to decide
            return resp
        except requests.exceptions.RequestException as e:
            # possible reason: cookie expired / server blocking
            if attempt == 0:
                # refresh cookie and retry
                _refresh_cookie(session)
            # exponential backoff
            time.sleep(1.5 ** attempt)
            continue
    # final attempt failed
    return None


# -----------------------
# Response processing helpers
# -----------------------
def remove_pre_and_post_market_prices_from_df(df: pd.DataFrame, unit: str = 'ms', interval: int = 3) -> pd.DataFrame:
    try:
        if not isinstance(df, pd.DataFrame):
            return df
        df['temp_datetime'] = df['datetime']
        if not pd.api.types.is_datetime64_dtype(df['datetime']):
            df['temp_datetime'] = pd.to_datetime(df['datetime'], unit=unit)

        df['time'] = df['temp_datetime'].dt.time
        start_time_obj = pd.to_datetime("09:15:00").time()
        end_time_obj = pd.to_datetime("15:30:00").time()
        print(df)
        # exit(9)
        filtered_df = df[(df['time'] >= start_time_obj) & (df['time'] < end_time_obj)]
        return filtered_df.drop(columns=['time', 'temp_datetime'], axis=0)
    except Exception as e:
        print(f"Error occurred while removing pre and post market prices: {e}")
        raise e


def process_historical_chart_response(df: pd.DataFrame, interval: str, start_datetime: datetime, end_datetime: datetime) -> pd.DataFrame:
    try:
        df = df[['time', 'open', 'high', 'low', 'close', 'volume']].copy()
        
        df.rename(columns={'time': 'datetime'}, inplace=True)
        
        if interval in ('D', 'W', 'M'):
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            return df

        df = remove_pre_and_post_market_prices_from_df(df=df.copy())
        try:
            minutes = int(interval) if str(interval) == '1' else 5
            time_offset_seconds = (minutes - 1) * 60 + 59
        except Exception:
            time_offset_seconds = 0

        df['datetime'] = df['datetime'] - time_offset_seconds * 1000
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df['datetime'] = df['datetime'].apply(
            lambda dt: dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
            if dt.second > 1 else dt.replace(second=0, microsecond=0)
        )
        return df
    except Exception as e:
        print('Exception in process_historical_chart_response', e)
        traceback.print_exc()
        return None

# -----------------------
# Private functions
# -----------------------

def __fetch_historical_data(symbol: str, 
                           token: str,
                           start_datetime: datetime, 
                           end_datetime: datetime, 
                           interval: int | str = '3',
                           symbol_type: str = 'Index',
                           raw: bool = False,
                           ):
    try:
        IST_OFFSET_SECONDS = 5 * 3600 + 30 * 60  # 19800
        chart_type = 'I'
        time_interval = 1
        
        if interval in ('D', 'W', 'M'):
            start_datetime = int(start_datetime.timestamp()) 
            end_datetime = int(end_datetime.timestamp())
            chart_type = interval
        else:
            start_datetime = int(start_datetime.timestamp()) + IST_OFFSET_SECONDS
            end_datetime = int(end_datetime.timestamp()) + IST_OFFSET_SECONDS
            time_interval =  int(interval)

        # preparing the payload
        payload = {
            'chartType': chart_type, 
            'fromDate': start_datetime, 
            'symbol': symbol, 
            'symbolType': symbol_type,
            'timeInterval': time_interval,
            'toDate': end_datetime,
            'token': token
        }

        resp = _http_get(url=nse_chart_url, payload=payload, headers=default_headers)
        if resp is None:
            resp = _http_post(url=nse_chart_url, payload=payload, headers=default_headers)
            # return None

        try:
            raw_data = resp.json()
        except Exception:
            return None

        if raw:
            return raw_data

        if not isinstance(raw_data, dict) or not raw_data.get('data'):
            print(f'No Data Returned for the given symbol: {symbol}')
            return None

        try:
            del raw_data['status']
        except KeyError:
            pass

        df = pd.DataFrame(raw_data['data'])
        df = process_historical_chart_response(df=df, interval=interval, start_datetime=start_datetime, end_datetime=end_datetime)
        return df.drop_duplicates(subset=['datetime']).reset_index(drop=True)

    except Exception as e:
        print(f'ERROR in get_index_historical_data: {e}')
        traceback.print_exc()
        return None



# -----------------------
# Public functions
# -----------------------

def get_script_token(symbol: str, segment: str | None = None, scrip_type: str | None = None, get_all: bool = False
                     ) -> tuple | pd.DataFrame |  None:
    """
    Fetches the security token and instrument type for a given symbol from the NSE.

    The function queries the search endpoint and filters the results based on a 
    priority matching logic:
    1. Exact symbol match.
    2. Symbols starting with the query.
    3. Descriptions containing the query.

    Args:
        symbol (str): The trading symbol or part of the description to search for 
            (e.g., 'NIFTY', 'RELIANCE', 'SBIN'). Case-insensitive.
        segment (str, optional): The market segment. Must be one of {'EQ', 'FO', 'IDX'}.
            Defaults to an empty search if not provided or invalid.
        scrip_type (str, optional): Filter results by instrument category. 
            Options: {'Equity', 'Index', 'Futures', 'Options'}.
        get_all (bool, False): If you need full search results then pass this value as True. Defaults to False.

    Returns:
        data (tuple | DataFrame | None): The return data-type is based on the passed arguments.
        - tuple: A tuple containing (symbol, token, type) if a match is found.
            Example: ('NIFTY 50', '26000', 'Index')
        - dataframe: Returns dataframe of the search results if asked for get_all flag.
        - None: Returns None if an error occurs during the lookup.
    """
    try:
        symbol = symbol.upper()
        segment_set = {'EQ', 'FO', 'IDX'}
        params = {
            'segment': segment if segment in segment_set else '',
            'symbol': symbol
        }

        resp = _http_get(url=search_token_url, payload=params)
        if resp is None:
            resp = _http_post(url=search_token_url, payload=params)
            
        data = resp.json()
        df = pd.DataFrame(data['data'])
        if get_all:
            return df
        
        if scrip_type:
            if scrip_type in {'Equity', 'Index', 'Futures', 'Options'}:
                df = df[df['type'] == scrip_type]
                
        df['symbol'] = df['symbol'].str.split('-').str[0]
        x = df[df['symbol'] == symbol]
        if not len(x):
            x = df[df['symbol'].str.startswith(symbol)]
        if not len(x):
            x = df[df['description'].str.contains(symbol)]
        
        symbol = x.iloc[0]['symbol']   
        token = x.iloc[0]['scripcode']
        type = x.iloc[0]['type']
        return symbol, token, type
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f'Error: Could not find the token for the given symbol. {e}')
        return None



def get_historical_data(symbol: str,
                        start_datetime: datetime,
                        end_datetime: datetime = datetime.now(),
                        interval: int | str = '3',
                        symbol_type: str | None = None,
                        raw: bool = False) -> pd.DataFrame | dict | None:
    """
    Fetches historical OHLC data for any NSE instrument (Index, Equity, F&O).

    This function acts as a universal interface, automatically resolving the 
    internal exchange token and instrument type. It supports a wide variety of 
    naming conventions, ranging from exact NSE symbols to human-readable 
    contract descriptions.

    Args:
        symbol (str): The identifier for the security or contract. 
            Supported formats include:
            
            - **Equity Stocks:** Standard tickers (e.g., 'TCS', 'JIOFIN', 'RELIANCE').
            - **Indices:** Standard index names (e.g., 'NIFTY 50', 'NIFTY BANK', 'NIFTY IT').
            - **Stock Futures:** Monthly codes (e.g., 'INFY26FEBFUT', 'HDFCBANK26JANFUT').
            - **Index Futures:** Monthly codes (e.g., 'NIFTY26JANFUT', 'BANKNIFTY26MARFUT').
            - **Options (Long-form):** Full descriptive strings:
                * Index Weekly: 'NIFTY 03 FEB 2026 CE 19800.00'
                * Index Monthly: 'NIFTY 24 FEB 2026 CE 19800.00'
                * Stock: 'JIOFIN 24 FEB 2026 CE 120.00' or 'INFY 24 FEB 2026 PE 1040.00'
            - **Options (Short-form):** Compact exchange symbols:
                * Index Weekly: 'NIFTY2620319800CE'
                * Index Monthly: 'NIFTY26FEB19800CE'
                * Stock: 'JIOFIN26FEB120CE' or 'INFY26FEB1040PE'

        start_datetime (datetime): The starting point for historical data.
        end_datetime (datetime, optional): The ending point for historical data. 
            Defaults to the current time.
        interval (int | str, optional): The timeframe for each candle. 
            - Minutes (int): 1, 3, 5, 15, 30, 60
            - Timeframe (str): 'D' (Daily), 'W' (Weekly), 'M' (Monthly)
            Defaults to '3'.
        symbol_type (str, optional): Explicitly define instrument type ('Equity', 'Index', 
            'Futures', 'Options') to filter lookup results.
        raw (bool, optional): If True, returns the raw JSON dictionary. 
            If False, returns a processed pandas DataFrame. Defaults to False.

    Returns:
        df (pd.DataFrame | dict | None): A processed DataFrame with OHLCV data or 
            the raw API response. Returns None if lookup fails.

    Note:
        For Options, the function intelligently differentiates between Weekly 
        and Monthly expiries based on the date provided in the symbol string or 
        the specific exchange symbol format (e.g., NIFTY262... vs NIFTY26FEB...).
    """
    search_result = get_script_token(symbol=symbol)
    if not search_result:
        raise ValueError("ERROR: Couldn't find the Symbol")
    
    # unpacking the tuple
    symbol, token, symbol_type = search_result
    
    return __fetch_historical_data(symbol=symbol,
                                  token=token,
                                  start_datetime=start_datetime,
                                  end_datetime=end_datetime,
                                  interval=interval,
                                  symbol_type=symbol_type,
                                  raw=raw)
