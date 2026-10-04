# HEADERS & ENDPOINTS
default_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, br, zstd', 
    'Accept': '*/*', 
    "Referer": "https://www.nseindia.com/",
}

####### NSEIndia #######
    
most_active = 'live-analysis-most-active-securities?index=volume'
most_valued = 'live-analysis-most-active-securities?index=value'
advance = 'live-analysis-advance'
decline = 'live-analysis-decline'
unchanged = 'live-analysis-unchanged'
all_gainers = 'live-analysis-variations?index=gainers'
all_losers = 'live-analysis-variations?index=loosers'

base_nse_api = 'https://www.nseindia.com/api/'
next_api_f = 'https://www.nseindia.com/api/NextApi/apiClient?functionName={}'
first_boy = 'https://www.nseindia.com/get-quote/equity/RELIANCE/Reliance-Industries-Limited'

market_status = 'https://www.nseindia.com/api/marketStatus'
holiday_list = 'https://www.nseindia.com/api/holiday-master?type=trading'

nse_chart_url = 'https://charting.nseindia.com/v1/charts/symbolHistoricalData'
search_token_url = 'https://charting.nseindia.com/v1/exchanges/symbolsDynamic'

nse_all_stocks_live = 'https://www.nseindia.com/api/live-analysis-stocksTraded'
al_indices = 'https://www.nseindia.com/api/allIndices'
nse_equity_quote = 'https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi?functionName=getSymbolData&marketType=N&series={}&symbol={}'
ticks_chart = 'https://www.nseindia.com/api/chart-databyindex-dynamic?index={}EQN&type=symbol'
underlying = 'https://www.nseindia.com/api/underlying-information'
oi_spurts_underlying = 'https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings'

# DERIVATIVES
stk_opt_url = 'https://www.nseindia.com/api/option-chain-contract-info?symbol={}'   

# SECURITIES ANALYSIS
new_year_high = 'https://www.nseindia.com/api/live-analysis-data-52weekhighstock'
new_year_low = 'https://www.nseindia.com/api/live-analysis-data-52weeklowstock'
pre_open = 'https://www.nseindia.com/api/market-data-pre-open?key={}'

# CSV
nse_equity_list = 'https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv'
nse_sme_stocks = 'https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv'

# Archives
full_bhavcopy_cm = 'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{session_date}.csv' # 01102025
historic_bhavcopy_cm = 'https://www.nseindia.com/api/reports?archives=%5B%7B%22name%22%3A%22Full%20Bhavcopy%20and%20Security%20Deliverable%20data%22%2C%22type%22%3A%22daily-reports%22%2C%22category%22%3A%22capital-market%22%2C%22section%22%3A%22equities%22%7D%5D&date={session_date}&type=equities&mode=single'

####### NiftyIndices #######
nifty_index_maping = 'https://iislliveblob.niftyindices.com/assets/json/IndexMapping.json'
index_watch = 'https://iislliveblob.niftyindices.com/jsonfiles/LiveIndicesWatch.json'
live_index_watch_json = 'https://www.nseindia.com/api/allIndices'
live_indices = 'https://www.nseindia.com/api/NextApi/apiClient?functionName=getIndexData&&type=All'

######## Index Constituents #######
nse_equity_index = 'https://www.nseindia.com/api/NextApi/apiClient/indexTrackerApi?functionName=getConstituents&&index={}&&noofrecords=0'


####### CHROME PROFILES #######
CHROME_PROFILES = [
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "platform": '"Windows"',
        "sec_ch_ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"'
    },
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "platform": '"Windows"',
        "sec_ch_ua": '"Chromium";v="133", "Not:A-Brand";v="24", "Google Chrome";v="133"'
    },
    {
        "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "platform": '"Linux"',
        "sec_ch_ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"'
    }
]

ACCEPT_API_VARIANTS = [
    "application/json, text/javascript, */*; q=0.01",
    "application/json, text/plain, */*",
    "*/*"
]


def get_nse_headers(profile: str = "api", profile_idx: int = 0, referer: str | None = None) -> dict:
    """
    Generates strict Chrome headers matching curl_cffi's TLS fingerprint.
    Uses profile_idx to maintain User-Agent consistency across authentication and requests.
    Allows optional custom referer overriding.
    """
    selected = CHROME_PROFILES[profile_idx % len(CHROME_PROFILES)]
    
    headers = {
        "User-Agent": selected["ua"],
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "sec-ch-ua": selected["sec_ch_ua"],
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": selected["platform"],
    }

    if profile == "page":
        headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": referer or "https://www.google.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1"
        })
    else:  # "api" profile
        headers.update({
            "Accept": ACCEPT_API_VARIANTS[0],
            "Referer": referer or "https://www.nseindia.com/market-data/live-equity-market",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        })

    return headers