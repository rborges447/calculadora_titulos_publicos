from __future__ import annotations

import time
from typing import Any, List, Optional

import requests

from .auth import AnbimaAuth


class AnbimaClient:
    def __init__(self, auth: Optional[AnbimaAuth] = None, timeout: int = 30, max_retries: int = 3):
        self.auth = auth or AnbimaAuth()
        self.timeout = timeout
        self.max_retries = max_retries

    def fetch_by_date(self, url: str, date_iso: str) -> Optional[Any]:
        """
        GET em um endpoint ANBIMA com params {'data': YYYY-MM-DD}
        Retorna JSON ou None se 404.
        """
        params = {"data": date_iso}

        last_err: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                headers = self.auth.build_headers()
                resp = requests.get(url, headers=headers, params=params, timeout=self.timeout)

                if resp.status_code == 404:
                    return None

                resp.raise_for_status()
                return resp.json()

            except Exception as e:
                last_err = e
                if attempt < self.max_retries:
                    time.sleep(0.6 * attempt)
                else:
                    raise last_err from None

        return None

    def fetch_for_dates(self, url: str, date_list: List[str]) -> List[Any]:
        """
        Loop em várias datas; retorna lista de JSONs (ignorando None).
        """
        out: List[Any] = []
        for d in date_list:
            data = self.fetch_by_date(url, d)
            if data is not None:
                out.append(data)
        return out

