from nsemine.bin import cookie



####### NSEIndia #######
market_status = 'https://www.nseindia.com/api/marketStatus'
holiday_list = 'https://www.nseindia.com/api/holiday-master?type=trading'

nse_chart_data = 'https://charting.nseindia.com//Charts/ChartData/'

nse_all_stocks_live =  'https://www.nseindia.com/market-data/stocks-traded'
nse_all_stocks_live_api = 'https://www.nseindia.com/api/live-analysis-stocksTraded'

al_indices_live_api = 'https://www.nseindia.com/api/allIndices'
al_indices_live = 'https://www.nseindia.com/market-data/live-market-indices'  

nse_equity_quote_api = 'https://www.nseindia.com/api/quote-equity?symbol={}'
nse_equity_quote = 'https://www.nseindia.com/get-quotes/equity?symbol={}'

nse_equity_index_api = 'https://www.nseindia.com/api/equity-stockIndices'
nse_equity_index = 'https://www.nseindia.com/market-data/live-equity-market'

stock_ticks_api = 'https://www.nseindia.com/api/chart-databyindex-dynamic?index={}EQN&type=symbol'

# SECURITIES ANALYSIS
new_year_high = 'https://www.nseindia.com/market-data/52-week-high-equity-market'
new_year_low = 'https://www.nseindia.com/market-data/52-week-low-equity-market'
new_year_high_api = 'https://www.nseindia.com/api/live-analysis-data-52weekhighstock'
new_year_low_api = 'https://www.nseindia.com/api/live-analysis-data-52weeklowstock'

# CSV
nse_equity_list = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'


####### NiftyIndices #######
nifty_index_maping = 'https://iislliveblob.niftyindices.com/assets/json/IndexMapping.json'
live_index_watch_json = 'https://iislliveblob.niftyindices.com/jsonfiles/LiveIndicesWatch.json?{}&_='




# HEADERS
# initial headers
default_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, br, zstd', 
    'Accept': '*/*', 
    "Referer": "https://www.nseindia.com/",
}

nifty_headers = {
            "Accept": "text/html,application/xhtml+xml,text/csv,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-language": "en-US,en;q=0.9,en-IN;q=0.8,en-GB;q=0.7",
            'Connection': 'keep-alive',
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }
