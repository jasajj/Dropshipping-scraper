from typing import Dict, List, Optional
import json
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import META_ACCESS_TOKEN, META_API_VERSION, USER_AGENT

BASE = f"https://graph.facebook.com/{META_API_VERSION}/ads_archive"

class MetaApiError(Exception):
    pass

def _headers():
    return {"User-Agent": USER_AGENT}

def _params(base_params: Dict) -> Dict:
    if not META_ACCESS_TOKEN:
        raise MetaApiError("Missing META_ACCESS_TOKEN. Put it in your .env file.")
    p = {
        "access_token": META_ACCESS_TOKEN,
        "limit": 100,  # use larger page size
        "fields": ",".join([
            "id","page_id","page_name",
            "ad_creation_time","ad_delivery_start_time","ad_delivery_stop_time",
            "ad_snapshot_url",
            "ad_creative_bodies","ad_creative_link_titles","ad_creative_link_descriptions","ad_creative_link_captions",
            "languages","publisher_platforms"
        ]),
    }
    p.update(base_params)
    return p

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=30),
       retry=retry_if_exception_type(MetaApiError))
def _get(url: str, params: Dict):
    r = requests.get(url, params=params, headers=_headers(), timeout=60)
    if r.status_code >= 400:
        raise MetaApiError(f"{r.status_code}: {r.text[:300]}")
    return r.json()

def fetch_ads(
    countries: List[str],
    terms: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    status: str = "ACTIVE",
):
    """
    Generator that yields ad records from Meta Ad Library.
    - countries: list of ISO codes (e.g. ["BE","NL","DE"])
    - terms: keyword search (string)
    - since/until: YYYY-MM-DD
    - status: ACTIVE | INACTIVE | ALL
    """
    base = {
        "ad_reached_countries": json.dumps(countries),
        "ad_type": "ALL",
        "ad_active_status": status,
        "search_terms": terms or "",
        "search_type": "KEYWORD_UNORDERED",
    }
    url = BASE
    params = _params(base)
    while True:
        data = _get(url, params)
        for item in data.get("data", []):
            yield item
        next_url = data.get("paging", {}).get("next")
        if not next_url:
            break
        url = next_url
        params = {}  # next already includes params

