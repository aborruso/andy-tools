"""HTTP client for the IstatData AI assistant backend.

Wraps `POST nodes/{node}/AI/ExecuteSearch` on the Data Browser hub, the same
endpoint the web form at
https://esploradati.istat.it/databrowser/#/it/dw/search?ai=true calls.
"""

import json
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://esploradati.istat.it/databrowserhub/api/core/"
DEFAULT_NODE = 1
DEFAULT_LANG = "it"
DEFAULT_MAX_RESULTS = 20

# Declared by the node itself (extra `AIRateLimiting`). The backend rejects the
# request with INTERNAL_ERROR_SERVER when this block is missing.
RATE_LIMITING = {"limit": 10, "seconds": 60, "maxMessageLength": 204800}


class ApiError(RuntimeError):
    """The backend answered with an error payload or an unusable response."""

    def __init__(self, message, code=None, status=None):
        super().__init__(message)
        self.code = code
        self.status = status


class RateLimitError(ApiError):
    """The backend refused the call because the rate budget is exhausted."""


def _request(url, lang, payload=None, timeout=60):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json, text/plain, */*", "UserLang": lang}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        status = exc.code
    except urllib.error.URLError as exc:
        raise ApiError(f"network error contacting {url}: {exc.reason}") from exc

    try:
        parsed = json.loads(body)
    except ValueError:
        raise ApiError(f"non-JSON answer from {url} (HTTP {status})", status=status)

    if isinstance(parsed, dict) and parsed.get("errorCode"):
        code = parsed["errorCode"]
        message = parsed.get("message") or code
        if status == 429 or "RATE" in code.upper():
            raise RateLimitError(message, code=code, status=status)
        raise ApiError(message, code=code, status=status)
    if status >= 400:
        raise ApiError(f"HTTP {status} from {url}", status=status)
    return parsed


class Client:
    def __init__(self, base_url=DEFAULT_BASE_URL, node=DEFAULT_NODE,
                 lang=DEFAULT_LANG, timeout=60):
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.node = node
        self.lang = lang
        self.timeout = timeout

    def execute_search(self, request, session_id=None, max_results=DEFAULT_MAX_RESULTS):
        """Ask the assistant a question. Returns the raw response dict.

        Passing back the `session_id` from a previous answer keeps the
        conversation context: follow-up questions are resolved against it.
        """
        payload = {
            "session_id": session_id,
            "request": request,
            "aiSearchMaxResults": max_results,
            "aiRateLimiting": RATE_LIMITING,
            "action": {"type": "query"},
        }
        url = f"{self.base_url}nodes/{self.node}/AI/ExecuteSearch"
        answer = _request(url, self.lang, payload, self.timeout)
        if not isinstance(answer, dict) or "chatContext" not in answer:
            raise ApiError("unexpected answer shape from ExecuteSearch")
        return answer

    def fetch_catalog(self):
        """Full dataset catalogue of the node (~1.9 MB, a couple of seconds)."""
        url = f"{self.base_url}nodes/{self.node}/catalog"
        answer = _request(url, self.lang, None, max(self.timeout, 120))
        if not isinstance(answer, dict) or "datasetMap" not in answer:
            raise ApiError("unexpected answer shape from catalog")
        return answer
