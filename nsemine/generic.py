from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
import json
import pandas as pd
import traceback
from io import StringIO



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
    


def get_holiday_list() -> Union[pd.DataFrame, None]:
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



def get_all_equities_list(raw: bool = False):
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
            df['date_of_listing'] = pd.to_datetime(df['date_of_listing'])
            return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()



