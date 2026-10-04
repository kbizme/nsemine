import asyncio
import pandas as pd
import time
from curl_cffi import requests
from nsemine.bin import scraper
from nsemine.utilities import urls, utils



async def _prime_nse_session(session: requests.AsyncSession, profile_idx: int = 0) -> bool:
    """Fetches base cookies from NSE homepage sequentially using document page headers."""
    try:
        headers = urls.get_nse_headers(profile="page", profile_idx=profile_idx)
        resp = await scraper.async_get_request(
            url="https://www.nseindia.com", 
            session=session, 
            headers=headers
        )
        if resp and resp.status_code == 200:
            await asyncio.sleep(0.5)
            session._last_primed = time.time() 
            return True
        
    except Exception:
        pass
    return False



async def _fetch_single_quote_task(
    session: requests.AsyncSession, 
    symbol: str, 
    series: str, 
    semaphore: asyncio.Semaphore,
    refresh_lock: asyncio.Lock,
    profile_idx: int = 0
) -> tuple[str, dict | None]:
    """Internal worker with concurrency throttling and locked token refresh fallback."""
    clean_symbol = symbol.replace('&', '%26')
    url = urls.nse_equity_quote.format(series, clean_symbol)
    quote_referer = f"https://www.nseindia.com/get-quotes/equity?symbol={clean_symbol}"
    
    # use API profile with stock-specific referer
    headers = urls.get_nse_headers(profile="api", profile_idx=profile_idx, referer=quote_referer)
    
    async with semaphore:
        try:
            resp = await scraper.async_get_request(url=url, session=session, headers=headers)
            
            if resp is None or resp.status_code in (401, 403):
                async with refresh_lock:
                    # only re-prime if another task hasn't primed it in the last 5 seconds
                    last_primed = getattr(session, '_last_primed', 0)
                    if time.time() - last_primed > 5.0:
                        await _prime_nse_session(session, profile_idx=profile_idx)
                
                # retry the request after the lock is released and session is fresh
                resp = await scraper.async_get_request(url=url, session=session, headers=headers)

            if resp and resp.status_code == 200:
                return symbol, resp.json()
        except Exception:
            pass
        return symbol, None


async def async_get_multiple_stock_quotes(
    symbols: list | set | tuple, 
    series: str = 'EQ', 
    raw: bool = False, 
    df: bool = True,
    max_concurrent: int = 15,
    profile_idx: int = 0
) -> pd.DataFrame | dict:
    
    symbols_list = list(symbols)
    semaphore = asyncio.Semaphore(max_concurrent)
    refresh_lock = asyncio.Lock() 
    
    async with requests.AsyncSession(impersonate="chrome") as session:
        session._last_primed = 0 
        
        primed = await _prime_nse_session(session, profile_idx=profile_idx)
        if not primed:
            await asyncio.sleep(1.0)
            await _prime_nse_session(session, profile_idx=profile_idx)

        tasks = [
            _fetch_single_quote_task(session, sym, series, semaphore, refresh_lock, profile_idx=profile_idx) 
            for sym in symbols_list
        ]
        results = await asyncio.gather(*tasks)

    raw_map = {symbol: raw_json for symbol, raw_json in results}

    if raw:
        return raw_map

    processed_map = {}
    processed_list = []

    for symbol in symbols_list:
        raw_json = raw_map.get(symbol)
        if raw_json:
            processed = utils.process_stock_quote_data(raw_json)
            if isinstance(processed, dict) and 'symbol' in processed:
                if 'volume' in processed and processed['volume'] is not None:
                    processed['volume'] = int(processed['volume'])
                processed_map[symbol] = processed
                processed_list.append(processed)
            else:
                processed_map[symbol] = None
                processed_list.append({'symbol': symbol})
        else:
            processed_map[symbol] = None
            processed_list.append({'symbol': symbol})

    if not df:
        return processed_map

    df_res = pd.DataFrame(processed_list)

    if 'volume' in df_res.columns:
        df_res['volume'] = df_res['volume'].astype('Int64')

    return df_res
