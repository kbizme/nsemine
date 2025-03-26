from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
import datetime
import json
import pandas as pd
import traceback



def fetch_stock_historical_data(stock_symbol: str, 
                          start_datetime: datetime.datetime, 
                          end_datetime: datetime.datetime = datetime.datetime.now(), 
                          interval: int = 1, 
                          raw: bool = False) -> pd.DataFrame:
    """
    Fetches historical stock data for a given symbol within a specified datetime range.

    Args:
        symbol (str): The stock symbol (e.g., "TCS" etc).
        start_datetime (datetime.datetime): The start datetime for the historical data.
        end_datetime (datetime.datetime, optional): The end datetime for the historical data. Defaults to the current datetime.
        interval (int, optional): The time interval in minutes for the data points. Allowed values are 1, 3, 5, 10, 15, 30, and 60. Defaults to 1 minute.
        raw (bool, optional): If True, returns the raw data without processing. If False, returns processed data. Defaults to False.

    Returns:
        DataFrame: A Pandas DataFrame containing the historical stock data.
        None: If any error occurs during the data fetching process.

    Notes:
        - if you need daily interval data, please use download_daily_data() function in stocks module.
        - If raw=False, the function performs the following processing steps:
            1.  Fixes the candle time shift by subtracting (interval - 1) minutes and 59 seconds.
            2.  Removes pre-market and post-market prices.
    """
    try:
        params = {
            "exch":"N",
            "tradingSymbol":f"{stock_symbol}-EQ",
            "fromDate":0,
            "toDate":int(end_datetime.timestamp()),
            "timeInterval": interval,
            "chartPeriod":"I",
            "chartStart":0
            }
        
        # initializing an empty dataframe
        df = pd.DataFrame()
        resp = scraper.get_request(url=urls.nse_chart_data, headers=urls.default_headers, params=params)
        if resp:
            data = resp.json()
            if data.get('s') == 'Ok':
                del data['s']
                df =  pd.DataFrame(data)
                df = df[df['t'] >= int(start_datetime.timestamp())].reset_index(drop=True)
                
        if raw:
            return df

        # otherwise, processing
        df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        time_offset = datetime.timedelta(minutes=interval - 1, seconds=59)
        df['datetime'] = df['datetime'] - time_offset.seconds
        df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
        df = utils.remove_pre_and_post_market_prices_from_df(df=df)
        return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None