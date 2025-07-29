from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
from datetime import datetime
from time import time
import json
import pandas as pd
import traceback




def get_stock_live_quotes(stock_symbol: str, raw: bool = False) -> Union[dict, None]:
    """
    Fetches the live quote of the given stock symbol.
    Args:
        stock_symbol (str): The stock symbol (e.g., "TCS" etc)
        raw (bool): Pass True, if you need the raw data without processing. Deafult is False.
        
    Returns:
        quote_data (dict, None) : Returns the raw data as dictionary if raw=True. By default, it returns cleaned and processed dictionary.
        Returns None if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.nse_equity_quote.format(stock_symbol.replace('&', '%26')))
        if resp:
            data = resp.json()
            if raw:
                return data
            return utils.process_stock_quote_data(quote_data=data)
        
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()



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
        params = {
            'index': index,
        }
        resp = scraper.get_request(url=urls.nse_equity_index, params=params)
        raw_data = resp.json()
        if raw:
            return raw_data
        # otherwise,
        data = raw_data['data']
        data = data[0]
        index_data = {
            'symbol': data.get('symbol'),
            'open': data.get('open'),
            'high': data.get('dayHigh'),
            'low': data.get('dayLow'),
            'close': data.get('lastPrice'),
            'previous_close': data.get('previousClose'),
            'change': round(data.get('change'), 2),
            'changepct': data.get('pChange'),
            'year_high': data.get('yearHigh'),
            'year_low': data.get('yearLow')
        }
        try:
            index_data['datetime'] = datetime.strptime(data.get('lastUpdateTime'), '%d-%b-%Y %H:%M:%S')
        except:
            pass
        return index_data
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()

        




def get_all_indices_live_snapshot(raw: bool = False):
    """This Functions Returns the Live Snapshot of all the available NSE Indices.

    Args:
        raw (bool, optional): Pass True if you want the raw data without processing. Defaults to False.

    Returns:
        DataFrame: Returns the pandas DataFrame containing these columns
        ['key', 'index', 'symbol', 'open', 'high', 'low', 'close','previous_close', 'change', 'changepct', 'year_high', 
        'year_low','advances', 'declines', 'unchanged', 'one_week_ago', 'one_month_ago', 'one_year_ago']
        
        None: If any errors occurred.
    Note:
        This function drops the nan values. So, you may get less number of the results than expected. 
        Use raw=True if you don't want this behavior. 
    """
    try:
        resp = scraper.get_request(url=urls.al_indices)
        if not resp:
            return None
        
        # initializing an empty dataframe
        df = pd.DataFrame()
        raw_data = resp.json()
        if raw:
            return raw_data
        
        # otherwise
        data = raw_data.get('data')
        df = pd.DataFrame(data)
        df = df.dropna()
        df = df[['key', 'index', 'indexSymbol', 'open', 'high', 'low', 'last', 'previousClose', 'variation', 'percentChange', 'yearHigh', 'yearLow','advances', 'declines', 'unchanged', 'oneWeekAgo', 'oneMonthAgo', 'oneYearAgo']]
        df.columns = ['key', 'index', 'symbol', 'open', 'high', 'low', 'close', 'previous_close', 'change', 'changepct', 'year_high', 'year_low','advances', 'declines', 'unchanged', 'one_week_ago', 'one_month_ago', 'one_year_ago']
        df[['advances', 'declines', 'unchanged']] = df[['advances', 'declines', 'unchanged']].astype('int')
        return df
    except Exception as e:
        print('ERROR! - ', e)
        traceback.print_exc()
        return None



def get_all_securities_live_snapshot(series: Union[str,list] = None, raw: bool = False) -> Union[pd.DataFrame, dict, None]:
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




def get_index_constituents_live_snapshot(index: str = 'NIFTY 50', raw: bool = False, stats: bool = False):
    """
    Retrieves live snapshot data of constituents for a specified stock market index from the NSE (National Stock Exchange of India).

    This function fetches real-time data for the components of a given index, such as 'NIFTY 50', 'NIFTY BANK', 'NIFTY NEXT 50', etc,. 
    It may return either the raw JSON response or a processed Pandas DataFrame based on the input parameters.

    Args:
        index (str, optional): The name of the index for which to retrieve constituent data. Defaults to 'NIFTY 50'.
        raw (bool, optional): If True, returns the raw JSON response from the API. If False, returns a processed Pandas DataFrame. Defaults to False.
        stats (bool, optional): If True, returns the timestamp, count of total, advances, declines, and unchanged constituents along with the processed DataFrame. Defaults to False.

    Returns:
        data : Union[pandas.DataFrame or tuple[pandas.DataFrame, dict] or dict or None]: 
            - If raw is False, returns a Pandas DataFrame containing the constituent data with columns:
              'symbol', 'name', 'series', 'derivatives', 'open', 'high', 'low', 'close', 'previous_close', 
              'change', 'changepct', 'volume', 'year_high', 'year_low'.
            - If raw is True, returns the raw JSON response as a dictionary.
            - Returns None if an error occurs during data retrieval or processing.

    Example:
        To get the processed DataFrame for NIFTY BANK:
        >>> df = get_index_constituents_live_snapshot(index_name='NIFTY BANK')

        To get the raw JSON response for NIFTY 50:
        >>> json_data = get_index_constituents_live_snapshot(index_name='NIFTY BANK', raw=True)
    """
    try:
        params = {
            'index': index,
        }
        resp = scraper.get_request(url=urls.nse_equity_index, params=params)
        if raw:
            return resp.json()
        
        # otherwise,
        data = resp.json()
        index_stats = data['advance'], data['timestamp']
        data = data['data']
        del data[0]
        df = pd.DataFrame(data)
        df[['name', 'derivatives']] = [[item.get('companyName'), item.get('isFNOSec') ] for item in df['meta']]
        df = df[['symbol', 'name', 'series', 'derivatives', 'open', 'dayHigh', 'dayLow', 'lastPrice', 'previousClose', 'change', 'pChange', 'totalTradedVolume', 'yearHigh', 'yearLow']]
        df.columns = ['symbol', 'name', 'series', 'derivatives', 'open', 'high', 'low', 'close', 'previous_close', 'change', 'changepct', 'volume', 'year_high', 'year_low']
        try:
            df[['open', 'high', 'low', 'close', 'previous_close', 'year_high', 'year_low']] = df[['open', 'high', 'low', 'close', 'previous_close', 'year_high', 'year_low']].astype('float', errors='ignore')
        except:
            pass
        if not stats:
            return df
        # otherwise
        advances = 0
        declines = 0
        unchanged = 0
        timestamp = None
        try:
            advances = int(index_stats[0].get('advances'))
            declines = int(index_stats[0].get('declines'))
            unchanged = int(index_stats[0].get('unchanged'))
            timestamp = datetime.strptime(index_stats[1], '%d-%b-%Y %H:%M:%S')
        except:
            print('Warning: Exceptions Occurred While Processing Index Stats Data.')
                    
        stats_data = {
            'total': len(df),
            'advances': advances,
            'declines': declines,
            'unchanged': unchanged,
            'datetime': timestamp
        }
        return df, stats_data
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()


def get_fno_indices_live_snapshot(df: bool = True) -> Union[pd.DataFrame, dict, None]:
    """This functions returns the live snapshot of the fno indices of the NSE Exchange.
        Fno Indices are: NIFTY 50, NIFTY NEXT 50, NIFTY BANK, NIFTY FINANCIAL SERVICES & NIFTY MIDCAP SELECT
    Args:
        df (bool) : If you don't want dataframe format, then you can pass df=False, then the dictionary format data will be returned. defaults to True

    Returns:
        data (DataFrame or dict or None): Returns the live snapshot as Pandas DataFrame or Dictionary. None If any error occurs.

    Note: The DataFrame contains these columns ['datetime', 'index', 'open', 'high', 'low', 'close', 'previous_close',
        'change', 'changepct', 'year_high', 'year_low'].
    """
    try:
        resp  = scraper.get_request(url=urls.live_index_watch_json + str(time()))
        url = 'https://www.nseindia.com/api/NextApi/apiClient?functionName=getIndexData&&type=All'
        if not resp:
            return None
        
        data = resp.json()
        data = data.get('data')
        fno_indices = {'NIFTY 50':'NIFTY', 
                       'NIFTY NEXT 50': 'NIFTYNXT50', 
                       'NIFTY BANK': 'BANKNIFTY', 
                       'NIFTY FIN SERVICE': 'FINNIFTY', 
                       'NIFTY MID SELECT': 'MIDCPNIFTY'}
        if not data:
            return
        if not df:
            fno_data = {}
            for item in data:
                if item.get('indexName') in fno_indices.keys():
                    close = float(item.get('last').replace(',',''))
                    previous_close = float(item.get('previousClose').replace(',',''))
                    fno_data[fno_indices.get(item.get('indexName'))] = {
                        'datetime': datetime.strptime(item.get('timeVal'), '%b %d, %Y %H:%M:%S'),
                        'open': float(item.get('open').replace(',', '')),
                        'high': float(item.get('high').replace(',', '')),
                        'low': float(item.get('low').replace(',', '')),
                        'close': close,
                        'previous_close': previous_close,
                        'change': round(close - previous_close, 2),
                        'changepct': float(item.get('percChange').replace(',', '')),
                        'year_high': float(item.get('yearHigh').replace(',', '')),
                        'year_low': float(item.get('yearLow').replace(',', ''))
                    }
                if len(fno_data) == 5:
                    break
            return fno_data
        # dataframe
        df = pd.DataFrame(data)
        df = df[df['indexName'].isin(fno_indices)]
        df[['yearLow', 'last', 'yearHigh', 'previousClose', 'high', 'low', 'percChange', 'open']] = df[['yearLow', 'last', 'yearHigh', 'previousClose', 'high', 'low', 'percChange', 'open']].replace(',', '', regex=True).astype('float')
        df['change'] = round(df['last'] - df['previousClose'], 2)
        df.drop(['indexType', 'indexOrder', 'indexSubType'], inplace=True, axis=1)
        df['timeVal'] = pd.to_datetime(df['timeVal'], format='%b %d, %Y %H:%M:%S')
        df = df[['timeVal', 'indexName', 'open', 'high', 'low', 'last', 'previousClose', 'change', 'percChange', 'yearHigh', 'yearLow']]
        df.columns = ['datetime', 'index', 'open', 'high', 'low', 'close', 'previous_close', 'change', 'changepct', 'year_high', 'year_low']
        return df.reset_index(drop=True)
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None
    


def get_stock_intraday_tick_by_tick_data(stock_symbol: str, candle_interval: int = None, raw: bool = False):
    """
    Retrieves intraday tick-by-tick data for a given stock symbol and optionally converts it to OHLC candles.
    **Note:** 

    Args:
        stock_symbol (str): The stock symbol for which to retrieve data.
        candle_interval (int, optional): The interval (in minutes) for OHLC candle conversion. If None, raw tick data is returned. Defaults to None.
        raw (bool, optional): If True, returns the raw JSON response. If False, returns a pandas DataFrame. Defaults to False.

    Returns:
        pandas.DataFrame or dict: A pandas DataFrame containing tick data or OHLC candles, or the raw JSON response if raw=True.
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
    
