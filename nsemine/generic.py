from nsemine.bin import scraper
from nsemine.utilities import urls, utils
from typing import Union
import json
import pandas as pd
import traceback
from io import StringIO
from datetime import datetime



class NSEStock:
    """
    This class provides methods to fetch various data related to a specific stock.
    """
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quote_data = self.get_quotes()
        if self.quote_data:
            self.name = self.quote_data.get('name')
            self.industry = self.quote_data.get('industry')
            self.derivatives = self.quote_data.get('derivatives')
            self.series = self.quote_data.get('series')
            self.date_of_listing = self.quote_data.get('date_of_listing')
            self.last_updated = self.quote_data.get('last_updated')
            self.trading_status = self.quote_data.get('trading_status')
            self.number_of_shares = self.quote_data.get('number_of_shares')
            self.face_value = self.quote_data.get('face_value')
        else:
            print(f"The Symbol: {self.symbol} is not properly initialized.")


    def get_quotes(self, raw: bool = False) -> Union[dict, pd.DataFrame, None]:
        """
        Fetches the live quote of the stock symbol.
        Args:
            raw (bool): Pass True, if you need the raw data without processing. Deafult is False.
        Returns:
            dict : Returns the raw data as dictionary if raw=True.
            DataFrame : Returns Pandas DataFrame object if raw=False.
            None : Returns None if any error occurred.
        """
        try:
            resp = scraper.get_request(url=urls.nse_equity_quote_api.format(self.symbol), initial_url=urls.nse_equity_quote.format(self.symbol))
            if resp:
                data = resp.json()
                if raw:
                    return data
                return utils.process_stock_quote_data(quote_data=data)
            
        except Exception as e:
            print(f'ERROR! - {e}\n')
            traceback.print_exc()