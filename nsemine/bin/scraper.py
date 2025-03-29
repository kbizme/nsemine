from typing import  Union
import requests
from nsemine.utilities import  urls
from traceback import print_exc
import time


def get_request(url: str, headers: dict = None, params: dict = None, initial_url: str = None) -> Union[requests.Response, None]:
    try:
        if not headers:
            headers = urls.nifty_headers
        session = requests.Session()
        if initial_url:
            session.get(url=initial_url, headers=urls.default_headers, timeout=15)
        for retry_count in range(3):
            sleep_time = 2**retry_count+time.time()%1
            try:
                response = session.get(url=url, headers=headers, params=params, timeout=15)
                response.raise_for_status()
                if response.status_code == 200:
                    return response
                time.sleep(sleep_time)
            except requests.exceptions.Timeout as e:
                print(f"Request timed out: {e}\nRetrying...")
                time.sleep(sleep_time)
                continue
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error: {e}\nRetrying...")
                time.sleep(sleep_time)
                continue
            except requests.exceptions.HTTPError as e:
                print(f"HTTP error: {e}\nRetrying...")
                time.sleep(sleep_time)
                continue
            except requests.exceptions.RequestException as e:
                print(f"Network error during request: {e}\nRetrying...")
                time.sleep(sleep_time)
                continue
        print("Request failed after multiple retries.")
        return None
    except Exception as e:
        print(f'ERROR! - {e}\n')
        print_exc()
        return None


