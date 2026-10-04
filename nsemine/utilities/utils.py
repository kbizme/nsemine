import traceback
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time as time_obj


def process_stock_quote_data(quote_data: dict) -> dict:
    try:
        quote_data = quote_data.get('equityResponse')[0]
        processed_data = dict()

        _metadata = quote_data.get('metaData')
        if _metadata:
            symbol = _metadata.get('symbol')
            name = _metadata.get('companyName')
            series = _metadata.get('series')
            open = _metadata.get('open')
            high = _metadata.get('dayHigh')
            low = _metadata.get('dayLow')
            close = _metadata.get('closePrice')
            previous_close = _metadata.get('previousClose')
            change = _metadata.get('change')
            change_percentage = _metadata.get('pChange')

            processed_data['symbol'] = symbol
            processed_data['name'] = name
            processed_data['series'] = series
            processed_data['open'] = open
            processed_data['high'] = high
            processed_data['low'] = low
            processed_data['close'] = close
            processed_data['previous_close'] = previous_close
            processed_data['change'] = change
            processed_data['changepct'] = change_percentage
            
        _sec_info = quote_data.get('secInfo')
        if _sec_info:
            try:
                date_of_listing = datetime.strptime(_sec_info.get('listingDate'), '%d-%b-%Y %H:%M:%S').date()
                last_updated = datetime.strptime(quote_data.get('lastUpdateTime'), '%d-%b-%Y %H:%M:%S') or None
                sector = _sec_info.get('sector')
                industry = _sec_info.get('industryInfo')
                processed_data['date_of_listing'] = date_of_listing
                processed_data['datetime'] = last_updated
                processed_data['sector'] = sector
                processed_data['industry'] = industry
                
            except Exception:
                pass        

        _price_info = quote_data.get('priceInfo')
        if _price_info:
            circuits = _price_info.get('priceBand')
            circuits_price = circuits.split('-') if circuits else None
            year_high = _price_info.get('yearHigh')
            year_low = _price_info.get('yearLow')
            if circuits_price:
                processed_data['upper_circuit'] = float(circuits_price[0])
                processed_data['lower_circuit'] = float(circuits_price[1])
            processed_data['year_high'] = year_high
            processed_data['year_low'] = year_low
            
        _trade_info = quote_data.get('tradeInfo')
        if _trade_info:
            volume = _trade_info.get('totalTradedVolume') or _trade_info.get('quantitytraded')  
            processed_data['volume'] = volume
        
        # close price fallback during market hours
        if not processed_data.get('close'):
            processed_data['close'] = processed_data.get('previous_close', 0) + processed_data.get('change', 0)
            
        return processed_data
    except Exception:
        return quote_data


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

    
def process_aud(df:pd.DataFrame) -> pd.DataFrame:
    try:
        df = df[['symbol', 'series', 'lastPrice', 'previousClose', 'change', 'pchange', 'totalTradedVolume', 'totalTradedValue', 'totalMarketCap']].copy()
        df.rename(axis=1, inplace=True, mapper={'lastPrice':'close', 'previousClose': 'previous_close', 'pchange':'changepct', 'totalTradedVolume': 'volume', 'totalTradedValue': 'traded_value_cr','totalMarketCap': 'market_cap_cr'})
        df['change'] = np.round(df['change'], 2)
        df['changepct'] = np.round(df['changepct'], 2)
        df['market_cap_cr'] = np.round(df['market_cap_cr'], 2)
        df['traded_value_cr'] = np.round(df['traded_value_cr'], 2)
        df['volume'] = np.int64(df['volume'] * 1_00000)
        return df
    except:
        return df


def remove_pre_and_post_market_prices_from_df(df: pd.DataFrame, unit: str = 'ms', interval: int = 3) -> pd.DataFrame:
    try:
        if not isinstance(df, pd.DataFrame):
            return df
        df['temp_datetime'] = df['datetime']
        if not pd.api.types.is_datetime64_dtype(df['datetime']):
            df['temp_datetime'] = pd.to_datetime(df['datetime'], unit=unit)

        df['time'] = df['temp_datetime'].dt.time
        start_time_obj = pd.to_datetime("09:15:00").time()
        end_time_obj = pd.to_datetime("15:30:00").time()
        filtered_df = df[(df['time'] >= start_time_obj) & (df['time'] < end_time_obj)]
        return filtered_df.drop(columns=['time', 'temp_datetime'], axis=0)
    except Exception as e:
        print(f"Error occurred while removing pre and post market prices: {e}")
        raise e


def process_historical_chart_response(df: pd.DataFrame, interval: str, start_datetime: datetime, end_datetime: datetime) -> pd.DataFrame:
    try:
        df = df[['time', 'open', 'high', 'low', 'close', 'volume']].copy()
        
        df.rename(columns={'time': 'datetime'}, inplace=True)
        
        if interval in ('D', 'W', 'M'):
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            return df

        df = remove_pre_and_post_market_prices_from_df(df=df.copy())
        try:
            minutes = int(interval) if str(interval) == '1' else 5
            time_offset_seconds = (minutes - 1) * 60 + 59
        except Exception:
            time_offset_seconds = 0

        df['datetime'] = df['datetime'] - time_offset_seconds * 1000
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df['datetime'] = df['datetime'].apply(
            lambda dt: dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
            if dt.second > 1 else dt.replace(second=0, microsecond=0)
        )
        return df
    except Exception as e:
        print('Exception in process_historical_chart_response', e)
        traceback.print_exc()
        return None



def process_movers_data(data):
    try:
        df = pd.DataFrame(data['data'])
        df['change'] = round(df['ltp'] - df['prev_price'], 2)
        df = df[['symbol', 'series', 'open_price', 'high_price', 'low_price', 'ltp', 
                'prev_price', 'change', 'perChange', 'trade_quantity', 'turnover']]
        df.rename(columns={'open_price': 'open', 'high_price': 'high', 'low_price': 'low', 'ltp': 'close',
                        'prev_price': 'previous_close', 'perChange': 'changepct', 'trade_quantity': 'volume'}, inplace=True)
        df['turnover'] = round(df['turnover'] * 1_00_000, 2)
        return df
    except:
        return data
    



def process_option_chain_response(raw_data: dict) -> pd.DataFrame:
    """
    Parses and flattens NSE option chain v3 raw response into a proper Pandas DataFrame.
    """
    if not raw_data or "records" not in raw_data or "data" not in raw_data["records"]:
        return pd.DataFrame()

    records_data = raw_data["records"].get("data", [])
    rows = []

    for item in records_data:
        strike_price = item.get("strikePrice")
        expiry_date = item.get("expiryDates")

        ce_data = item.get("CE") or {}
        pe_data = item.get("PE") or {}

        spot_price = float(
            ce_data.get("underlyingValue") or pe_data.get("underlyingValue") or 0.0
        )

        def extract_option_data(opt_dict: dict, prefix: str) -> dict:
            return {
                f"{prefix}_oi": int(opt_dict.get("openInterest") or 0),
                f"{prefix}_oi_change": int(opt_dict.get("changeinOpenInterest") or 0),
                f"{prefix}_oi_changepct": float(opt_dict.get("pchangeinOpenInterest") or 0.0),
                f"{prefix}_volume": int(opt_dict.get("totalTradedVolume") or 0),
                f"{prefix}_iv": float(opt_dict.get("impliedVolatility") or 0.0),
                f"{prefix}_ltp": float(opt_dict.get("lastPrice") or 0.0),
                f"{prefix}_change": float(opt_dict.get("change") or 0.0),
                f"{prefix}_changepct": float(opt_dict.get("pChange") or 0.0),
                f"{prefix}_top_bid_price": float(opt_dict.get("buyPrice1") or 0.0),
                f"{prefix}_top_bid_qty": int(opt_dict.get("buyQuantity1") or 0),
                f"{prefix}_top_ask_price": float(opt_dict.get("sellPrice1") or 0.0),
                f"{prefix}_top_ask_qty": int(opt_dict.get("sellQuantity1") or 0),
                f"{prefix}_total_bid_qty": int(opt_dict.get("totalBuyQuantity") or 0),
                f"{prefix}_total_ask_qty": int(opt_dict.get("totalSellQuantity") or 0),
                f"{prefix}_symbol": opt_dict.get("identifier"),
            }

        row = {
            "expiry_date": expiry_date,
            "spot_price": spot_price,
            "strike_price": strike_price,
        }
        row.update(extract_option_data(ce_data, "ce"))
        row.update(extract_option_data(pe_data, "pe"))

        rows.append(row)

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    int_cols = [
        col for col in df.columns 
        if any(keyword in col for keyword in ["_oi", "_volume", "_qty"])
    ]
    df[int_cols] = df[int_cols].astype("int64")

    # vectorized rounding of all float columns to 2 decimal places
    float_cols = df.select_dtypes(include=["float64", "float32"]).columns
    df[float_cols] = df[float_cols].round(2)

    return df

