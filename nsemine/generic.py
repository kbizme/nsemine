from nsemine import live, historical, fno, nse
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
            self.indices = self.quote_data.get('indices')
        else:
            print(f"The Symbol: {self.symbol} is not properly initialized.")


    def get_quotes(self, raw: bool = False) -> Union[dict, None]:
        """
        Fetches the live quote of the stock symbol.
        Args:
            raw (bool): Pass True, if you need the raw data without processing. Deafult is False.
        Returns:
            quote_data (dict, None) : Returns the raw data as dictionary if raw=True. By default, it returns cleaned and processed dictionary.
            Returns None if any error occurred.
        """
        try:
            return live.get_stock_live_quotes(stock_symbol=self.symbol, raw=raw)
        except Exception as e:
            print(f'ERROR! - {e}\n')
            traceback.print_exc()