from typing import Any, Union
import requests
from nsemine.utilities import  urls
import traceback



def get_request(url: str, headers: dict = None, params: Any = None, initial_url: str = None):
    try:
        if not headers:
            headers = urls.nifty_headers
        
        session = requests.Session()
        if initial_url:
            session.get(url=initial_url, headers=urls.default_headers)

        response = session.get(url=url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 200:
            return response
        return None
    
    except Exception as e:
        print(f'ERROR! - {e}\n')
        traceback.print_exc()


