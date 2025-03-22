from bin import scraper
from utilities import urls
from typing import Union
import json
import pandas as pd



def get_all_indices_names() -> Union[pd.DataFrame, None]:
    try:
        resp = scraper.get_request(url=urls.nifty_index_maping)
        if resp:
            data = resp.text
            if data.startswith('\ufeff'):
                data = json.loads(data[1:])
            df = pd.DataFrame(data)
            df.columns = ['trading_index', 'full_name']
            return df
    except Exception as e:
        print('Error Occurred in get_all_indices_names():', e)
