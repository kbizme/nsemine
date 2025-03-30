import traceback
import pandas as pd
from datetime import datetime, timedelta, time as time_obj


def process_stock_quote_data(quote_data: dict) -> dict:
    try:
        processed_data = dict()
        _info = quote_data.get('info')
        if _info:
            symbol = _info.get('symbol')
            name = _info.get('companyName')
            industry = _info.get('industry')
            derivatives = _info.get('isFNOSec')
            
            processed_data['symbol'] = symbol
            processed_data['name'] = name
            processed_data['industry'] = industry
            processed_data['derivatives'] = derivatives

        _metadata = quote_data.get('metadata')
        if _metadata:
            series = _metadata.get('series')
            processed_data['series'] = series
            try:
                date_of_listing = datetime.strptime(_metadata.get('listingDate'), '%d-%b-%Y').date()
                processed_data['date_of_listing'] = date_of_listing
                last_updated = datetime.strptime(_metadata.get('lastUpdateTime'), '%d-%b-%Y %H:%M:%S') or None
                processed_data['last_updated'] = last_updated
                indices = _metadata.get('pdSectorIndAll')
                processed_data['top_indices'] = indices[:5]
            except Exception:
                pass        

        _security_info = quote_data.get('securityInfo')
        if _security_info:
            trading_status = _security_info.get('tradingStatus')
            number_of_shares = _security_info.get('issuedSize')
            face_value = _security_info.get('faceValue') or 0
            processed_data['trading_status'] = trading_status
            processed_data['number_of_shares'] = number_of_shares
            processed_data['face_value'] = face_value

        _price_info = quote_data.get('priceInfo')
        if _price_info:
            open = _price_info.get('open')
            processed_data['open'] = open

            _intraday_range = _price_info.get('intraDayHighLow')
            if _intraday_range:
                high = _intraday_range.get('max')
                low = _intraday_range.get('min')
                processed_data['high'] = high
                processed_data['low'] = low

            close = _price_info.get('close')
            last_price = _price_info.get('lastPrice')
            previous_close = _price_info.get('previousClose')
            change = round(_price_info.get('change') or 0, 2)
            change_percentage = round(_price_info.get('pChange') or 0, 2)
            vwap = _price_info.get('vwap')
            upper_circuit = _price_info.get('upperCP')
            lower_circuit = _price_info.get('lowerCP')
        
            processed_data['close'] = close
            processed_data['last_price'] = last_price
            processed_data['previous_close'] = previous_close
            processed_data['change'] = change
            processed_data['change_percentage'] = change_percentage
            processed_data['vwap'] = vwap
            if upper_circuit and lower_circuit:
                processed_data['upper_circuit'] = float(upper_circuit)
                processed_data['lower_circuit'] = float(lower_circuit)

            _preopen_price = quote_data.get('preOpenMarket')
            if _preopen_price:
                processed_data['preopen_price'] = _preopen_price.get('IEP')

        return processed_data
    except Exception:
        return quote_data




def remove_pre_and_post_market_prices_from_df(df: pd.DataFrame, unit: str = 's') -> pd.DataFrame:
    try:
        if not isinstance(df, pd.DataFrame):
            return df
        if not pd.api.types.is_datetime64_dtype(df['datetime']):
            df['datetime'] = pd.to_datetime(df['datetime'], unit=unit)
        
        df['time'] = df['datetime'].dt.time
        start_time_obj = pd.to_datetime("09:14:59").time() 
        end_time_obj = pd.to_datetime("15:30:00").time()
        filtered_df = df[(df['time'] > start_time_obj) & (df['time'] < end_time_obj)]
        return filtered_df.drop('time', axis=1)
    except Exception as e:
        print(f"Error occurred while removing pre and post market prices: {e}")
        return df




def convert_ticks_to_ohlc(data: pd.DataFrame, interval: int, require_validation: bool = False):
    try:
        if not isinstance(data,pd.DataFrame):
            try:
                df = pd.DataFrame(data)
            except Exception:
                raise ValueError("Invalid Input Data")
        if not isinstance(interval, int):
            try:
                interval = int(interval)
            except ValueError:
                print("Interval(minutes) must be interger or String value.")

        df = data.copy()
        if require_validation:
            if not pd.api.types.is_datetime64_dtype(df['datetime']):
                df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            df = df[(df['datetime'].dt.time >= pd.to_datetime('09:15:00').time()) & \
                    (df['datetime'].dt.time < pd.to_datetime('15:30:00').time())]

        df = df.set_index('datetime')
        df['price'] = df['price'].astype('float')
        df = df['price'].resample(rule=pd.Timedelta(minutes=interval), origin='start').agg(['first', 'max', 'min', 'last']).rename(columns={'first':'open', 'max': 'high', 'min': 'low', 'last':'close'})
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()
        return data


def remove_post_market_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    try:
        post_market_time = time_obj(hour=15, minute=29)
        def is_post_market_anomaly(row):
            if row['datetime'].time() >= post_market_time and row['open'] == row['high'] == row['low'] == row['close']:
                return True
            return False
        anomalous_rows = df[df.apply(is_post_market_anomaly, axis=1)].index
        df.drop(anomalous_rows, inplace=True)
        return df
    except Exception:
        return df


def process_chart_response(df: pd.DataFrame, start_datetime: datetime, interval: str) -> pd.DataFrame:
    try:
        df = df[df['t'] >= int(start_datetime.timestamp())]
        df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']

        if interval in ('D', 'W', 'M'):
            df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
            return df
        
        time_offset = timedelta(minutes=int(interval) - 1, seconds=59)
        df['datetime'] = df['datetime'] - time_offset.seconds
        df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
        df = remove_pre_and_post_market_prices_from_df(df=df)
        df['datetime'] = df['datetime'].apply(lambda dt: dt.replace(second=0, microsecond=0) + timedelta(minutes=1) if dt.second > 1 else dt.replace(second=0, microsecond=0))
        # anomaly detection
        df = remove_post_market_anomalies(df)        
        return df.reset_index(drop=True)
    except Exception:
        return df