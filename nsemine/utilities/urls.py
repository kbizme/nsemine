from random import choice


# HEADERS
# initial headers
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
first_boy = 'https://www.nseindia.com/get-quotes/equity?symbol=RELIANCE'

market_status = 'https://www.nseindia.com/api/marketStatus'
holiday_list = 'https://www.nseindia.com/api/holiday-master?type=trading'

nse_chart = 'https://charting.nseindia.com//Charts/ChartData/'
nse_chart_symbol = 'https://charting.nseindia.com//Charts/symbolhistoricaldata/'
nse_all_stocks_live = 'https://www.nseindia.com/api/live-analysis-stocksTraded'
al_indices = 'https://www.nseindia.com/api/allIndices'
nse_equity_quote = 'https://www.nseindia.com/api/quote-equity?symbol={}'
nse_equity_index = 'https://www.nseindia.com/api/equity-stockIndices'
ticks_chart = 'https://www.nseindia.com/api/chart-databyindex-dynamic?index={}EQN&type=symbol'
underlying = 'https://www.nseindia.com/api/underlying-information'
oi_spurts_underlying = 'https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings'

# SECURITIES ANALYSIS
new_year_high = 'https://www.nseindia.com/api/live-analysis-data-52weekhighstock'
new_year_low = 'https://www.nseindia.com/api/live-analysis-data-52weeklowstock'
pre_open = 'https://www.nseindia.com/api/market-data-pre-open?key={}'

# CSV
nse_equity_list = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'


####### NiftyIndices #######
nifty_index_maping = 'https://iislliveblob.niftyindices.com/assets/json/IndexMapping.json'
index_watch = 'https://iislliveblob.niftyindices.com/jsonfiles/LiveIndicesWatch.json'
live_index_watch_json = 'https://iislliveblob.niftyindices.com/jsonfiles/LiveIndicesWatch.json?{}&_='


####### NIFTY HEADERS #######
def get_nse_headers(profile: str = "api"):
    """
    Returns randomized headers for NSE requests.

    Args:
        profile (str): "page" → For HTML pages like first_boy
                       "api"  → For JSON/XHR API endpoints

    Returns:
        dict: Headers dictionary ready for requests
    """

    # User-Agent options with platform
    user_agents = [
        # Windows
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/139.0 Safari/537.36 OPR/120", "Windows"),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/139.0 Safari/537.36 Edg/139", "Windows"),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0", "Windows"),

        # macOS
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6) AppleWebKit/605.1.15 "
         "(KHTML, like Gecko) Version/17.0 Safari/605.1.15", "macOS"),
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/139.0 Safari/537.36 Edg/139", "macOS"),
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/139.0 Safari/537.36 Vivaldi/7.5", "macOS"),

        # Linux
        ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/139.0 Safari/537.36", "Linux"),
        ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0", "Linux"),
    ]

    # Accept-Language options
    accept_languages = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9",
        "en-IN,en;q=0.8",
        "en;q=0.9,fr;q=0.8,de;q=0.7,ro;q=0.6",
    ]

    # Accept header options for API
    accept_api = [
        "application/json, text/javascript, */*; q=0.01",
        "application/json, */*; q=0.01",
        "application/json, text/plain, */*; q=0.01"
    ]

    # Pick random User-Agent and platform
    user_agent, platform = choice(user_agents)

    # Determine sec-ch-ua based on browser type in User-Agent
    if "Edg" in user_agent:
        sec_ch_ua = '"Chromium";v="139", "Not.A/Brand";v="8", "Microsoft Edge";v="139"'
    elif "OPR" in user_agent or "Vivaldi" in user_agent:
        sec_ch_ua = '"Chromium";v="139", "Not.A/Brand";v="8", "Opera";v="120"'
    elif "Firefox" in user_agent:
        sec_ch_ua = '"Mozilla Firefox";v="141"'
    else:  # Chrome fallback
        sec_ch_ua = '"Chromium";v="139", "Not.A/Brand";v="8", "Chrome";v="139"'

    # Base headers
    headers = {
        "Accept-Language": choice(accept_languages),
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "User-Agent": user_agent,
        "sec-ch-ua": sec_ch_ua,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": platform,
        "Referer": "https://www.nseindia.com/",
        "X-Requested-With": "XMLHttpRequest"
    }

    # Profile-specific headers
    if profile == "page":
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/png,image/webp,*/*;q=0.8"
        headers["Upgrade-Insecure-Requests"] = "1"
    else:  # "api"
        headers["Accept"] = choice(accept_api)

    return headers