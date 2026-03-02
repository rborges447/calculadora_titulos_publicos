from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass
from typing import Dict, Optional

import requests


@dataclass
class Token:
    access_token: str
    expires_at: float # epoch seconds


class AnbimaAuth:
    TOKEN_URL = "https://api.anbima.com.br/oauth/access-token"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
    ):

        self.client_id = client_id or os.getenv("ANBIMA_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("ANBIMA_CLIENT_SECRET", "")
        self.timeout = timeout

        if not self.client_id or not self.client_secret:
            raise RuntimeError(
                "Credenciais ANBIMA ausentes. Defina ANBIMA_CLIENT_ID e ANBIMA_CLIENT_SECRET."
            )

        self._token: Optional[Token] = None

    def _basic_auth_header(self) -> str:
        raw = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        return "Basic " + base64.b64encode(raw).decode("utf-8")

    def get_access_token(self) -> str:
        # reusa token se ainda válido
        if self._token and time.time() < (self._token.expires_at - 30):
            return self._token.access_token

        headers = {
            "Content-Type": "application/json",
            "Authorization": self._basic_auth_header(),
        }
        data = {"grant_type": "client_credentials"}

        resp = requests.post(self.TOKEN_URL, headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        payload = resp.json()
        access_token = payload["access_token"]
        expires_in = float(payload.get("expires_in", 1800)) # fallback 30 min

        self._token = Token(access_token=access_token, expires_at=time.time() + expires_in)
        return access_token

    def build_headers(self) -> Dict[str, str]:
        token = self.get_access_token()

        return {
            "Content-Type": "application/json",
            "client_id": self.client_id,
            "access_token": token,
        }
