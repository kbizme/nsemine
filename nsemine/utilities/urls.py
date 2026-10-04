# ENDPOINTS

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
all_indices = 'https://www.nseindia.com/api/allIndices'
nse_equity_quote = 'https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi?functionName=getSymbolData&marketType=N&series={}&symbol={}'
ticks_chart = 'https://www.nseindia.com/api/chart-databyindex-dynamic?index={}EQN&type=symbol'
underlying = 'https://www.nseindia.com/api/underlying-information'

# DERIVATIVES
stk_opt_url = 'https://www.nseindia.com/api/option-chain-contract-info?symbol={}'
option_chain = "https://www.nseindia.com/api/option-chain-v3"
oi_spurts_underlying = 'https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings'


# SECURITIES ANALYSIS
new_year_high = 'https://www.nseindia.com/api/live-analysis-data-52weekhighstock'
new_year_low = 'https://www.nseindia.com/api/live-analysis-data-52weeklowstock'
pre_open = 'https://www.nseindia.com/api/market-data-pre-open?key={}'


# CSV
nse_equity_list = 'https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv'
nse_sme_stocks = 'https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv'


# Archives
full_bhavcopy_cm = 'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{session_date}.csv'  # 01102025
historic_bhavcopy_cm = 'https://www.nseindia.com/api/reports?archives=%5B%7B%22name%22%3A%22Full%20Bhavcopy%20and%20Security%20Deliverable%20data%22%2C%22type%22%3A%22daily-reports%22%2C%22category%22%3A%22capital-market%22%2C%22section%22%3A%22equities%22%7D%5D&date={session_date}&type=equities&mode=single'


####### NiftyIndices #######
nifty_index_maping = 'https://iislliveblob.niftyindices.com/assets/json/IndexMapping.json'
index_watch = 'https://iislliveblob.niftyindices.com/jsonfiles/LiveIndicesWatch.json'
live_index_watch_json = 'https://www.nseindia.com/api/allIndices'
live_indices = 'https://www.nseindia.com/api/NextApi/apiClient?functionName=getIndexData&type=All'


######## Index Constituents #######
nse_equity_index = 'https://www.nseindia.com/api/NextApi/apiClient/indexTrackerApi?functionName=getConstituents&index={}&noofrecords=0'


