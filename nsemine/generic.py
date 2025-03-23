from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
import json
import pandas as pd
import traceback


def get_all_indices_names() -> Union[pd.DataFrame, None]:
    """
    This functions fetches all the available indices at NSE Exchange.
    Returns:
        df (DataFrame) : Pandas DataFrame containing all the nse indices names.

        Returns None, if any error occurred.
    """
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
        print(f'ERROR! - {e}\n')
        traceback.print_exc()

