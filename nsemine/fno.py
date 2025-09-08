import pandas as pd
import traceback
from nsemine.bin import scraper
from nsemine import live
from nsemine.utilities import urls




def get_oi_spurts(raw: bool = False, sentiment_analysis: bool = True) -> pd.DataFrame | dict | None:
    """Fetches Open Interest (OI) spurts data from the NSE and performs sentiment analysis.

    This function retrieves OI data, renames columns for clarity, and can optionally
    merge with live equity data to perform a sentiment analysis based on changes
    in OI and price.

    Args:
        raw (bool, optional): If True, returns the raw JSON data from the API. Defaults to False.
        sentiment_analysis (bool, optional): If True, merges OI data with live equity price data to add columns
                                             for market action and sentiment. Defaults to True.

    Returns:
        df (pandas.DataFrame or dict or None): A pandas DataFrame containing OI data and
                                  (optionally) sentiment analysis, or a raw dictionary if 'raw' is True. Otherwise. returns None.
    """
    try:
        resp = scraper.get_request(url=urls.oi_spurts_underlying)
        data = resp.json()
        if raw:
            return data
        
        df = pd.DataFrame(data['data'])
        df = df[['symbol', 'underlyingValue', 'latestOI', 'prevOI', 'changeInOI', 'avgInOI', 'volume']]
        df.rename(columns={
            'latestOI': 'latest_oi',
            'prevOI': 'previous_oi',
            'changeInOI': 'oi_change',
            'avgInOI': 'oi_changepct',
            'underlyingValue': 'ltp',
        }, inplace=True)
        
        if not sentiment_analysis:
            return df
        
        all_live_quotes = live.get_index_constituents_live_snapshot(index='NIFTY 500')
        final_df = pd.merge(df, all_live_quotes[['symbol', 'previous_close', 'change', 'changepct']], on='symbol', how='left')
        
        def get_sentiment(row):
            oi_change = row['oi_change']
            price_change = row['change']
            
            # Handles cases where there is no change in OI or price
            if oi_change == 0 and price_change == 0:
                return 'Neutral', 'Sideways'
            elif oi_change > 0 and price_change > 0:
                return 'Long Buildup', 'Bullish'
            elif oi_change > 0 and price_change < 0:
                return 'Short Buildup', 'Bearish'
            elif oi_change < 0 and price_change > 0:
                return 'Short Covering', 'Bullish'
            elif oi_change < 0 and price_change < 0:
                return 'Long Unwinding', 'Bearish'
            elif oi_change == 0 and price_change != 0:
                return 'Neutral', 'No OI change'
            elif oi_change != 0 and price_change == 0:
                return 'Neutral', 'No Price change'
            else:
                return 'N/A', 'N/A' # Fallback for any unexpected cases

        final_df[['market_action', 'interpretation']] = final_df.apply(get_sentiment, axis=1, result_type='expand')
        
        final_df.drop(columns=['previous_close', 'change', 'changepct'], inplace=True, errors='ignore')
        
        return final_df
    
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None