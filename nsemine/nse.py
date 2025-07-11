from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
import json
import pandas as pd
import numpy as np
import traceback
from io import StringIO
from datetime import datetime



def get_market_status(market_name: str = None) -> Union[list[dict], bool, None]:
    """
    Returns the current market status of the NSE Exchange.
    Args:
        market_name (str): You can pass the exact market name to get its status.
                            For example -  CM for Capital Market, CUR for Currency,
                            COM for Commodity, DB for Debt, CURF for Currency Future.
    Returns:
        market_status (list[dict], bool, None) : Returns the market status.

        Note: if market_name is passed then it returns True if the market is open, and False if the market is closed.
            If no market_name is given as argument, then it returns the raw data as list of dictionaries.
            Returns None, if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.market_status)
        if resp:
            fetched_data = resp.json()['marketState']
        if not market_name:
            return fetched_data
        
        # otherwise,
        mapper = { 'CM': 'Capital Market', 'CUR': 'Currency', 'COM': 'Commodity', 'DB': 'Debt', 'CURF': 'currencyfuture'}
        market_name = mapper.get(market_name)
        for market in fetched_data:
            if market.get('market') == market_name:
                return market.get('marketStatus') == 'Open'
        
        # if nothing matched, then returning the raw data
        return fetched_data
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()



def get_market_stats():
    """
    This function fetches the market stattistics data from the NSE Exchange.
    The data includes number of year high or low stocks, circuit breaker stocks, positive or
    negative stocks etc.

    Returns:
        data (dict or None) : The stats data in dictionary format. Returns None if any error occurred.
    """
    try:
        data = scraper.get_request(url=urls.next_api_f.format('getMarketStatistics'))
        if data:
            data =  data.json()['data']
            data['asOnDate'] = datetime.strptime(data['asOnDate'], '%d-%b-%Y %H:%M:%S')
            return data
        return None
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None
    


def get_holiday_lists() -> Union[pd.DataFrame, None]:
    """
    This function fetches the holidays at the NSE Exchange.

    Returns:
        df (DataFrame) : Pandas DataFrame containing all the holidays.

        Returns None, if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.holiday_list)
        if resp:
            fetched_data = resp.json()
        
        df = pd.DataFrame(fetched_data.get('CM'))
        if not df.empty:
            df = df[['tradingDate', 'weekDay', 'description']]
            df['tradingDate'] = pd.to_datetime(df['tradingDate'], errors='coerce')
            df.columns = ['date', 'day', 'description']
            return df
        return None
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()



def get_all_indices_list() -> Union[pd.DataFrame, None]:
    """
    This functions fetches all the available indices at the NSE Exchange.
    Returns:
        df (DataFrame) : Pandas DataFrame containing all the nse indices names.

        Returns None, if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.nifty_index_maping)
        if resp:
            data = resp.text
            if data.startswith('\ufeff'):
                data = json.loads(data[1:])
            df = pd.DataFrame(data)
            df.columns = ['trading_index', 'full_name']
            return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()



def get_all_equities_list(raw: bool = False) -> Union[pd.DataFrame, None]:
    """
    This functions fetches all the available equity list at the NSE Exchange.
    Args:
        raw (bool): Pass True, if you need the raw data without processing.
    Returns:
        df (DataFrame) : Pandas DataFrame containing all the nse equity list.

        Returns None, if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.nse_equity_list)
        if resp:
            byte_steams = StringIO(resp.text)
            df = pd.read_csv(byte_steams)
            if raw:
                return df
            # processing
            df = df[['SYMBOL', 'NAME OF COMPANY', ' SERIES', ' DATE OF LISTING', ' ISIN NUMBER', ' FACE VALUE']]
            df.columns = ['symbol', 'name', 'series', 'date_of_listing', 'isin_number', 'face_value']
            df['date_of_listing'] = pd.to_datetime(df['date_of_listing'], format='%d-%b-%Y')
            return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()


def get_fno_stocks_lists(raw: bool = False) -> Union[pd.DataFrame, None]:
    """
    This functions fetches all the fno equity list at the NSE Exchange.
    Args:
        raw (bool): Pass True, if you need the raw data without processing.
    Returns:
        df (DataFrame) : Pandas DataFrame containing all the nse equity list.

        Returns None, if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.underlying)
        data = resp.json()
        if raw:
            return data
        
        df = pd.DataFrame(data['data']['UnderlyingList'])
        df = df[['underlying', 'symbol']]
        df.columns = ['name', 'symbol']
        return df    
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        


def get_pre_open_data(key: str = 'NIFTY', raw: bool = False) -> Union[pd.DataFrame, dict, None]:
    """
    Retrieves pre-open market data from the NSE India Website.

    This function fetches pre-open market data for a specified instrument (e.g., NIFTY)
    from the NSE India API. It can return either the raw JSON response or a processed
    pandas DataFrame containing relevant market data.

    Args:
        key (str, optional): The instrument key to fetch data for (e.g., 'NIFTY', 'BANKNIFTY', 'SME', 'FO', 'OTHERS', 'ALL').
            Defaults to 'NIFTY'.
        raw (bool, optional): If True, returns the raw JSON response from the API.
            If False, returns a processed pandas DataFrame. Defaults to False.

    Returns:
        df (pandas.DataFrame or dict or None):
            - If raw is False, returns a pandas DataFrame with columns: ['symbol', 'iep', 'previous_close', 'change', 'changepct', 'quantity',
              'total_turn_over', 'market_cap', 'year_high', 'year_low'].
            - If raw is True, returns the raw JSON response (a dictionary).
            - Returns None if an error occurs during the API request or data processing.
    Raises:
        Exception: If any error occurs during the API request or data processing, the error
            is printed to the console, and the traceback is also printed.

    Example:
        >>> df = get_pre_open_data(key='NIFTY')
        >>> print(df.head())
        >>> raw_data = get_pre_open_data(key='BANKNIFTY', raw=True)
        >>> print(raw_data)
    """
    try:
        
        resp = scraper.get_request(url=urls.pre_open.format(key))
        if not resp:
            return None
        data = resp.json()
        if raw:
            return data
        # otherwise
        container = list()
        data = data.get('data')
        for item in data:
            meta_data = item.get('metadata')
            if meta_data:
                container.append(meta_data)
        df = pd.DataFrame(container)
        df = df[['symbol', 'iep', 'previousClose', 'change', 'pChange', 'finalQuantity', 'totalTurnover', 'marketCap', 'yearHigh', 'yearLow']]
        df.columns = ['symbol', 'iep', 'previous_close', 'change', 'changepct', 'quantity', 'total_turn_over', 'market_cap', 'year_high', 'year_low']
        return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None



def get_securities_at_52_weeks_high(raw: bool = False, need_timestamp: bool = False) -> Union[pd.DataFrame, tuple[pd.DataFrame, datetime], dict, None]:
    """
    Retrieves live data for securities hitting a 52-week High from NSE India.
    This securities list may contains stocks, ETFs, Mutual Funds etc. 
    Returns type of this function varies based on the given arguments.
    
    Args:
        raw (bool): If True, returns the raw JSON response from the API.
                    If False (default), returns a Pandas DataFrame with processed data.
        
        need_timestamp (bool): The timestamp of the data, If True then the return type is a tuple containing the processed DataFrame and the timestamp.
                               If False (default), returns only the processed DataFrame.
                            
    Returns:
        df (Union[DataFrame or tuple[DataFrame, datetime] or dict or None]): Pandas DataFrame or dict if successful, None if an error occurs.
    """
    try:
        resp = scraper.get_request(url=urls.new_year_high)
        if not resp:
            return None
        data = resp.json()
        if raw:
            return data
        
        # otherwise
        df = pd.DataFrame(data['data'])
        df.columns = ['symbol', 'series', 'name', 'new_high', 'previous_high', 'previous_date', 'close', 'previous_close', 'change', 'changepct']
        df['previous_close'] = df['previous_close'].astype('float')
        df['previous_date'] = pd.to_datetime(df['previous_date'],  errors='coerce')
        df['changepct'] = round(df['changepct'], 2)
        if need_timestamp:
            timestamp = data.get('timestamp')
            timestamp = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
            return df, timestamp
        return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None



def get_securities_at_52_weeks_low(raw: bool = False, need_timestamp: bool = False) -> Union[pd.DataFrame, tuple[pd.DataFrame, datetime], dict, None]:
    """
    Retrieves live data for securities hitting a 52-week Low from NSE India.
    This securities list may contains Stocks, ETFs, Mutual Funds etc.
    Returns type of this function varies based on the given arguments.

    Args:
        raw (bool): If True, returns the raw JSON response from the API.
                    If False (default), returns a Pandas DataFrame with processed data.
        
        need_timestamp (bool): The timestamp of the data, If True then the return type is a tuple containing the processed DataFrame and the timestamp.
                               If False (default), returns only the processed DataFrame.
                            
    Returns:
        df (Union[DataFrame or tuple[DataFrame, datetime] or dict or None]): Pandas DataFrame or dict if successful, None if an error occurs.
    """
    try:
        resp = scraper.get_request(url=urls.new_year_low)
        if not resp:
            return None
        data = resp.json()
        if raw:
            return data
        
        # otherwise
        df = pd.DataFrame(data['data'])
        df.columns = ['symbol', 'series', 'name', 'new_low', 'previous_low', 'previous_date', 'close', 'previous_close', 'change', 'changepct']
        df['previous_close'] = df['previous_close'].astype('float')
        df['previous_date'] = pd.to_datetime(df['previous_date'],  errors='coerce')
        df['changepct'] = round(df['changepct'], 2)
        if need_timestamp:
            timestamp = data.get('timestamp')
            timestamp = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
            return df, timestamp
        return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None

 
def get_securities_above_previous_close(raw: bool = False, need_timestamp: bool = False) -> Union[pd.DataFrame, tuple[pd.DataFrame, datetime], dict, None]:
    """This functions returns the list of securities that currently trading at higher prices than yesterday.
    
    Args:
        raw (bool, optional): If you want the raw api response, then pass this parameter as True. Defaults to False.
        need_timestamp (bool): The timestamp of the data, If True then the return type is a tuple containing the processed DataFrame and the timestamp.
                               If False (default), returns only the processed DataFrame.
    Returns:
        df (Union[DataFrame or tuple[DataFrame, datetime] or dict or None]):  Returns a pandas DataFrame or None if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.base_nse_api+urls.advance)
        if not resp:
            return
        
        data = resp.json()
        if raw:
            return data
        # otherwise
        df = pd.DataFrame(data=data['advance']['data'])
        processed_df =  utils.process_aud(df=df)
        
        if need_timestamp:
            timestamp = data.get('timestamp')
            timestamp = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
            return processed_df, timestamp

        return processed_df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None


  
def get_securities_below_previous_close(raw: bool = False, need_timestamp: bool = False) -> Union[pd.DataFrame, tuple[pd.DataFrame, datetime], dict, None]:
    """This functions returns the list of securities that currently trading at lower prices than yesterday.
    
    Args:
        raw (bool, optional): If you want the raw api response, then pass this parameter as True. Defaults to False.
        need_timestamp (bool): The timestamp of the data, If True then the return type is a tuple containing the processed DataFrame and the timestamp.
                               If False (default), returns only the processed DataFrame.
                               
    Returns:
        df (Union[DataFrame or tuple[DataFrame, datetime] or dict or None]): Returns a pandas DataFrame or None if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.base_nse_api+urls.decline)
        if not resp:
            return
        
        data = resp.json()
        if raw:
            return data
        # otherwise
        df = pd.DataFrame(data=data['decline']['data'])
        processed_df =  utils.process_aud(df)
        if need_timestamp:
            timestamp = data.get('timestamp')
            timestamp = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
            return processed_df, timestamp

        return processed_df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None


 
    
def get_securities_same_as_previous_close(raw: bool = False, need_timestamp: bool = False) -> Union[pd.DataFrame, tuple[pd.DataFrame, datetime], dict, None]:
    """This functions returns the list of securities that currently trading at the same prices as yesterday.
    
    Args:
        raw (bool, optional): If you want the raw api response, then pass this parameter as True. Defaults to False.
        need_timestamp (bool): The timestamp of the data, If True then the return type is a tuple containing the processed DataFrame and the timestamp.
                               If False (default), returns only the processed DataFrame.
                               
    Returns:
        df (Union[pd.DataFrame, tuple[pd.DataFrame, datetime], dict, None]): Returns a pandas DataFrame or None if any error occurred.
    """
    try:
        resp = scraper.get_request(url=urls.base_nse_api+urls.unchanged)
        if not resp:
            return
        
        data = resp.json()
        if raw:
            return data
        # otherwise
        df = pd.DataFrame(data=data['Unchange']['data'])
        processed_df =  utils.process_aud(df)
        if need_timestamp:
            timestamp = data.get('timestamp')
            timestamp = datetime.strptime(timestamp, '%d-%b-%Y %H:%M:%S')
            return processed_df, timestamp

        return processed_df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None

 
    
def get_most_liquid_stocks(raw: bool = False):
    """This function fetches the top 20 stocks with the most volume at NSE Exchange.
    
    Args:
        raw (bool, optional): Pass this parameter as True if you want the raw response. Defaults to False.
    
    Returns:
        df (DataFrame or None): Returns a Pandas DataFrame, or None if any error occurs.
    """
    try:
        resp = scraper.get_request(urls.base_nse_api+urls.most_active)
        if not resp:
            return
        data = resp.json()
        if raw:
            return data
        # otherwise.
        df = pd.DataFrame(data.get('data'))
        
        df = df[['lastUpdateTime', 'symbol', 'open', 'dayHigh', 'dayLow', 'lastPrice', 'previousClose', 'change', 'pChange', 'totalTradedVolume', 'totalTradedValue', 'yearHigh', 'yearLow']]
        df.rename(inplace=True, columns={'lastUpdateTime': 'datetime', 'dayHigh': 'high', 'dayLow': 'low', 'lastPrice': 'close', 'previousClose': 'previous_close',
                                            'pChange': 'changepct', 'totalTradedVolume': 'volume', 'totalTradedValue': 'traded_value', 'yearHigh': 'year_high', 'yearLow': 'year_low'})
        
        try:
            df['datetime'] = pd.to_datetime(df['datetime'], format='%d-%b-%Y %H:%M:%S')
        except:
            df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')

        df['change'] = np.round(df['change'], 2)
        df['changepct'] = np.round(df['changepct'], 2)
        return df
    
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None



def get_most_value_traded_stocks(raw: bool = False):
    """This function fetches the top 20 stocks with the most traded value at NSE Exchange.
    
    Args:
        raw (bool, optional): Pass this parameter as True if you want the raw response. Defaults to False.
    
    Returns:
        df (DataFrame or None): Returns a Pandas DataFrame, or None if any error occurs.
    """
    try:
        resp = scraper.get_request(urls.base_nse_api+urls.most_valued)
        if not resp:
            return
        data = resp.json()
        if raw:
            return data
        # otherwise.
        df = pd.DataFrame(data.get('data'))
        
        df = df[['lastUpdateTime', 'symbol', 'open', 'dayHigh', 'dayLow', 'lastPrice', 'previousClose', 'change', 'pChange', 'totalTradedVolume', 'totalTradedValue', 'yearHigh', 'yearLow']]
        df.rename(inplace=True, columns={'lastUpdateTime': 'datetime', 'dayHigh': 'high', 'dayLow': 'low', 'lastPrice': 'close', 'previousClose': 'previous_close',
                                            'pChange': 'changepct', 'totalTradedVolume': 'volume', 'totalTradedValue': 'traded_value', 'yearHigh': 'year_high', 'yearLow': 'year_low'})
        
        try:
            df['datetime'] = pd.to_datetime(df['datetime'], format='%d-%b-%Y %H:%M:%S')
        except:
            df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
                
        df['change'] = np.round(df['change'], 2)
        df['changepct'] = np.round(df['changepct'], 2)
        return df
    
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None



def get_todays_gainers(key: str = 'ALL', raw: bool = False):
    """ This function returns the gainers stocks of today's trading session.
    
    Args:
        key (str): This defines the type of the gainers, i.e. Nifty, Bank Nifty, FNO Securities etc. Defaults to ALL.
                    The other possible values includes ALL, NIFTY, NIFTYNEXT50, BANKNIFTY, FNO, GT20 (Securities greater than 20) & LT20 (Securities less than 20).
        raw (bool, optional): Pass this parameter as True if you want the raw response. Defaults to False.
    
    Returns:
        df (DataFrame or None): Returns a Pandas DataFrame, or None if any error occurs.
    
    """
    try:
        resp = scraper.get_request(url=urls.base_nse_api+urls.all_gainers)
        if not resp:
            return
        data = resp.json()
        if raw:
            return data
        # otherwise
        key_mapper = {
            'ALL': 'allSec',
            'NIFTY': 'NIFTY',
            'BANKNIFTY': 'BANKNIFTY',
            'FNO': 'FOSec',
            'NIFTYNEXT50': 'NIFTYNEXT50',
            'NIFTYNXT50': 'NIFTYNEXT50',
            'GT20': 'SecGtr20',
            'LT20': 'SecLwr20'
        }
        key = key_mapper.get(key.upper())
        data = data.get(key)
        # data processing
        return utils.process_movers_data(data=data) 
   
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None



def get_todays_losers(key: str = 'ALL', raw: bool = False):
    """ This function returns the losers stocks of today's trading session.
    
    Args:
        key (str): This defines the type of the losers, i.e. Nifty, Bank Nifty, FNO Securities etc. Defaults to ALL.
                    The other possible values includes ALL, NIFTY, NIFTYNEXT50, BANKNIFTY, FNO, GT20 (Securities greater than 20) & LT20 (Securities less than 20).
        raw (bool, optional): Pass this parameter as True if you want the raw response. Defaults to False.
    
    Returns:
        df (DataFrame or None): Returns a Pandas DataFrame, or None if any error occurs.
    
    """
    try:
        resp = scraper.get_request(url=urls.base_nse_api+urls.all_losers)
        if not resp:
            return
        data = resp.json()
        if raw:
            return data
        # otherwise
        key_mapper = {
            'ALL': 'allSec',
            'NIFTY': 'NIFTY',
            'BANKNIFTY': 'BANKNIFTY',
            'FNO': 'FOSec',
            'NIFTYNEXT50': 'NIFTYNEXT50',
            'NIFTYNXT50': 'NIFTYNEXT50',
            'GT20': 'SecGtr20',
            'LT20': 'SecLwr20'
        }
        key = key_mapper.get(key.upper())
        data = data.get(key)
        # data processing
        return utils.process_movers_data(data=data) 
   
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None
    
    