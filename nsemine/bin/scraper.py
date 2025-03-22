from typing import Any, Union
import requests
from nsemine.utilities import  utils



def get_request(url: str, params: Any = None):
    try:
        response = requests.get(url=url, headers=utils.api_headers, params=params)
        response.raise_for_status()
        if response.status_code == 200:
            return response
        return None
    
    except Exception as e:
        print('Error while making the request to nse website:', e)()


