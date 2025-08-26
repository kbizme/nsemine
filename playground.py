from nsemine import live, nse
from nsemine.utilities import urls
import requests, random

x = urls.get_nse_headers()
print(x)

x = live.get_stock_live_quotes('TCS')
print(x)