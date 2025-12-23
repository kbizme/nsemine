# nsemine_light.py
import os
import json
import time
import traceback
from datetime import datetime, timedelta
from typing import Union
import requests
import pandas as pd

# -----------------------
# Configuration / URLs
# -----------------------
nse_chart_symbol = 'https://charting.nseindia.com//Charts/symbolhistoricaldata/'
nse_chart = 'https://charting.nseindia.com//Charts/ChartData/'
first_boy = 'https://www.nseindia.com/get-quotes/equity?symbol=RELIANCE' # landing page to acquire cookies

# default minimal headers (stable and simple)
default_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br, zstd",
}

# cookie filename stored in same folder as this module / notebook
COOKIE_FILE = "nse_cookie.json"
# cookie expiry window (you asked for 2 hours)
COOKIE_TTL = timedelta(hours=2)

# -----------------------
# Index tokens (copied from your mapping)
# -----------------------
index_tokens = {
    'NIFTY 50': 26000,
    'NIFTY BANK': 26009,
    'NIFTY NEXT 50': 26013,
    'NIFTY FIN SERVICE': 26037,
    'NIFTY FINANCIAL SERVICES': 26037,
    'NIFTY MIDCAP 100': 26010,    
    'NIFTY MID SELECT': 26074,
    'NIFTY MIDCAP SELECT': 26074,
    'NIFTY TOTAL MKT': 26021,
    'NIFTY TOTAL MARKET': 26021,
    'NIFTY IT': 26008,
    'NIFTY 500': 26003,
    'NIFTY 100': 26012,
    'INDIA VIX': 26017,
    'NIFTY MIDCAP 50': 26014,
    'NIFTY REALTY': 26052,
    'NIFTY INFRA': 26019,
    'NIFTY ENERGY': 26054,
    'NIFTY FMCG': 26055,
    'NIFTY MNC': 26056,
    'NIFTY PHARMA': 26057,
    'NIFTY PSE': 26024,
    'NIFTY PSU BANK': 26059,
    'NIFTY SERV SECTOR': 26060,
    'NIFTY SMLCAP 100': 26011,
    'NIFTY SMALLCAP 100': 26011,
    'NIFTY 200': 26065,
    'NIFTY AUTO': 26061,
    'NIFTY MEDIA': 26063,
    'NIFTY METAL': 26062,
    'NIFTY DIV OPPS 50': 26078,
    'NIFTY COMMODITIES': 26066,
    'NIFTY CONSUMPTION': 26048,
    'NIFTY50 DIV POINT': 26080,
    'NIFTY100 LIQ 15': 26051,
    'NIFTY CPSE': 26041,
    'NIFTY GROWSECT 15': 26082,
    'NIFTY50 TR 2X LEV': 26075,
    'NIFTY50 PR 2X LEV': 26064,
    'NIFTY50 TR 1X INV': 26076,
    'NIFTY50 PR 1X INV': 26020,
    'NIFTY50 VALUE 20': 26081,
    'NIFTY100 QUALTY30': 26026,
    'NIFTY MID LIQ 15': 26018,
    'NIFTY PVT BANK': 26025,
    'NIFTY PRIVATE BANK': 26025,
    'NIFTY GS 8 13YR': 26053,
    'NIFTY GS 10YR': 26058,
    'NIFTY GS 10YR CLN': 26029,
    'NIFTY GS 4 8YR': 26030,
    'NIFTY GS 11 15YR': 26069,
    'NIFTY GS 15YRPLUS': 26070,
    'NIFTY GS COMPSITE': 26071,
    'NIFTY50 EQL WGT': 26083,
    'NIFTY100 EQL WGT': 26084,
    'NIFTY100 LOWVOL30': 26085,
    'NIFTY ALPHA 50': 26086,
    'NIFTY MIDCAP 150': 26087,
    'NIFTY SMLCAP 50': 26088,
    'NIFTY SMALLCAP 50': 26088,
    'NIFTY SMLCAP 250': 26089,
    'NIFTY SMALLCAP 250': 26089,
    'NIFTY MIDSML 400': 26091,
    'NIFTY200 QUALTY30': 26092,
    'NIFTY FINSRV25 50': 26093,
    'NIFTY ALPHALOWVOL': 26094,
    'NIFTY200MOMENTM30': 26067,
    'NIFTY100ESGSECLDR': 26068,
    'NIFTY HEALTHCARE': 26096,
    'NIFTY HEALTHCARE INDEX': 26096,
    'NIFTY CONSR DURBL': 26095,
    'NIFTY CONSUMER DURABLES': 26095,
    'NIFTY OIL AND GAS': 26099,
    'NIFTY OIL & GAS' : 26099,
    'NIFTY500 MULTICAP': 26098,
    'NIFTY LARGEMID250': 26097,
    'NIFTY MICROCAP250': 26022,
    'NIFTY MICROCAP 250': 26022,
    'NIFTY IND DIGITAL': 26023,
    'NIFTY100 ESG': 26027,
    'NIFTY M150 QLTY50': 26028,
    'NIFTY INDIA MFG': 26031,
    'NIFTY200 ALPHA 30': 26043,
    'NIFTYM150MOMNTM50': 26042,
    'NIFTY TATA 25 CAP': 26047,
    'NIFTY MIDSML HLTH': 26044,
    'NIFTY MIDSMALL HEALTHCARE' : 26044,
    'NIFTY MULTI MFG': 26045,
    'NIFTY MULTI INFRA': 26046,
    'NIFTY IND DEFENCE': 26038,
    'NIFTY IND TOURISM': 26039,
    'NIFTY CAPITAL MKT': 26040,
    'NIFTY500MOMENTM50': 26049,
    'NIFTYMS400 MQ 100': 26050,
    'NIFTYSML250MQ 100': 26079,
    'NIFTY TOP 10 EW': 26077,
    'NIFTY AQL 30': 26100,
    'NIFTY AQLV 30': 26101,
    'NIFTY EV': 26102,
    'NIFTY HIGHBETA 50': 26103,
    'NIFTY NEW CONSUMP': 26104,
    'NIFTY CORP MAATR': 26105,
    'NIFTY LOW VOL 50': 26106,
    'NIFTY MOBILITY': 26107,
    'NIFTY QLTY LV 30': 26108,
    'NIFTY SML250 Q50': 26109,
    'NIFTY TOP 15 EW': 26110,
    'NIFTY100 ALPHA 30': 26111,
    'NIFTY100 ENH ESG': 26112,
    'NIFTY200 VALUE 30': 26113,
    'NIFTY500 EW': 26114,
    'NIFTY MULTI MQ 50': 26115,
    'NIFTY500 VALUE 50': 26116,
    'NIFTY TOP 20 EW': 26117,
    'NIFTY COREHOUSING': 26118,
    'NIFTY FINSEREXBNK': 26119,
    'NIFTY HOUSING': 26120,
    'NIFTY IPO': 26121,
    'NIFTY MS FIN SERV': 26122,
    'NIFTY MIDSMALL FINANCIAL SERVICES': 26122,
    'NIFTY MS IND CONS': 26123,
    'NIFTY MS IT TELCM': 26124,
    'NIFTY MIDSMALL IT & TELECOM' : 26124,
    'NIFTY NONCYC CONS': 26125,
    'NIFTY RURAL': 26126,
    'NIFTY SHARIAH 25': 26127,
    'NIFTY TRANS LOGIS': 26128,
    'NIFTY50 SHARIAH': 26129,
    'NIFTY500 LMS EQL': 26130,
    'NIFTY500 SHARIAH': 26131,
    'NIFTY500 QLTY50': 26132,
    'NIFTY500 LOWVOL50': 26133,
    'NIFTY500 MQVLV50': 26134,
}

# If you want the entire mapping included, paste the full dict here (I included the beginning).
# (In this file I'll include the full mapping as you provided earlier.)
# For runtime, we'll assume index_tokens contains the tokens you previously gave.

# -----------------------
# Cookie manager (file-based)
# -----------------------
def _cookie_file_path():
    # Use current working directory so it's alongside the notebook
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
        # don't crash on save problems
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
    # 1) Try to load existing cookie
    cookie = load_cookie()
    if cookie:
        session.cookies.update(cookie)
        return cookie

    # 2) Fetch fresh cookie from first_boy
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



def _http_get(url: str, params: dict = None, headers: dict = None, max_retries: int = 3, timeout: int = 15):
    """
    Lightweight GET wrapper with session, cookie refresh, retries.
    Returns the requests.Response object or None.
    """
    session = requests.Session()
    # ensure we have cookie loaded or refreshed
    _refresh_cookie(session)

    if headers is None:
        headers = default_headers

    for attempt in range(max_retries):
        try:
            resp = session.get(url, headers=headers, params=params, timeout=timeout, cookies=session.cookies.get_dict())
            resp.raise_for_status()
            # if server returns a JSON with empty/blocked content, we still return the response for caller to decide
            return resp
        except requests.exceptions.RequestException as e:
            # possible reason: cookie expired / server blocking
            # Try to refresh cookie once if we get 403/401 or other request exceptions on first attempt
            if attempt == 0:
                # refresh cookie and retry
                _refresh_cookie(session)
            # exponential backoff-ish
            time.sleep(1.5 ** attempt)
            continue
    # final attempt failed
    return None

# -----------------------
# Response processing helpers (same logic you provided)
# -----------------------
def remove_pre_and_post_market_prices_from_df(df: pd.DataFrame, unit: str = 's', interval: int = 3) -> pd.DataFrame:
    try:
        if not isinstance(df, pd.DataFrame):
            return df
        if not pd.api.types.is_datetime64_dtype(df['datetime']):
            df['temp_datetime'] = pd.to_datetime(df['datetime'], unit=unit)
        else:
            df['temp_datetime'] = df['datetime']

        df['time'] = df['temp_datetime'].dt.time
        start_time_obj = pd.to_datetime("09:15:00").time()
        end_time_obj = pd.to_datetime("15:30:03").time()
        filtered_df = df[(df['time'] >= start_time_obj) & (df['time'] < end_time_obj)]
        return filtered_df.drop(columns=['time', 'temp_datetime'], axis=1)
    except Exception as e:
        print(f"Error occurred while removing pre and post market prices: {e}")
        return df

def process_historical_chart_response(df: pd.DataFrame, interval: str, start_datetime: datetime, end_datetime: datetime) -> pd.DataFrame:
    try:
        df = df.copy()
        df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        if interval in ('D', 'W', 'M'):
            df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
            return df

        df = remove_pre_and_post_market_prices_from_df(df=df.copy())

        # The original code used (minutes-1, seconds=59) time_offset technique.
        # Use consistent offset: convert interval to minutes and subtract ~(interval-1)*60 + 59 seconds
        try:
            minutes = int(interval)
            time_offset_seconds = (minutes - 1) * 60 + 59
        except Exception:
            time_offset_seconds = 0

        df['datetime'] = df['datetime'] - time_offset_seconds
        df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
        df['datetime'] = df['datetime'].apply(
            lambda dt: dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
            if dt.second > 1 else dt.replace(second=0, microsecond=0)
        )
        df = df[(df['datetime'] >= start_datetime) & (df['datetime'] <= end_datetime)]
        return df.reset_index(drop=True)
    except Exception as e:
        print('Exception in process_historical_chart_response', e)
        traceback.print_exc()
        return df

# -----------------------
# Public functions
# -----------------------
def get_stock_historical_data(stock_symbol: str,
                              start_datetime: datetime,
                              end_datetime: datetime = datetime.now(),
                              interval: Union[int, str] = 1,
                              raw: bool = False) -> Union[pd.DataFrame, dict, None]:
    """
    Fetches historical stock data for a given symbol within a specified datetime range for the given interval.
    interval: int (minutes) or 'D','W','M'
    """
    try:
        # NSE endpoints often expect epoch seconds adjusted for IST offset (19800 seconds)
        IST_OFFSET_SECONDS = 5 * 3600 + 30 * 60  # 19800

        params = {
            "exch": "N",
            "tradingSymbol": f"{stock_symbol}-EQ",
            "fromDate": int(start_datetime.timestamp()),
            "toDate": int(end_datetime.timestamp()) + IST_OFFSET_SECONDS,
            "chartStart": 0
        }

        if interval in ('D', 'W', 'M'):
            params.update({
                'timeInterval': 1,
                'chartPeriod': str(interval),
                'fromDate': int(start_datetime.timestamp()) - IST_OFFSET_SECONDS
            })
        else:
            params.update({'timeInterval': int(interval), 'chartPeriod': 'I'})

        resp = _http_get(nse_chart, params=params, headers=default_headers)
        if resp is None:
            # network or server failure
            return None

        raw_data = None
        try:
            raw_data = resp.json()
        except Exception:
            # if JSON decode fails, return None
            return None

        if raw:
            return raw_data

        # expected structure: {"s":"Ok", ...}
        if not isinstance(raw_data, dict) or raw_data.get('s') != 'Ok':
            return None

        # remove the status key and convert to DataFrame
        try:
            del raw_data['s']
        except KeyError:
            pass

        df = pd.DataFrame(raw_data)
        df = process_historical_chart_response(df=df, interval=interval, start_datetime=start_datetime, end_datetime=end_datetime)
        return df

    except Exception as e:
        print(f'ERROR in get_stock_historical_data: {e}')
        traceback.print_exc()
        return None


def get_index_historical_data(index: str,
                              start_datetime: datetime,
                              end_datetime: datetime = datetime.now(),
                              interval: Union[str] = 'ONE_DAY',
                              raw: bool = False) -> Union[pd.DataFrame, dict, None]:
    """
    Fetches historical data for a given index.
    interval: int (minutes) or 'D','W','M'
    """
    try:
        IST_OFFSET_SECONDS = 5 * 3600 + 30 * 60  # 19800

        token = index_tokens.get(index.upper())
        if not token:
            raise Exception("Couldn't find the index. Please check the index name.")

        params = {
            "exch": "N",
            "instrType": "C",
            "scripCode": token,
            "ulToken": token,
            "fromDate": int(start_datetime.timestamp()),
            "toDate": int(end_datetime.timestamp()) + IST_OFFSET_SECONDS,
            "chartStart": 0
        }

        if interval in ('D', 'W', 'M'):
            params.update({'timeInterval': 1, 'chartPeriod': interval, 'fromDate': int(start_datetime.timestamp()) - IST_OFFSET_SECONDS})
        else:
            # align with original style: 'I' for intraday with minutes
            try:
                params.update({'timeInterval': int(interval), 'chartPeriod': 'I'})
            except Exception:
                params.update({'timeInterval': 1, 'chartPeriod': 'I'})

        resp = _http_get(nse_chart_symbol, params=params, headers=default_headers)
        if resp is None:
            return None

        try:
            raw_data = resp.json()
        except Exception:
            return None

        if raw:
            return raw_data

        if not isinstance(raw_data, dict) or raw_data.get('s') != 'Ok':
            return None

        try:
            del raw_data['s']
        except KeyError:
            pass

        df = pd.DataFrame(raw_data)
        df = process_historical_chart_response(df=df, interval=interval, start_datetime=start_datetime, end_datetime=end_datetime)
        # index endpoint may include volume — drop for index
        if 'volume' in df.columns:
            df.drop(columns=['volume'], inplace=True)
        return df

    except Exception as e:
        print(f'ERROR in get_index_historical_data: {e}')
        traceback.print_exc()
        return None
