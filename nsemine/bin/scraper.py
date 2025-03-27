from typing import  Union
from requests import Session, Response
from nsemine.utilities import  urls
from time import time
from traceback import print_exc



def get_request(url: str, headers: dict = None, params: dict = None, initial_url: str = None) -> Union[Response, None]:
    try:
        if not headers:
            headers = urls.nifty_headers
        
        session = Session()
        if initial_url:
            session.get(url=initial_url, headers=urls.default_headers, timeout=30)
        for retry_count in range(3):
            try:
                response = session.get(url=url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                if response.status_code == 200:
                    return response
                time.sleep(2**retry_count+time()%1)
            except Exception:
                time.sleep(2**retry_count+time()%1)
                continue
        return None
    
    except Exception as e:
        print(f'ERROR! - {e}\n')
        print_exc()


