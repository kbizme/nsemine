from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from nsemine.utilities.tokens import index_tokens
from typing import Union
from datetime import datetime, timedelta
import pandas as pd
import traceback



def get_stock_historical_data(stock_symbol: str, 
                          start_datetime: datetime, 
                          end_datetime: datetime = datetime.now(), 
                          interval: Union[int, str] = 1, 
                          raw: bool = False) -> Union[pd.DataFrame, dict, None]:
    """
    Fetches historical stock data for a given symbol within a specified datetime range for the given interval.
    The interval can be either in minutes or 'D' for Daily, 'W' for Weekly and 'M' for monthly interval data.
    

    Args:
        symbol (str): The stock symbol (e.g., "TCS" etc).
        start_datetime (datetime.datetime): The start datetime for the historical data.
        end_datetime (datetime.datetime, optional): The end datetime for the historical data. Defaults to the current datetime.
        interval (int or str, optional) : The time interval of the historical data. Valid values are 1, 3, 5, 10, 15, 30, 60, 'D', 'W', and 'M'. Defaults to 1 minute.
        raw (bool, optional): If True, returns the raw data without processing. If False, returns processed data. Defaults to False.

    Returns:
        data (Union[pd.DataFrame, dict, None]) : A Pandas DataFrame containing the historical stock data. If you pass raw=True,
        then you will get the data in dictionary format. Returns None If any error occurs during data fetching or processing.

    Notes:
        - You can try other unsual intervals like 7, 18, 50, 143 minutes, etc than those commonly used intervals.
        - By Default, NSE provides data delayed by 1 minutes. so, when using this functions (or any other live functions) an one minute delay is expected.
    Example:
        - To get the daily interval data.
        >>> df = get_stock_historical_data('TCS', datetime(2025, 1, 1), datetime.now(), interval='D')

        - To get 3-minute interval data.
        >>> df = get_stock_historical_data('INFY', datetime(2025, 1, 1), datetime.now(), interval=3)
    """
    try:       
        params = {
        "exch":"N",
        "tradingSymbol":f"{stock_symbol}-EQ",
        "fromDate":int(start_datetime.timestamp()),
        "toDate":int(end_datetime.timestamp()) + timedelta(hours=5, minutes=30).seconds,
        "chartStart":0
        }
        if interval in ('D', 'W', 'M'):
            params.update({'timeInterval': 1, 'chartPeriod': str(interval)})
        else:
            params.update({'timeInterval': int(interval), 'chartPeriod': 'I'})


        resp = scraper.get_request(url=urls.nse_chart, headers=urls.default_headers, params=params)
        raw_data = resp.json()
        if raw:
            return raw_data
        # otherwise
        if raw_data.get('s') != 'Ok':
            return 
        del raw_data['s']
        df =  pd.DataFrame(raw_data)
        return utils.process_chart_response(df=df, start_datetime=start_datetime, interval=interval)
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None
    



def get_index_historical_data(index: str, 
                        start_datetime: datetime, 
                        end_datetime: datetime = datetime.now(), 
                        interval: Union[str] = 'ONE_DAY', 
                        raw: bool = False) -> Union[pd.DataFrame, dict, None]:
    """
    Fetches historical data for the given index within a specified datetime range for the given interval.
    The interval can be either in minutes or 'D' for Daily, 'W' for Weekly and 'M' for monthly interval data.
    

    Args:
        index (str): The index name (e.g., "NIFTY 50, NIFTY BANK" etc).
        start_datetime (datetime.datetime): The start datetime for the historical data.
        end_datetime (datetime.datetime, optional): The end datetime for the historical data. Defaults to the current datetime.
        interval (int or str, optional) : The time interval of the historical data. Valid values are 1, 3, 5, 10, 15, 30, 60, 'D', 'W', and 'M'. Defaults to 1 minute.
        raw (bool, optional): If True, returns the raw data without processing. If False, returns processed data. Defaults to False.

    Returns:
        data (Union[pd.DataFrame, dict, None]) : A Pandas DataFrame containing the historical data. If you pass raw=True,
        then you will get the data in dictionary format. Returns None If any error occurs during data fetching or processing.

    Notes:
        - You can try other unsual intervals like 7, 18, 50, 143 minutes, etc than those commonly used intervals.
        - By Default, NSE provides data delayed by 1 minutes. so, when using this functions (or any other live functions) an one minute delay is expected.

    Example:
        - To get the daily interval data.
        >>> df = get_index_historical_data('NIFTY 50', datetime(2025, 1, 1), datetime.now(), interval='D')

        - To get 3-minute interval data.
        >>> df = get_index_historical_data('NIFTY BANK', datetime(2025, 1, 1), datetime.now(), interval=3)
    """
    try:
        token = index_tokens.get(index.upper())
        if not token:
            raise Exception("Couldn't find the index. Please check the index name.")
        params = {
            "exch":"N",
            "instrType":"C",
            "scripCode":token,
            "ulToken":token,
            "fromDate":int(start_datetime.timestamp()),
            "toDate":int(end_datetime.timestamp()) + timedelta(hours=5, minutes=30).seconds,
            "chartStart":0
        }
        if interval in ('D', 'W', 'M'):
            params.update({'timeInterval': 1, 'chartPeriod': interval})
        else:
            params.update({'timeInterval': int(interval), 'chartPeriod': 'I'})
        resp = scraper.get_request(url=urls.nse_chart_symbol, params=params)
        raw_data = resp.json()
        if raw:
            return raw_data
        # otherwise, processing
        if raw_data.get('s') != 'Ok':
            return
        del raw_data['s']
        df =  pd.DataFrame(raw_data)
        df = utils.process_chart_response(df=df, start_datetime=start_datetime, interval=interval)
        df.drop(columns=['volume'], inplace=True)  
        return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None

