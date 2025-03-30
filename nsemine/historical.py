from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
from datetime import datetime, timedelta
import pandas as pd
import traceback



def get_stock_intraday_interval_data(stock_symbol: str, 
                          start_datetime: datetime, 
                          end_datetime: datetime = datetime.now(), 
                          interval: Union[int, str] = 1, 
                          raw: bool = False) -> Union[pd.DataFrame, dict, None]:
    """
    Fetches historical stock data for a given symbol within a specified datetime range.
    This function fetches data for small intraday interval. For daily, weekly or monthly interval data, 
    please use get_stock_historical_data() function.
    

    Args:
        symbol (str): The stock symbol (e.g., "TCS" etc).
        start_datetime (datetime.datetime): The start datetime for the historical data.
        end_datetime (datetime.datetime, optional): The end datetime for the historical data. Defaults to the current datetime.
        interval (int or str) (optional): The time interval in minutes for the data points. Valid values are 1, 3, 5, 10, 15, 30, and 60. Defaults to 1 minute.
        raw (bool, optional): If True, returns the raw data without processing. If False, returns processed data. Defaults to False.

    Returns:
        data (Union[pd.DataFrame, dict, None]) : A Pandas DataFrame containing the historical stock data. If you pass raw=True,
        then you will get the data in dictionary format. Returns None If any error occurs during data fetching or processing.

    Notes:
        - You can try other unsual intervals like 7, 18, 50, 143 minutes, etc than those commonly used intervals, but the data might not be properly organized or accurate.
        - If you need daily interval data, please use get_stock_historical_data() function in historical module.
        - If raw=False, the function performs the following processing steps:
            1.  Fixes the candle time shift.
            2.  Removes pre-market and post-market anomalies.
    """
    try:       
        params = {
            "exch":"N",
            "tradingSymbol":f"{stock_symbol}-EQ",
            "fromDate":0,
            "toDate":int(end_datetime.timestamp()),
            "timeInterval": int(interval),
            "chartPeriod":"I",
            "chartStart":0
            }

        resp = scraper.get_request(url=urls.nse_chart_data, headers=urls.default_headers, params=params)
        if resp:
            raw_data = resp.json()
        if raw:
            return raw_data
        # otherwise, processing
        if raw_data.get('s') != 'Ok':
            return 
        del raw_data['s']
        df =  pd.DataFrame(raw_data)
        df = df[df['t'] >= int(start_datetime.timestamp())]
        df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        time_offset = timedelta(minutes=int(interval) - 1, seconds=59)
        df['datetime'] = df['datetime'] - time_offset.seconds
        df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
        df = utils.remove_pre_and_post_market_prices_from_df(df=df)
        df['datetime'] = df['datetime'].apply(lambda dt: dt.replace(second=0, microsecond=0) + timedelta(minutes=1) if dt.second > 1 else dt.replace(second=0, microsecond=0))
        # anomaly detection
        df = utils.remove_post_market_anomalies(df)        
        return df.reset_index(drop=True)
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None
    



def get_stock_historical_data(stock_symbol: str, 
                        start_datetime: datetime, 
                        end_datetime: datetime = datetime.now(), 
                        interval: Union[str] = 'ONE_DAY', 
                        raw: bool = False) -> Union[pd.DataFrame, dict, None]:
    pass