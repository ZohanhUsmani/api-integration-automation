"""HTTP client with auth, retries, pagination."""
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIClient:
    def __init__(self, base_url, auth=None, retries=3, timeout=20, rps=2.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.min_interval = 1.0 / max(rps, 0.01)
        self.last = 0.0
        self.session = requests.Session()
        retry = Retry(total=retries, backoff_factor=0.5,
                      status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self._apply_auth(auth or {})

    def _apply_auth(self, auth):
        t = auth.get("type", "none")
        if t == "bearer":
            self.session.headers["Authorization"] = f"Bearer {auth['token']}"
        elif t == "apikey":
            self.session.headers[auth.get("header", "X-API-Key")] = auth["key"]
        elif t == "basic":
            self.session.auth = (auth["username"], auth["password"])

    def _throttle(self):
        now = time.time()
        if now - self.last < self.min_interval:
            time.sleep(self.min_interval - (now - self.last))
        self.last = time.time()

    def request(self, method, path, **kw):
        self._throttle()
        url = path if path.startswith("http") else self.base_url + path
        resp = self.session.request(method, url, timeout=self.timeout, **kw)
        resp.raise_for_status()
        return resp

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)

    def paginate(self, path, params=None, strategy="page", page_key="page",
                per_page=50, items_key=None, max_pages=100):
        params = dict(params or {})
        results = []
        page = 1
        cursor = None
        for _ in range(max_pages):
            if strategy == "page":
                params[page_key] = page
                params.setdefault("per_page", per_page)
            elif strategy == "offset":
                params["offset"] = (page - 1) * per_page
                params["limit"] = per_page
            elif strategy == "cursor" and cursor:
                params["cursor"] = cursor

            resp = self.get(path, params=params).json()
            items = resp if isinstance(resp, list) else resp.get(items_key or "data", [])
            if not items:
                break
            results.extend(items)

            if strategy == "cursor":
                cursor = resp.get("next_cursor") or resp.get("next")
                if not cursor:
                    break
            else:
                page += 1
                total = resp.get("total") if isinstance(resp, dict) else None
                if total is not None and len(results) >= total:
                    break
        return results