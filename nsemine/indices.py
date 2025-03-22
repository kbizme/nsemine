import requests
from nsemine.utilities import utils


class NSEIndex:
    
    def __init__(self, index_name: str = 'NIFTY 50'):
        self.name = index_name
    

    def get_live_price(self):
        pass