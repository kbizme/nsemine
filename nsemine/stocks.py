from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
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