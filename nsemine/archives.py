from nsemine.bin import scraper
from nsemine.utilities import urls
from io import StringIO
from datetime import date
import pandas as pd
import traceback




def get_daily_bhavcopy_and_deliverables_data(series: str = None, trade_date: date = None, raw: bool = False) -> pd.DataFrame | None:
    """
    Fetches the daily Capital Market (CM) Bhavcopy data from the NSE, including price, volume, and delivery statistics.
    The function standardizes column names and converts turnover from lakhs (hundred thousands) to absolute value.

    Args:
        series (str, optional): The security series to filter the data by (e.g., 'EQ' for Equity). If None, all series are returned. Defaults to None.
        trade_date (date, optional): The trading date of the bhavcopy and deliverable data. Defaults latest session.
        raw (bool): If True, returns the DataFrame directly after initial reading, with original column names. Defaults to False.

    Returns:
        df (pd.DataFrame or None): A cleaned DataFrame containing the daily bhavcopy 
            and delivery data with standardized columns, or None if an error occurs.
                Columns include:
                - date (date)
                - symbol (str)
                - series (str)
                - previous_close (float)
                - open (float)
                - high (float)
                - low (float)
                - close (float)
                - vwap (float)
                - volume (float)
                - turnover (float) - Converted to absolute value
                - delivery_volume (float)
                - delivery_pct (float)
    """
    try:
        if trade_date:
            url = urls.historic_bhavcopy_cm.format(session_date=trade_date.strftime('%d-%b-%Y'))
        else:
            url = urls.full_bhavcopy_cm.format(session_date=date.today().strftime('%d%m%Y'))

        resp = scraper.get_request(url=url)
        
        # processing the response
        df = pd.read_csv(StringIO(resp.text))
        if raw:
            return df
        # otherwise

        df.columns = df.columns.str.strip()
        df.rename(columns={'DATE1': 'date', 'SYMBOL': 'symbol', 'SERIES': 'series', 'PREV_CLOSE': 'previous_close',
                           'OPEN_PRICE': 'open', 'HIGH_PRICE': 'high', 'LOW_PRICE': 'low', 'CLOSE_PRICE': 'close',
                           'AVG_PRICE': 'vwap', 'TTL_TRD_QNTY': 'volume', 'TURNOVER_LACS': 'turnover',
                           'DELIV_QTY': 'delivery_volume', 'DELIV_PER': 'delivery_pct'
                           },
                  inplace=True)
        df = df[['date', 'symbol', 'series', 'previous_close', 'open', 'high', 'low','close', 'vwap', 'volume', 'turnover', 'delivery_volume', 'delivery_pct']].copy()
        if series:
            df = df[df['series'].str.strip() == series].reset_index(drop=True)
        # datatype conversion
        df[['delivery_volume', 'delivery_pct']] = df[['delivery_volume', 'delivery_pct']].astype(float, errors='ignore')
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
        df['turnover'] = df['turnover'] * 100000 # converting back into absolute value
        return df        
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()


