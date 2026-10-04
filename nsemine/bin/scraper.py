import time
import random
import asyncio
from curl_cffi import requests
from nsemine.utilities import urls
from nsemine.bin import auth


REQUEST_TIMEOUT = 15
MAX_RETRIES = 3

# Synchronous Global Session
SESSION = requests.Session(impersonate="chrome")
CURRENT_PROFILE_IDX = 0




def _refresh_session_token() -> dict | None:
    """Synchronous session refresh."""
    try:
        SESSION.cookies.clear()
        page_headers = urls.get_nse_headers(profile="page", profile_idx=CURRENT_PROFILE_IDX)
        response = SESSION.get(url=urls.first_boy, headers=page_headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        session_token = SESSION.cookies.get_dict()
        if session_token:
            auth.set_session_token(session_token)
            return session_token

    except Exception as e:
        print(f"Failed to refresh NSE session token: {e}")
        return None



async def _async_refresh_session_token(async_session: requests.AsyncSession) -> dict | None:
    """Asynchronous session refresh (Non-blocking I/O)."""
    try:
        async_session.cookies.clear()
        page_headers = urls.get_nse_headers(profile="page", profile_idx=CURRENT_PROFILE_IDX)
        response = await async_session.get(url=urls.first_boy, headers=page_headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        session_token = async_session.cookies.get_dict()
        if session_token:
            auth.set_session_token(session_token)
            return session_token

    except Exception as e:
        print(f"Failed to refresh NSE session token asynchronously: {e}")
        return None



def get_request(url: str, headers: dict | None = None, params: dict | None = None) -> requests.Response | None:
    try:
        if headers is None:
            headers = urls.get_nse_headers(profile="api", profile_idx=CURRENT_PROFILE_IDX)

        session_token = auth.get_session_token()

        if not session_token:
            session_token = _refresh_session_token()
            if not session_token:
                raise ValueError("Failed to establish session with NSE.")

        SESSION.cookies.update(session_token)

        for retry_count in range(MAX_RETRIES):
            try:
                response = SESSION.get(
                    url=url, 
                    headers=headers, 
                    params=params, 
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()

                # persist updated telemetry cookies to SQLite
                updated_cookies = SESSION.cookies.get_dict()
                if updated_cookies:
                    auth.set_session_token(updated_cookies)

                return response

            except requests.errors.RequestsError as e:
                status_code = getattr(e.response, "status_code", None) if hasattr(e, "response") else None
                
                if status_code in (401, 403):
                    print(f"NSE session expired/blocked ({status_code}). Refreshing session...")
                    try:
                        session_token = _refresh_session_token()
                        if session_token:
                            SESSION.cookies.update(session_token)
                            continue
                    except Exception as refresh_error:
                        print(f"Dynamic token refresh failed: {refresh_error}")
                
                print(f"Network exception (Retry {retry_count + 1}/{MAX_RETRIES}): {e}")

            time.sleep((2 ** retry_count) + random.uniform(0.5, 1.5))

        print("Data extraction terminated: Maximum retries reached.")
        return None

    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
        return None



async def async_get_request(
        url: str, 
        headers: dict | None = None, 
        params: dict | None = None,
        session: requests.AsyncSession | None = None
    ) -> requests.Response | None:
    if headers is None:
        headers = urls.get_nse_headers(profile="api", profile_idx=CURRENT_PROFILE_IDX)

    session_token = auth.get_session_token()

    # shared or standalone async session handler
    close_session = False
    if session is None:
        session = requests.AsyncSession(impersonate="chrome")
        close_session = True

    try:
        if not session_token:
            session_token = await _async_refresh_session_token(session)
            if not session_token:
                return None

        session.cookies.update(session_token)

        for retry_count in range(MAX_RETRIES):
            try:
                response = await session.get(
                    url=url, 
                    headers=headers, 
                    params=params, 
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()

                updated_cookies = session.cookies.get_dict()
                if updated_cookies:
                    auth.set_session_token(updated_cookies)

                return response

            except requests.errors.RequestsError as e:
                status_code = getattr(e.response, "status_code", None) if hasattr(e, "response") else None

                if status_code in (401, 403):
                    session_token = await _async_refresh_session_token(session)
                    if session_token:
                        session.cookies.update(session_token)
                        continue

            await asyncio.sleep((2 ** retry_count) + random.uniform(0.5, 1.5))

        return None
    finally:
        if close_session:
            await session.close()
            
            