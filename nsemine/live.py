from nsemine.bin import autils, scraper
from nsemine.utilities import urls, utils
from datetime import datetime
import pandas as pd
import asyncio
import traceback
from curl_cffi import requests



def get_stock_live_quotes(stock_symbol: str, series: str | None = None, raw: bool = False) -> dict | None:
    """
    Fetches the live quote of the given stock symbol.
    Args:
        stock_symbol (str): The stock symbol (e.g., "TCS" etc)
        series (str | None): Series of the given stock symbol. Defaults to 'EQ'.
        raw (bool): Pass True, if you need the raw data without processing. Deafult is False.
        
    Returns:
        quote_data (dict, None) : Returns the raw data as dictionary if raw=True. By default, it returns cleaned and processed dictionary.
        Returns None if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.nse_equity_quote.format(series or 'EQ',stock_symbol.replace('&', '%26')))
        if resp:
            data = resp.json()
            if raw:
                return data
            return utils.process_stock_quote_data(quote_data=data)
        
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()



def get_multiple_stock_live_quotes(
    symbols: list | set | tuple, 
    series: str = 'EQ', 
    raw: bool = False, 
    df: bool = True,
    max_concurrent: int = 25
) -> pd.DataFrame | dict:
    """
    Synchronous entry point for fetching multiple stock quotes concurrently with controlled throttling.
    
    Args:
        symbols (list | set | tuple): Stock symbols (e.g. ['TCS', 'HDFCBANK', 'INFY'])
        series (str): Equity series, default 'EQ'
        raw (bool): If True, returns dict of raw API JSON responses
        df (bool): If True, returns Pandas DataFrame; if False, returns dict of dicts
        max_concurrent (int): Maximum simultaneous requests to NSE (default: 25)
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(
            autils.async_get_multiple_stock_quotes(symbols, series, raw, df, max_concurrent)
        )
    else:
        return asyncio.run(
            autils.async_get_multiple_stock_quotes(symbols, series, raw, df, max_concurrent)
        )



def get_index_live_price(index: str = 'NIFTY 50', raw: bool = False):
    """
    Retrieves live price data for a specified stock market index from the NSE (National Stock Exchange of India).

    Args:
        index (str, optional): The name of the index to fetch data for. Defaults to 'NIFTY 50'.
        raw (bool, optional): If True, returns the raw JSON response from the API. If False, returns a processed dictionary. Defaults to False.

    Returns:
        dict: A dictionary containing the processed index data, including open, high, low, close, previous close, change, change percentage, year high, year low, and optionally datetime.
        If raw is True, returns the raw JSON response as a dictionary.
        Returns None if an error occurs.

    Example:
        >>> get_index_live_price()
        >>> get_index_live_price(index_name='NIFTY BANK', raw=True)
    """
    try:
        index = index.upper().strip()
        resp = scraper.get_request(url=urls.all_indices, referer=urls.all_indices_ref)
        raw_data = resp.json()
        if raw:
            return raw_data
        # otherwise,
        fetched_data = raw_data['data']
        data = None
        # searching
        for item in fetched_data:
            if item.get('indexSymbol') == index or item.get('index') == index:
                data = item
                break
        
        if not data:
            return
        
        index_data = {
            'symbol': index,
            'open': data.get('open'),
            'high': data.get('high'),
            'low': data.get('low'),
            'close': data.get('last'),
            'previous_close': data.get('previousClose'),
            'change': data.get('variation'),
            'changepct': data.get('percentChange'),
            'year_high': data.get('yearHigh'),
            'year_low': data.get('yearLow'),
        }
        try:
            index_data['datetime'] = datetime.strptime(raw_data.get('timestamp'), '%d-%b-%Y %H:%M')
        except:
            pass
        return index_data
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()

        




def get_all_indices_live_snapshot(raw: bool = False) -> dict | pd.DataFrame | None:
    """This Functions Returns the Live Snapshot of all the available NSE Indices.

    Args:
        raw (bool, optional): Pass True if you want the raw data without processing. Defaults to False.

    Returns:
        data (DataFrame | dict | None): Returns the pandas DataFrame containing these columns
        ['key', 'index', 'symbol', 'open', 'high', 'low', 'close','previous_close', 'change', 'changepct', 'year_high', 
        'year_low','advances', 'declines', 'unchanged', 'one_week_ago', 'one_month_ago', 'one_year_ago']
        
        None: If any errors occurred.
    Note:
        This function drops the nan values. So, you may get less number of the results than expected. 
        Use raw=True if you don't want this behavior. 
    """
    try:
        resp = scraper.get_request(url=urls.all_indices, referer=urls.all_indices_ref)
        if not resp:
            return None
        

        raw_data = resp.json()
        if raw:
            return raw_data
        
        # otherwise
        data = raw_data.get('data')
        
        df = pd.DataFrame(data)
        df = df.dropna()
        df = df[['key', 'index', 'indexSymbol', 'open', 'high', 'low', 'last', 'previousClose', 'variation', 'percentChange', 'yearHigh', 'yearLow','advances', 'declines', 'unchanged', 'oneYearAgoVal', 'oneMonthAgoVal', 'oneYearAgoVal']]
        df.columns = ['key', 'index', 'symbol', 'open', 'high', 'low', 'close', 'previous_close', 'change', 'changepct', 'year_high', 'year_low','advances', 'declines', 'unchanged', 'one_week_ago', 'one_month_ago', 'one_year_ago']
        df[['advances', 'declines', 'unchanged']] = df[['advances', 'declines', 'unchanged']].astype('int')
        return df
    except Exception as e:
        print('ERROR! - ', e)
        traceback.print_exc()
        return None



def get_all_securities_live_snapshot(series: str |list = None, raw: bool = False) -> pd.DataFrame | dict | None:
    """Fetches the live snapshot all the available securities in the NSE Exchange.
    This snapshot includes the last price (close), previous_close price, change, change percentage, volume etc.
    Args:
        series (str, list): Filter the securities by series name.
                        Series name can be EQ, SM, ST, BE, GB, GS, etc...(refer to nse website for all available series names.)
                        Refer to this link: https://www.nseindia.com/market-data/legend-of-series
        raw (bool): Pass True, if you need the raw data without processing.
    Returns:
        data (DataFrame or dict or None) : Returns Pandas DataFrame object if succeed. Returns dictionary if raw=True, 
        and returns None if any error occurred.
    Example:
        To get the processed DataFrame for all securities:
        >>> df = get_all_nse_securities_live_snapshot()

        To get the raw DataFrame for all securities:
        >>> raw_df = get_all_nse_securities_live_snapshot(raw=True)

        To get the processed DataFrame for 'EQ' series securities:
        >>> eq_df = get_all_nse_securities_live_snapshot(series='EQ')

        To get the processed DataFrame for 'EQ' and 'SM' series securities:
        >>> eq_sm_df = get_all_nse_securities_live_snapshot(series=['EQ', 'SM'])
    """
    try:
        resp = scraper.get_request(url=urls.nse_all_stocks_live)
        if resp.status_code == 200:
            data = resp.json()
            if raw:
                return data
            # processing
            base_df = pd.DataFrame(data['total']['data'])
            df = base_df[['symbol', 'series', 'lastPrice', 'previousClose', 'change', 'pchange', 'totalTradedVolume', 'totalTradedValue', 'totalMarketCap']].copy()
            df.columns = ['symbol', 'series', 'close', 'previous_close', 'change', 'changepct', 'volume', 'traded_value', 'market_cap']
            df['volume'] = df['volume'] * 1_00000
            df['volume'] = df['volume'].astype('int')
            df[['traded_value', 'market_cap']] = df[['traded_value', 'market_cap']] * 100_00000
            if not series:
                return df
            if not isinstance(series, list):
                series = [series,]        
            return df[df['series'].isin(series)].reset_index(drop=True)
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()




def get_index_constituents_live_snapshot(
        index: str = "NIFTY 50",
        raw: bool = False,
        stats: bool = False,
        allow_fallback: bool = False,
    ) -> pd.DataFrame | tuple[pd.DataFrame, dict] | dict | None:
    """
    Retrieves live snapshot data of constituents for a specified stock market index from the NSE.
    
    This function attempts to fetch real-time data from the primary (v1) endpoint. If the primary
    endpoint fails or returns empty data, it can optionally fall back to a secondary (v2) endpoint
    if `allow_fallback=True`.

    Note on Schema Differences:
        - Primary Endpoint (v1): Full schema (16 columns including OHLC, 52-week highs/lows, 
            historical change %s) and supports `stats=True` (advance/decline).
        - Fallback Endpoint (v2): Reduced schema (8 columns: `symbol`, `ltp`, `previous_close`,
            `change`, `changepct`, `weightage`, `volume`, `turnover`). It **does not** contain
            advance/decline stats (`stats` will return an empty dict `{}`).

    Args:
        index (str, optional): The name of the index to retrieve (e.g., 'NIFTY 50', 'NIFTY BANK'). Defaults to 'NIFTY 50'.
        raw (bool, optional): If True, returns the raw unparsed JSON payload from the API. Defaults to False.
        stats (bool, optional): If True, returns a tuple where the first element is the DataFrame
            and the second element is a dictionary containing advance/decline stats. Defaults to False.
        allow_fallback (bool, optional): If True, attempts to fetch data from the v2 endpoint if
            v1 fails or returns empty results. Note that v2 provides a reduced schema (8 columns)
            and does not support index stats. Defaults to False.

    Returns:
        pd.DataFrame | tuple[pd.DataFrame, dict] | dict | None: 
            - If `raw=True`: Raw API JSON response dictionary.
            - If `raw=False` and `stats=False`: Processed constituents DataFrame.
            - If `raw=False` and `stats=True`: Tuple of (DataFrame, stats_dict).
            - Returns `None` if requests fail and no valid payload could be retrieved.

    Example:
        >>> # Standard strict v1 query (returns full 16-column schema or raises/fails)
        >>> df = get_index_constituents_live_snapshot(index='NIFTY BANK')

        >>> # Query with fallback enabled (accepts 8-column schema if v1 endpoint fails)
        >>> df = get_index_constituents_live_snapshot(index='NIFTY BANK', allow_fallback=True)
    """
    try:
        try:
            # Trying Primary Endpoint v1
            resp = scraper.get_request(url=urls.nse_equity_index_v1, params={"symbol": index})
            if resp.status_code != 200:
                raise RuntimeError(f"v1 endpoint HTTP status: {resp.status_code}")
    
            data = resp.json()
            if not data.get("data"):
                raise ValueError("v1 endpoint returned empty payload or missing 'data' key.")
    
            if raw:
                return data
            # data = {'data': [{'h': 'a'}]}
            return utils.process_index_constituents_data(data=data, stats=stats)
            
        except Exception as e:
            if not allow_fallback:
                traceback.print_exc()
                return None
            print(f'ERROR: v1 Endpoint failed with error: {e}. \nTrying v2 endpoint...')
           
           
        # Trying Fqallback Endpoint v2
        resp = scraper.get_request(url=urls.nse_equity_index_v2, params={"index": index})
        if resp.status_code != 200:
            raise RuntimeError(f"v2 endpoint HTTP status: {resp.status_code}")

        data = resp.json()
        if raw:
            return data

        # processing
        records = data.get("data", [])
        if not isinstance(records, list) or not records:
            raise ValueError("v2 endpoint returned empty records list.")

        df = pd.DataFrame(records)

        df.columns = ['change', 'cmSymbol', 'lasttradedPrice','pchange', 'totaltradedquantity', 'totaltradedvalue', 'weightage']
        df.columns = ['change', 'symbol', 'ltp', 'changepct', 'volume', 'turnover', 'weightage']
        df['previous_close'] = df['ltp'] - df['change']
        df =df[['symbol', 'ltp', 'previous_close', 'change', 'changepct', 'weightage', 'volume', 'turnover']].copy()
        df['volume'] = (df['volume'] * 100000).astype('int')
        df['turnover'] = df['turnover'] * 10000000

        if stats:
            return df, {}

        return df
                    
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()




def get_fno_indices_live_snapshot(df: bool = False) -> pd.DataFrame | dict | None:
    """
    Returns the live market snapshot of NSE F&O indices.

    The snapshot includes current OHLC data, price change, yearly range,
    market breadth, and weekly, monthly, and yearly performance.

    Args:
        df (bool): If True, returns a DataFrame. If False, returns a dictionary
            keyed by index names. Defaults to False.

    Returns:
        data (DataFrame | dict | None): Live F&O-index snapshot, or None if the source request fails or no supported indices are available.
    """
    try:
        resp = scraper.get_request(url=urls.all_indices, referer=urls.all_indices_ref)

        if not resp:
            return None

        payload = resp.json()
        timestamp = payload.get("timestamp")
        data = payload.get("data")

        timestamp = (
            datetime.strptime(timestamp, "%d-%b-%Y %H:%M")
            if timestamp else datetime.now()
        )

        if not data:
            return None

        fno_indices = {
            "NIFTY 50": "NIFTY",
            "NIFTY NEXT 50": "NIFTYNXT50",
            "NIFTY BANK": "BANKNIFTY",
            "NIFTY FIN SERVICE": "FINNIFTY",
            "NIFTY FINANCIAL SERVICES": "FINNIFTY",
            "NIFTY MID SELECT": "MIDCPNIFTY",
            "NIFTY MIDCAP SELECT": "MIDCPNIFTY",
        }

        if not df:
            fno_data = {}

            for item in data:
                quant_index = fno_indices.get(item.get("index"))

                if not quant_index:
                    continue

                close = item.get("last")
                previous_close = item.get("previousClose")
                one_week_ago_value = item.get("oneWeekAgoVal")

                fno_data[quant_index] = {
                    "datetime": timestamp,
                    "open": item.get("open"),
                    "high": item.get("high"),
                    "low": item.get("low"),
                    "close": close,
                    "previous_close": previous_close,
                    "change": (
                        round(close - previous_close, 2)
                        if close is not None and previous_close else None
                    ),
                    "changepct": item.get("percentChange"),
                    "year_high": item.get("yearHigh"),
                    "year_low": item.get("yearLow"),
                    "advances": int(item["advances"]) if item.get("advances") else None,
                    "declines": int(item["declines"]) if item.get("declines") else None,
                    "unchanged": int(item["unchanged"]) if item.get("unchanged") else None,
                    "changepct_weekly": (
                        round((close - one_week_ago_value) / one_week_ago_value * 100, 2)
                        if close and one_week_ago_value not in (None, 0) else None
                    ),
                    "changepct_monthly": item.get("perChange30d"),
                    "changepct_yearly": item.get("perChange365d"),
                }

                if len(fno_data) == 5:
                    break

            return fno_data or None

        df = pd.DataFrame(data)
        df = df[df["index"].isin(fno_indices)]

        if df.empty:
            return None

        df["change"] = (df["last"] - df["previousClose"]).round(2)
        df["changepct_weekly"] = (
            ((df["last"] - df["oneWeekAgoVal"]) / df["oneWeekAgoVal"]) * 100
        ).round(2)
        df["changepct_monthly"] = df["perChange30d"]
        df["changepct_yearly"] = df["perChange365d"]

        df = df[
            [
                "index",
                "open",
                "high",
                "low",
                "last",
                "previousClose",
                "change",
                "percentChange",
                "yearHigh",
                "yearLow",
                "advances",
                "declines",
                "unchanged",
                "changepct_weekly",
                "changepct_monthly",
                "changepct_yearly",
            ]
        ]

        df.insert(0, "datetime", timestamp)

        df.columns = [
            "datetime",
            "index",
            "open",
            "high",
            "low",
            "close",
            "previous_close",
            "change",
            "changepct",
            "year_high",
            "year_low",
            "advances",
            "declines",
            "unchanged",
            "changepct_weekly",
            "changepct_monthly",
            "changepct_yearly",
        ]

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"ERROR! - {e}\n")
        traceback.print_exc()
        return None
    


def get_stock_intraday_tick_by_tick_data(stock_symbol: str, candle_interval: int = None, raw: bool = False) -> pd.DataFrame:
    """
    Retrieves intraday tick-by-tick data for a given stock symbol and optionally converts it to OHLC candles.
    **Note:** 

    Args:
        stock_symbol (str): The stock symbol for which to retrieve data.
        candle_interval (int, optional): The interval (in minutes) for OHLC candle conversion. If None, raw tick data is returned. Defaults to None.
        raw (bool, optional): If True, returns the raw JSON response. If False, returns a pandas DataFrame. Defaults to False.

    Returns:
        data (pandas.DataFrame or dict or None): A pandas DataFrame containing tick data or OHLC candles, or the raw JSON response if raw=True.
        Returns None in case of errors.
        
    ## Notes:
        - This functions fetches the tick data of the current day only.
        - The candle interval can be any minutes. 1,2,3.7....69.......143...uptp 375. Whoa!! Are you kidding me? :))
    Example:
        - Get raw tick data
        >>> raw_data = get_intraday_tick_by_tick_data('INFY', raw=True)

        - Get tick data as a DataFrame
        >>> tick_data_df = get_intraday_tick_by_tick_data('INFY')

        - Get OHLC candles with 5-minute interval
        >>> ohlc_df = get_intraday_tick_by_tick_data('INFY', candle_interval=5)

        - Get OHLC candles with a non-standard 143-minute interval.
        >>> unusual_ohlc_df = get_intraday_tick_by_tick_data('INFY', candle_interval=143)
    """
    try:
        resp = scraper.get_request(url=urls.ticks_chart.format(stock_symbol.replace('&', '%26')), headers=urls.default_headers)
        data = resp.json()
        if not candle_interval:
            if raw:
                return data
        
        # otherwise
        df = pd.DataFrame(data['grapthData'])
        df.columns = ['datetime', 'price', 'type']
        if not candle_interval:
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms', errors='coerce')
            return df.reset_index(drop=True)
        
        if not isinstance(candle_interval, int):
            try:
                candle_interval = int(candle_interval)
            except ValueError:
                    print("Candle Interval(minutes) must be interger or String value.")
        return utils.convert_ticks_to_ohlc(data=df, interval=candle_interval, require_validation=True)
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None
    
