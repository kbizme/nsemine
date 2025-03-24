from nsemine.bin import cookie



####### NSEIndia #######
market_status = 'https://www.nseindia.com/api/marketStatus'
holiday_list = 'https://www.nseindia.com/api/holiday-master?type=trading'


nse_live_stock_analysis =  'https://www.nseindia.com/market-data/stocks-traded'
nse_live_stock_analysis_api = 'https://www.nseindia.com/api/live-analysis-stocksTraded'

# CSV
nse_equity_list = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'


####### NiftyIndices #######
nifty_index_maping = 'https://iislliveblob.niftyindices.com/assets/json/IndexMapping.json'




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
