# DEFAULT HEADERS

default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com/",
}


####### CHROME PROFILES #######

CHROME_PROFILES = [
    {
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "platform": '"Windows"',
        "sec_ch_ua": '"Chromium";v="133", "Not:A-Brand";v="24", "Google Chrome";v="133"',
    }
]

ACCEPT_API_VARIANTS = [
    "application/json, text/javascript, */*; q=0.01",
    "application/json, text/plain, */*",
    "*/*",
]


def get_nse_headers(profile: str = "api", profile_idx: int = 0, referer: str | None = None) -> dict:
    """
    Generate the stable NSE request headers used by nsemine.

    ``profile_idx`` remains in the public signature for backwards compatibility,
    but there is intentionally only one canonical Chrome 133 advertised profile.
    """
    selected = CHROME_PROFILES[profile_idx]

    headers = {
        "User-Agent": selected["ua"],
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "sec-ch-ua": selected["sec_ch_ua"],
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": selected["platform"],
    }

    if profile == "page":
        headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": referer or "https://www.nseindia.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        })
    else:
        headers.update({
            "Accept": ACCEPT_API_VARIANTS[0],
            "Referer": referer or "https://www.nseindia.com/market-data/live-equity-market",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        })

    return headers
