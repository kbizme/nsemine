from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
from time import time
import json
import pandas as pd
import traceback




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
        resp = scraper.get_request(url=urls.al_indices_live_api, initial_url=urls.al_indices_live)
        if not resp:
            return None
        
        # initializing an empty dataframe
        df = pd.DataFrame()
        data = resp.json()
        if data:
            data = data.get('data')
            df = pd.DataFrame(data)
        if raw:
            return df
        # otherwise,
        df = df.dropna()
        df = df[['key', 'index', 'indexSymbol', 'open', 'high', 'low', 'last', 'previousClose', 'variation', 'percentChange', 'yearHigh', 'yearLow','advances', 'declines', 'unchanged', 'oneWeekAgo', 'oneMonthAgo', 'oneYearAgo']]
        df.columns = ['key', 'index', 'symbol', 'open', 'high', 'low', 'close', 'previous_close', 'change', 'changepct', 'year_high', 'year_low','advances', 'declines', 'unchanged', 'one_week_ago', 'one_month_ago', 'one_year_ago']
        df[['advances', 'declines', 'unchanged']] = df[['advances', 'declines', 'unchanged']].astype('int')
        return df
    except Exception as e:
        print('ERROR! - ', e)
        traceback.print_exc()
        return None



def get_all_securities_live_snapshot(series: Union[str,list] = None, raw: bool = False) -> Union[pd.DataFrame, None]:
    """Fetches the live snapshot all the available securities in the NSE Exchange.
    This snapshot includes the last price (close), previous_close price, change, change percentage, volume etc.
    Args:
        series (str, list): Filter the securities by series name.
                        Series name can be EQ, SM, ST, BE, GB, GS, etc...(refer to nse website for all available series names.)
                        Refer to this link: https://www.nseindia.com/market-data/legend-of-series
        raw (bool): Pass True, if you need the raw data without processing.
    Returns:
        DataFrame : Returns Pandas DataFrame object if succeed.
                    OR None if any error occurred.
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
        resp = scraper.get_request(url=urls.nse_all_stocks_live_api, initial_url=urls.nse_all_stocks_live)
        if resp.status_code == 200:
            json_data = json.loads(resp.text)
            base_df = pd.DataFrame(json_data['total']['data'])
            if raw:
                return base_df
            
            # processing
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




def get_index_constituents_live_snapshot(index_name: str = 'NIFTY 50', raw: bool = False):
    """
    Retrieves live snapshot data of constituents for a specified stock market index from the NSE (National Stock Exchange of India).

    This function fetches real-time data for the components of a given index, such as 'NIFTY 50', 'NIFTY BANK', 'NIFTY NEXT 50', etc,. 
    It may return either the raw JSON response or a processed Pandas DataFrame based on the input parameters.

    Args:
        index_name (str, optional): The name of the index for which to retrieve constituent data. Defaults to 'NIFTY 50'.
        raw (bool, optional): If True, returns the raw JSON response from the API. If False, returns a processed Pandas DataFrame. Defaults to False.

    Returns:
        data : Union[pandas.DataFrame or dict or None]: 
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
            'index': index_name,
        }
        resp = scraper.get_request(url=urls.nse_equity_index_api, params=params, initial_url=urls.nse_equity_index)
        if raw:
            return resp.json()
        
        # otherwise,
        data = resp.json()
        data = data['data']
        del data[0]
        df = pd.DataFrame(data)
        df[['name', 'derivatives']] = [[item.get('companyName'), item.get('isFNOSec') ] for item in df['meta']]
        df = df[['symbol', 'name', 'series', 'derivatives', 'open', 'dayHigh', 'dayLow', 'lastPrice', 'previousClose', 'change', 'pChange', 'totalTradedVolume', 'yearHigh', 'yearLow']]
        df.columns = ['symbol', 'name', 'series', 'derivatives', 'open', 'high', 'low', 'close', 'previous_close', 'change', 'changepct', 'volume', 'year_high', 'year_low']
        return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()



def get_fno_indices_live_snapshot():
    """This functions returns the live snapshot of the fno indices of the NSE Exchange.
        Fno Indices are: NIFTY 50, NIFTY NEXT 50, NIFTY BANK, NIFTY FINANCIAL SERVICES & NIFTY MIDCAP SELECT

    Returns:
        DataFrame: Returns the live snapshot as Pandas DataFrame.
        None: If any error occurs.

    Note: The DataFrame contains these columns ['datetime', 'index', 'open', 'high', 'low', 'close', 'previous_close',
        'change', 'changepct', 'year_high', 'year_low'].
    """
    try:
        resp  = scraper.get_request(url=urls.live_index_watch_json + str(time()))
        if not resp:
            return None
        
        data = resp.json()
        data = data.get('data')
        if data:
            df = pd.DataFrame(data)

        fno_indices = ['NIFTY 50', 'NIFTY NEXT 50', 'NIFTY BANK', 'NIFTY FIN SERVICE', 'NIFTY MID SELECT']
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
    


def get_intraday_tick_by_tick_data(stock_symbol: str, candle_interval: int = None, raw: bool = False):
    """
    Retrieves intraday tick-by-tick data for a given stock symbol and optionally converts it to OHLC candles.
    **Note:** The candle interval can be any minutes. 1,2,3.9....69.......143...uptp 375. Whoa!! Are you kidding me? :))

    Args:
        stock_symbol (str): The stock symbol for which to retrieve data.
        candle_interval (int, optional): The interval (in minutes) for OHLC candle conversion. If None, raw tick data is returned. Defaults to None.
        raw (bool, optional): If True, returns the raw JSON response. If False, returns a pandas DataFrame. Defaults to False.

    Returns:
        pandas.DataFrame or dict: A pandas DataFrame containing tick data or OHLC candles, or the raw JSON response if raw=True.
        Returns None in case of errors.

    Example:
        # Get raw tick data
        >>> raw_data = get_intraday_tick_by_tick_data('INFY', raw=True)

        # Get tick data as a DataFrame
        >>> tick_data_df = get_intraday_tick_by_tick_data('INFY')

        # Get OHLC candles with 5-minute interval
        >>> ohlc_df = get_intraday_tick_by_tick_data('INFY', candle_interval=5)

        # Get OHLC candles with a non-standard 143-minute interval.
        >>> unusual_ohlc_df = get_intraday_tick_by_tick_data('INFY', candle_interval=143)
    """
    try:
        resp = scraper.get_request(url=urls.stock_ticks_api.format(stock_symbol), initial_url=urls.nse_equity_quote.format(stock_symbol), headers=urls.default_headers)
        data = resp.json()
        if raw and not candle_interval:
            return data
        # otherwise
        df = pd.DataFrame(data['grapthData'])
        df.columns = ['datetime', 'price', 'type']
        if not candle_interval:
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
    