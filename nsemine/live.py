from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
import datetime
import json
import pandas as pd
import traceback



def get_all_nse_securities_live_snapshot(series: Union[str,list] = None, raw: bool = False) -> Union[pd.DataFrame, None]:
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
        resp = scraper.get_request(url=urls.nse_live_stock_analysis_api, initial_url=urls.nse_live_stock_analysis)
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