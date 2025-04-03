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

# SECURITIES ANALYSIS
new_year_high = 'https://www.nseindia.com/api/live-analysis-data-52weekhighstock'
new_year_low = 'https://www.nseindia.com/api/live-analysis-data-52weeklowstock'
pre_open = 'https://www.nseindia.com/api/market-data-pre-open?key={}'

# CSV
nse_equity_list = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'


####### NiftyIndices #######
nifty_index_maping = 'https://iislliveblob.niftyindices.com/assets/json/IndexMapping.json'
live_index_watch_json = 'https://iislliveblob.niftyindices.com/jsonfiles/LiveIndicesWatch.json?{}&_='


####### NIFTY HEADERS #######
def get_nse_headers():
    user_agents = [
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0", '"Windows"'),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36", '"Windows"'),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", '"Windows"'),
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15", '"macOS"'),
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36", '"macOS"'),
        ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36", '"Linux"'),
        ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0", '"Linux"'),
        ("Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko", '"Windows"'),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/129.0.0.0 Safari/537.36", '"Windows"'),
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Safari/537.36", '"macOS"'),
    ]

    accept_languages = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9",
        "en-IN,en;q=0.8",
        "en;q=0.9,fr;q=0.8,de;q=0.7,ro;q=0.6",
    ]

    user_agent, platform = choice(user_agents)

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/png,image/webp,*/*;q=0.8",
        "Accept-language": choice(accept_languages),
        'Accept-Encoding': 'gzip, deflate, br, zstd', 
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "User-Agent": user_agent,
        "sec-ch-ua": '"Chromium";v="129", "Not.A/Brand";v="8", "Microsoft Edge";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": platform,
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "X-Requested-With": "XMLHttpRequest"
    }
    if "Edge" not in user_agent:
        headers["sec-ch-ua"] = '"Chromium";v="129", "Not.A/Brand";v="8", "Chrome";v="129"'
    return headers
