import gzip
import io
import zlib
import brotli
import zstandard
import pandas as pd



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
        market_start_time_obj = pd.to_datetime("09:14:00").time() 
        market_end_time_obj = pd.to_datetime("15:31:00").time()
        filtered_df = df[(df['time'] > market_start_time_obj) & (df['time'] < market_end_time_obj)]
        
        return filtered_df.drop('time', axis=1)
    except Exception as e:
        print(f"An error occurred: {e}")
        return df