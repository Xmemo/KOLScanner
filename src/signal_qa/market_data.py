from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd
import requests

logger = logging.getLogger(__name__)


@dataclass
class PricePoint:
    price: float
    timestamp: int


class SolanaTrackerClient:
    def __init__(self, api_key: str, base_url: str = "https://data.solanatracker.io", timeout: int = 20) -> None:
        if not api_key:
            raise ValueError("api_key is required for live mode")
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._last_request_ts = 0.0

    def _request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        delay = 0.5
        elapsed = time.time() - self._last_request_ts
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_request_ts = time.time()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        for attempt in range(4):
            try:
                resp = requests.get(
                    url,
                    headers={"Accept": "application/json", "x-api-key": self.api_key},
                    params=params,
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.HTTPError as exc:
                status_code = exc.response.status_code if exc.response is not None else None
                if status_code in {429, 500, 502, 503, 504} and attempt < 3:
                    sleep_for = (2 ** attempt) + random.random()
                    logger.warning("Retrying %s after HTTP %s in %.2fs", url, status_code, sleep_for)
                    time.sleep(sleep_for)
                    continue
                logger.error("Solana Tracker request failed for %s: %s", url, exc)
                return None
            except requests.RequestException as exc:
                logger.error("Solana Tracker request failed for %s: %s", url, exc)
                return None
        return None

    def get_price_at_timestamp(self, token_address: str, timestamp: int) -> Optional[Dict[str, Any]]:
        return self._request("/price/history/timestamp", {"token": token_address, "timestamp": timestamp})

    def get_price_history_range(self, token_address: str, time_from: int, time_to: int) -> Optional[Dict[str, Any]]:
        return self._request(
            "/price/history/range",
            {"token": token_address, "time_from": time_from, "time_to": time_to},
        )


class FixtureMarketDataClient:
    def __init__(self, csv_path: Union[str, Path]) -> None:
        self.frame = pd.read_csv(csv_path)
        required = {"token_address", "timestamp", "price"}
        missing = required.difference(self.frame.columns)
        if missing:
            raise ValueError(f"Fixture CSV missing columns: {sorted(missing)}")
        self.frame["timestamp"] = self.frame["timestamp"].astype(int)
        self.frame["price"] = self.frame["price"].astype(float)

    def get_price_at_timestamp(self, token_address: str, timestamp: int) -> Optional[Dict[str, Any]]:
        subset = self.frame[(self.frame["token_address"] == token_address) & (self.frame["timestamp"] <= timestamp)]
        if subset.empty:
            return None
        row = subset.sort_values("timestamp").iloc[-1]
        return {"price": float(row["price"]), "timestamp": int(row["timestamp"])}

    def get_price_history_range(self, token_address: str, time_from: int, time_to: int) -> Optional[Dict[str, Any]]:
        subset = self.frame[
            (self.frame["token_address"] == token_address)
            & (self.frame["timestamp"] >= time_from)
            & (self.frame["timestamp"] <= time_to)
        ]
        if subset.empty:
            return None
        row = subset.sort_values(["price", "timestamp"], ascending=[False, True]).iloc[0]
        return {"price": {"highest": {"price": float(row["price"]), "time": int(row["timestamp"])}}}
