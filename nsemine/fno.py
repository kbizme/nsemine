import pandas as pd
import traceback
from nsemine.bin import scraper
from nsemine import live
from nsemine.utilities import urls, utils
from datetime import datetime, date






def get_option_chain(
        symbol: str,
        expiry_date: date,
        underlying_type: str = "Equity",
        raw: bool = False,
    ) -> pd.DataFrame | dict | None:
    """
    Fetches option chain data for a given symbol and filters by expiry date.

    Args:
        symbol (str):  Stock or Index symbol (e.g., 'ADANIENT', 'NIFTY', 'BANKNIFTY')
        expiry_date (date): Target expiry date object (e.g., date(2026, 10, 27)). If None, automatically defaults to the nearest active expiry.
        underlying_type (str, optional) : Type of underlying: 'Equity' or 'Indices' (default is 'Equity')
        raw (bool, optional): If True, returns the complete unparsed raw response dictionary.

    Returns:
        data (pd.DataFrame | dict | None): Full Available option chain of the given symbol for the given expiry.
    """
    try:
        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol must be a valid non-empty string.")
        
        clean_symbol = symbol.upper().strip()

        if underlying_type not in ["Equity", "Indices"]:
            raise ValueError("underlying_type must be a string of either 'Equity' or 'Indices'.")

        if not isinstance(expiry_date, date):
            raise ValueError("expiry_date must be a valid datetime.date object.")

        formatted_expiry = expiry_date.strftime("%d-%b-%Y")
        
        params = {
            "type": underlying_type,
            "symbol": clean_symbol,
            "expiry": formatted_expiry
        }

        response = scraper.get_request(url=urls.option_chain, params=params)
        if response is None or response.status_code != 200:
            return None

        raw_data = response.json()
        if raw:
            return raw_data

        return utils.process_option_chain_response(raw_data=raw_data)
    
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return None
  
    


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
        df = df[['symbol', 'underlyingValue', 'latestOI', 'prevOI', 'changeInOI', 'avgInOI', 'volume', 'futValue']]
        df.rename(columns={
            'latestOI': 'latest_oi',
            'prevOI': 'previous_oi',
            'changeInOI': 'oi_change',
            'avgInOI': 'oi_changepct',
            'underlyingValue': 'ltp',
            'futValue': 'turnover',
        }, inplace=True)
        
        # converting the turnover from lakh to absolute value
        df['turnover'] = df['turnover'] * 100000
        df['datetime'] = data.get('timestamp')
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        df.insert(0, 'datetime', df.pop('datetime'))

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




def get_stock_option_details(symbol: str, 
                             only_expiry: bool = False, 
                             only_strikes: bool = False, 
                             raw: bool = False) -> dict | list | None :
    """
    This function fetches stock option's expiry dates and strikes prices of the given stock symbol. 
    It supports various modes to return only specific parts of the data.
 
    Args:
        symbol (str): The stock symbol (e.g., 'AUBANK', 'TCS').
        only_expiry (bool, optional): If True, returns only a list of available expiry dates. Defaults to False.
        only_strikes (bool, optional): If True, returns only a list of available strike prices. Defaults to False.
        raw (bool, optional): If True, returns the raw JSON response from the NSE. Defaults to False.
 
    Returns:
        data (dict | list | None): A dictionary with expiry dates and strike prices, 
            a list of expiry dates, a list of strike prices, the raw data,
            or None if the request fails. The return type depends on the 
            `only_expiry`, `only_strikes`, and `raw` parameters.
 
    """
    try:
        resp = scraper.get_request(url=urls.stk_opt_url.format(symbol))
        if not resp:
            return
        fetched_data = resp.json()
        if raw:
            return fetched_data
 
        # waterfall processing    
        expiry_dates = fetched_data['expiryDates']
        expiry_dates = [datetime.strptime(item, '%d-%b-%Y').date() for item in expiry_dates]
        if only_expiry:
            return expiry_dates
        
        strike_prices = fetched_data['strikePrice']
        strike_prices = [int(x) for x in strike_prices]
        if only_strikes:
            return strike_prices
        return dict(expiry_dates=expiry_dates, strike_prices=strike_prices)
    
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
 
 
 