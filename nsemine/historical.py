from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from datetime import datetime
import pandas as pd
import traceback



def get_stock_historical_data(stock_symbol: str, 
                            start_datetime: datetime, 
                            end_datetime: datetime = datetime.now(), 
                            interval: int | str = 1, 
                            raw: bool = False) -> pd.DataFrame | dict | None:
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
        search_result = __get_script_token(symbol=stock_symbol)
        if not search_result:
            raise ValueError("An error occurred. Token not found.")
        
        # unpacking the tuple
        symbol, token, symbol_type = search_result
        
        return __fetch_historical_data(symbol=symbol,
                                    token=token,
                                    start_datetime=start_datetime,
                                    end_datetime=end_datetime,
                                    interval=interval,
                                    symbol_type=symbol_type,
                                    raw=raw)
        
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None



def get_index_historical_data(index: str, 
                        start_datetime: datetime, 
                        end_datetime: datetime = datetime.now(), 
                        interval: int | str = '3', 
                        raw: bool = False) -> pd.DataFrame | dict | None:
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
        search_result = __get_script_token(symbol=index)
        if not search_result:
            raise ValueError("An error occurred. Token not found.")
        
        # unpacking the tuple
        symbol, token, symbol_type = search_result
        
        return __fetch_historical_data(symbol=symbol,
                                    token=token,
                                    start_datetime=start_datetime,
                                    end_datetime=end_datetime,
                                    interval=interval,
                                    symbol_type=symbol_type,
                                    raw=raw)
        
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None



# ---------------------------------------------#
#               Private Functions              #
# ---------------------------------------------#

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

        resp = scraper.get_request(url=urls.nse_chart_url, params=payload, headers=urls.default_headers)
       
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
        df.columns.name = symbol
        df = utils.process_historical_chart_response(df=df, interval=interval, start_datetime=start_datetime, end_datetime=end_datetime)
        return df.drop_duplicates(subset=['datetime']).reset_index(drop=True)

    except Exception as e:
        print(f'FETCH ERROR! - {e}\n')
        return None



def __get_script_token(symbol: str, 
                       segment: str | None = None, 
                       scrip_type: str | None = None) -> tuple | pd.DataFrame |  None:
    try:
        symbol = symbol.upper()
        segment_set = {'EQ', 'FO', 'IDX'}
        params = {
            'segment': segment if segment in segment_set else '',
            'symbol': symbol
        }

        resp = scraper.get_request(url=urls.search_token_url, params=params)
        data = resp.json()
        df = pd.DataFrame(data['data'])
        
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
        print(f'Could not find the token for the given symbol: {symbol}')
        return None