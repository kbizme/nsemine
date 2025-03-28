import io
import traceback
import pandas as pd
from datetime import datetime
import zlib
import gzip
import brotli
import zstandard



def decompress_data(compressed_data: bytes) -> bytes:
    """
    Automatically detects and decompresses data compressed with gzip, deflate, brotli, or zstd.

    Args:
        compressed_data: The compressed bytes.

    Returns:
        The decompressed bytes, or the original bytes if decompression fails.
    """
    if not compressed_data:
        return b""

    # gzip check
    if compressed_data.startswith(b'\x1f\x8b'):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as f:
                return f.read()
        except OSError:
            pass  
    # deflate check
    try:
        return zlib.decompress(compressed_data)
    except zlib.error:
        try:
            return zlib.decompress(compressed_data, wbits=-zlib.MAX_WBITS) #raw deflate
        except zlib.error:
            pass 
    # brotli check
    try:
        return brotli.decompress(compressed_data)
    except brotli.error:
        pass  
    # zstd check
    try:
        dctx = zstandard.ZstdDecompressor()
        return dctx.decompress(compressed_data)
    except zstandard.ZstdError:
        pass  
    # If all decompression attempts fail, returning the original data.
    return compressed_data



def remove_pre_and_post_market_prices_from_df(df: pd.DataFrame, unit: str = 's') -> pd.DataFrame:
    """
    This function expects that the given dataframe has a column 'datetime'.

    Args:
        df (DataFrame) : A Pandas DataFrame
        unit (str): Unit of the timestamp.
    Returns:
        df (DataFrame) : The processed dataframe.
    
    Note:
        If the datetime of the given dataframe is in timestamp, then you can provide the unit, Default is 'Second'.
        And of any error occurs during the conversion, it returns the given data as it is.
        
    """
    try:
        if not isinstance(df, pd.DataFrame):
            return df
        # otherwise,
        if not pd.api.types.is_datetime64_dtype(df['datetime']):
            df['datetime'] = pd.to_datetime(df['datetime'], unit=unit)
        
        # filtering
        df['time'] = df['datetime'].dt.time
        start_time_obj = pd.to_datetime("09:14:00").time() 
        end_time_obj = pd.to_datetime("15:31:00").time()
        filtered_df = df[(df['time'] > start_time_obj) & (df['time'] < end_time_obj)]
        return filtered_df.drop('time', axis=1)
    except Exception as e:
        print(f"Error occurred while removing pre and post market prices: {e}")
        return df



def process_stock_quote_data(quote_data: dict) -> dict:
    try:
        # initializng an empty dictionary
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

        # finally returning the processed data    
        return processed_data
    except Exception:
        return quote_data
    

def convert_ticks_to_ohlc(data: pd.DataFrame, interval: int, require_validation: bool = False):
    """ This functions converts tick by ticks data into candle at the given interval.
    This functions expects the dataframe to have at least these two columns named 'datetime' and 'price',
    datetime column's data could be either epoch timestamp(ms) value or datetime64 type value.
    """
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