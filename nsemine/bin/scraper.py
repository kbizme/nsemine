import asyncio
import logging
import random
import time
import threading
from curl_cffi import requests
from nsemine.utilities import urls
from nsemine.bin import auth, header 



LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15
MAX_RETRIES = 3  
DEFAULT_IMPERSONATE = "chrome133a"
HTTP_VERSION = "v1"
SESSION_MAX_AGE_MINUTES = 60
MAX_BACKOFF_SECONDS = 8.0
MAX_SERVER_BACKOFF_SECONDS = 30.0

SESSION: requests.Session | None = None
CURRENT_PROFILE_IDX = 0

_SESSION_LOCAL = threading.local()
_SESSION_REFRESH_LOCK = threading.Lock()
_ASYNC_REFRESH_TASKS = {}
_ASYNC_REFRESH_TASKS_LOCK = threading.Lock()


_RETRYABLE_STATUS_CODES = {408, 425, 500, 502, 503, 504}
_SESSION_REFRESH_STATUS_CODES = {401, 403}






def _close_sync_session(session: requests.Session | None) -> None:
    if session is None:
        return
    try:
        session.close()
    except Exception:
        LOGGER.debug("Failed to close NSE sync session", exc_info=True)


def _get_sync_session(force_new: bool = False) -> requests.Session:
    """
    Return a session private to the current worker thread.

    A single curl_cffi session is not shared across unrelated threads. This avoids
    concurrent cookie mutation and socket-pool races while preserving connection
    reuse for sequential requests made by the same thread.
    """
    global SESSION

    session = getattr(_SESSION_LOCAL, "session", None)
    if force_new and session is not None:
        _close_sync_session(session)
        session = None
        _SESSION_LOCAL.session = None
        _SESSION_LOCAL.seeded = False

    if session is None:
        session = requests.Session(
            impersonate=DEFAULT_IMPERSONATE,
            http_version=HTTP_VERSION,
        )
        _SESSION_LOCAL.session = session
        _SESSION_LOCAL.seeded = False

    SESSION = session
    return session


def _seed_sync_session(session: requests.Session, session_token: dict | None) -> None:
    """Seed a newly-created session once; do not clear cookies on every request."""
    if getattr(_SESSION_LOCAL, "seeded", False):
        return
    if session_token:
        session.cookies.update(session_token)
    _SESSION_LOCAL.seeded = True


def _create_async_session() -> requests.AsyncSession:
    return requests.AsyncSession(
        impersonate=DEFAULT_IMPERSONATE,
        http_version=HTTP_VERSION,
    )


def _refresh_session_token(force: bool = False) -> dict | None:
    """Bootstrap a fresh NSE session and persist its cookies.

    The refresh lock prevents a burst of concurrent synchronous callers from all
    rebuilding the NSE session at once. A forced refresh ignores the cached token.
    """
    with _SESSION_REFRESH_LOCK:
        if not force:
            cached = auth.get_session_token(max_age_minutes=SESSION_MAX_AGE_MINUTES)
            if cached:
                return cached

        session = _get_sync_session(force_new=True)
        session.cookies.clear()
        page_headers = header.get_nse_headers(profile="page", profile_idx=CURRENT_PROFILE_IDX)

        try:
            response = session.get(
                url=urls.first_boy,
                headers=page_headers,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            session_token = session.cookies.get_dict()
            if session_token:
                auth.set_session_token(session_token)
                _SESSION_LOCAL.seeded = True
                return session_token

            LOGGER.warning("NSE session bootstrap returned no cookies.")
            return None
        except Exception as e:
            LOGGER.warning("Failed to refresh NSE session token: %s", e)
            return None


async def _async_refresh_session_token(
    async_session: requests.AsyncSession,
    force: bool = False,
) -> dict | None:
    """
    Bootstrap an NSE session with per-event-loop single-flight refresh.

    Only one refresh task is created for a given running event loop at a time.
    Concurrent callers await the same result and then apply the returned cookie
    bundle to their own session.
    """
    loop = asyncio.get_running_loop()

    with _ASYNC_REFRESH_TASKS_LOCK:
        task = _ASYNC_REFRESH_TASKS.get(loop)
        if task is None or task.done():
            task = loop.create_task(
                _async_refresh_session_token_impl(
                    async_session=async_session,
                    force=force,
                )
            )
            _ASYNC_REFRESH_TASKS[loop] = task

    try:
        return await asyncio.shield(task)
    finally:
        if task.done():
            with _ASYNC_REFRESH_TASKS_LOCK:
                if _ASYNC_REFRESH_TASKS.get(loop) is task:
                    _ASYNC_REFRESH_TASKS.pop(loop, None)



async def _async_refresh_session_token_impl(
    async_session: requests.AsyncSession,
    force: bool = False,
) -> dict | None:
    """Perform the actual NSE session bootstrap for the single-flight task."""
    if not force:
        cached = auth.get_session_token(max_age_minutes=SESSION_MAX_AGE_MINUTES)
        if cached:
            return cached

    try:
        async_session.cookies.clear()
        page_headers = header.get_nse_headers(
            profile="page",
            profile_idx=CURRENT_PROFILE_IDX,
        )

        response = await async_session.get(
            url=urls.first_boy,
            headers=page_headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        session_token = async_session.cookies.get_dict()
        if session_token:
            auth.set_session_token(session_token)
            return session_token

        LOGGER.warning("NSE async session bootstrap returned no cookies.")
        return None
    except Exception as e:
        LOGGER.warning(
            "Failed to refresh NSE session token asynchronously: %s",
            e,
        )
        return None


def _is_akamai_html_block(response: requests.Response) -> bool:
    """
    Detect an HTML edge/block response masquerading as an API success.

    This intentionally classifies the response rather than attempting to bypass or
    solve the edge challenge. Callers can then stop/rebootstrap in a bounded way.
    """
    content_type = response.headers.get("content-type", "").lower()
    if "text/html" not in content_type:
        return False

    text_sample = response.text[:1000].lower()
    markers = (
        "<html",
        "<!doctype html",
        "access denied",
        "request unsuccessful",
        "akamai",
        "bot manager",
        "challenge",
        "forbidden",
    )
    return any(marker in text_sample for marker in markers)


def _classify_response(response: requests.Response) -> str:
    status_code = response.status_code

    if 200 <= status_code < 300:
        return "html_block" if _is_akamai_html_block(response) else "success"
    if status_code in _SESSION_REFRESH_STATUS_CODES:
        return "session_or_access_block"
    if status_code == 429:
        return "rate_limited"
    if status_code in _RETRYABLE_STATUS_CODES or status_code >= 500:
        return "transient_http"
    return "http_error"



def _is_transport_error(exc: Exception) -> bool:
    message = str(exc).lower()
    markers = (
        "curl: (7)",
        "curl: (18)",
        "curl: (28)",
        "curl: (35)",
        "curl: (52)",
        "curl: (56)",
        "curl: (92)",
        "connection",
        "timed out",
        "timeout",
        "connection reset",
        "connection aborted",
        "remote end closed",
        "broken pipe",
    )
    return any(marker in message for marker in markers)


def _retry_after_seconds(response: requests.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if not value:
        return None

    try:
        seconds = float(value.strip())
    except (TypeError, ValueError):
        return None

    if seconds < 0:
        return None
    return min(seconds, MAX_SERVER_BACKOFF_SECONDS)


def _backoff_seconds(retry_index: int, response: requests.Response | None = None) -> float:
    server_delay = _retry_after_seconds(response) if response is not None else None
    if server_delay is not None:
        return server_delay

    base = min(2**retry_index, MAX_BACKOFF_SECONDS)
    return base + random.uniform(0.25, 0.75)


def _safe_close_response(response: requests.Response | None) -> None:
    if response is None:
        return
    try:
        response.close()
    except Exception:
        LOGGER.debug("Failed to close unsuccessful NSE response", exc_info=True)



def _persist_session_cookies(session) -> None:
    try:
        updated_cookies = session.cookies.get_dict()
        if updated_cookies:
            auth.set_session_token(updated_cookies)
    except Exception:
        LOGGER.debug("Failed to persist NSE session cookies", exc_info=True)



def _apply_session_token(session, session_token: dict | None, clear_first: bool = False) -> None:
    if clear_first:
        session.cookies.clear()
    if session_token:
        session.cookies.update(session_token)





def get_request(
    url: str,
    headers: dict | None = None,
    params: dict | None = None,
) -> requests.Response | None:
    """Perform a resilient synchronous NSE request.

    The function preserves the original public API: callers receive a response on
    success and ``None`` after bounded recovery attempts on failure.
    """
    try:
        if headers is None:
            headers = header.get_nse_headers(profile="api", profile_idx=CURRENT_PROFILE_IDX)

        session_token = auth.get_session_token(max_age_minutes=SESSION_MAX_AGE_MINUTES)
        if not session_token:
            session_token = _refresh_session_token()
            if not session_token:
                LOGGER.warning("Failed to establish NSE session.")
                return None

        session = _get_sync_session()
        _seed_sync_session(session, session_token)

        refreshed_after_block = False

        for retry_index in range(MAX_RETRIES):
            response = None
            try:
                response = session.get(
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )

                result = _classify_response(response)

                if result == "success":
                    _persist_session_cookies(session)
                    return response

                if result == "html_block" or result == "session_or_access_block":
                    if not refreshed_after_block:
                        refreshed_after_block = True
                        session_token = _refresh_session_token(force=True)
                        if session_token:
                            session = _get_sync_session()
                            _apply_session_token(session, session_token, clear_first=True)
                            _SESSION_LOCAL.seeded = True
                            _safe_close_response(response)
                            continue

                    status_code = response.status_code
                    _safe_close_response(response)
                    LOGGER.warning(
                        "NSE request rejected after bounded session recovery: status=%s url=%s",
                        status_code,
                        url,
                    )
                    return None

                if result == "rate_limited" or result == "transient_http":
                    delay = _backoff_seconds(retry_index, response)
                    status_code = response.status_code
                    _safe_close_response(response)
                    LOGGER.warning(
                        "Retryable NSE response: status=%s attempt=%s/%s delay=%.2fs url=%s",
                        status_code,
                        retry_index + 1,
                        MAX_RETRIES,
                        delay,
                        url,
                    )
                    if retry_index < MAX_RETRIES - 1:
                        time.sleep(delay)
                        continue
                    return None

                status_code = response.status_code
                _safe_close_response(response)
                LOGGER.warning("NSE request failed: status=%s url=%s", status_code, url)
                return None

            except Exception as e:
                _safe_close_response(response)

                if _is_transport_error(e) and retry_index < MAX_RETRIES - 1:
                    LOGGER.warning(
                        "NSE transport error: attempt=%s/%s error=%s",
                        retry_index + 1,
                        MAX_RETRIES,
                        e,
                    )

                    is_curl92 = "curl: (92)" in str(e).lower()

                    if is_curl92:
                        refreshed_token = _refresh_session_token(force=True)
                        if refreshed_token:
                            session_token = refreshed_token
                        session = _get_sync_session()
                    else:
                        session = _get_sync_session(force_new=True)

                    _apply_session_token(session, session_token, clear_first=True)
                    _SESSION_LOCAL.seeded = True
                    time.sleep(_backoff_seconds(retry_index))
                    continue

                LOGGER.warning(
                    "NSE request failed without further recovery: attempt=%s/%s error=%s",
                    retry_index + 1,
                    MAX_RETRIES,
                    e,
                )
                return None

        LOGGER.warning("NSE request exhausted recovery attempts: url=%s", url)
        return None

    except Exception as e:
        LOGGER.exception("Critical NSE scraper failure: %s", e)
        return None




async def async_get_request(
    url: str,
    headers: dict | None = None,
    params: dict | None = None,
    session: requests.AsyncSession | None = None,
) -> requests.Response | None:
    """Async counterpart of :func:`get_request` with the same recovery semantics."""
    if headers is None:
        headers = header.get_nse_headers(profile="api", profile_idx=CURRENT_PROFILE_IDX)

    session_token = auth.get_session_token(max_age_minutes=SESSION_MAX_AGE_MINUTES)

    close_session = False
    if session is None:
        session = _create_async_session()
        close_session = True

    try:
        if not session_token:
            session_token = await _async_refresh_session_token(session)
            if not session_token:
                LOGGER.warning("Failed to establish NSE async session.")
                return None

        if not session.cookies:
            _apply_session_token(session, session_token)

        refreshed_after_block = False

        for retry_index in range(MAX_RETRIES):
            response = None
            try:
                response = await session.get(
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )

                result = _classify_response(response)

                if result == "success":
                    _persist_session_cookies(session)
                    return response

                if result == "html_block" or result == "session_or_access_block":
                    if not refreshed_after_block:
                        refreshed_after_block = True

                        if close_session:
                            await session.close()
                            session = _create_async_session()
                        else:
                            session.cookies.clear()

                        session_token = await _async_refresh_session_token(session, force=True)
                        if session_token:
                            _apply_session_token(session, session_token, clear_first=True)
                            _safe_close_response(response)
                            continue

                    status_code = response.status_code
                    _safe_close_response(response)
                    LOGGER.warning(
                        "NSE async request rejected after bounded session recovery: status=%s url=%s",
                        status_code,
                        url,
                    )
                    return None

                if result == "rate_limited" or result == "transient_http":
                    delay = _backoff_seconds(retry_index, response)
                    status_code = response.status_code
                    _safe_close_response(response)
                    LOGGER.warning(
                        "Retryable NSE async response: status=%s attempt=%s/%s delay=%.2fs url=%s",
                        status_code,
                        retry_index + 1,
                        MAX_RETRIES,
                        delay,
                        url,
                    )
                    if retry_index < MAX_RETRIES - 1:
                        await asyncio.sleep(delay)
                        continue
                    return None

                status_code = response.status_code
                _safe_close_response(response)
                LOGGER.warning("NSE async request failed: status=%s url=%s", status_code, url)
                return None

            except Exception as e:
                _safe_close_response(response)

                if _is_transport_error(e) and retry_index < MAX_RETRIES - 1:
                    LOGGER.warning(
                        "NSE async transport error: attempt=%s/%s error=%s",
                        retry_index + 1,
                        MAX_RETRIES,
                        e,
                    )

                    is_curl92 = "curl: (92)" in str(e).lower()

                    if is_curl92:
                        if close_session:
                            await session.close()
                            session = _create_async_session()
                        else:
                            session.cookies.clear()

                        refreshed_token = await _async_refresh_session_token(
                            session,
                            force=True,
                        )
                        if refreshed_token:
                            session_token = refreshed_token
                    else:
                        if close_session:
                            await session.close()
                            session = _create_async_session()
                        else:
                            session.cookies.clear()

                    _apply_session_token(session, session_token, clear_first=True)
                    await asyncio.sleep(_backoff_seconds(retry_index))
                    continue

                LOGGER.warning(
                    "NSE async request failed without further recovery: attempt=%s/%s error=%s",
                    retry_index + 1,
                    MAX_RETRIES,
                    e,
                )
                return None

        LOGGER.warning("NSE async request exhausted recovery attempts: url=%s", url)
        return None

    finally:
        if close_session:
            try:
                await session.close()
            except Exception:
                LOGGER.debug("Failed to close owned NSE async session", exc_info=True)

