from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from .models import SignalMessage

logger = logging.getLogger(__name__)

BASE58_ADDRESS_RE = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")
EXPLICIT_ADDRESS_RE = re.compile(
    r"(?:CA|Contract|contract|mint|Token|token)[^1-9A-HJ-NP-Za-km-z]{0,12}"
    r"([1-9A-HJ-NP-Za-km-z]{32,44})"
)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_exported_messages(path: Union[str, Path]) -> List[Dict[str, Any]]:
    file_path = Path(path)
    data = _load_json(file_path)

    if isinstance(data, list):
        messages = data
    elif isinstance(data, dict) and isinstance(data.get("messages"), list):
        messages = data["messages"]
    elif isinstance(data, dict):
        possible = None
        for value in data.values():
            if isinstance(value, dict) and isinstance(value.get("messages"), list):
                possible = value["messages"]
                break
        if possible is None:
            raise ValueError(f"Unsupported Telegram export structure in {file_path}")
        messages = possible
    else:
        raise ValueError(f"Unsupported Telegram export structure in {file_path}")

    normalized: List[Dict[str, Any]] = []
    for message in messages:
        if isinstance(message, dict):
            normalized.append(message)
    return normalized


def flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: List[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)
    if value is None:
        return ""
    return str(value)


def extract_timestamp(message: Dict[str, Any]) -> Optional[int]:
    raw_unix = message.get("date_unixtime")
    if raw_unix is not None:
        try:
            return int(float(raw_unix))
        except (TypeError, ValueError):
            logger.debug("Failed to parse date_unixtime: %s", raw_unix)

    raw_date = message.get("date")
    if isinstance(raw_date, str):
        try:
            parsed = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return int(parsed.timestamp())
        except ValueError:
            logger.debug("Failed to parse date: %s", raw_date)
    return None


def extract_token_address(text: str) -> Optional[str]:
    if not text:
        return None

    explicit = EXPLICIT_ADDRESS_RE.search(text)
    if explicit:
        return explicit.group(1)

    if "CA" in text or "ca" in text or "mint" in text or "token" in text:
        base58 = BASE58_ADDRESS_RE.search(text)
        if base58:
            return base58.group(0)

    candidates = BASE58_ADDRESS_RE.findall(text)
    if candidates:
        return candidates[0]
    return None


def iter_signal_messages(messages: Iterable[Dict[str, Any]], source_file: str, channel_name: str) -> List[SignalMessage]:
    results: List[SignalMessage] = []
    for index, message in enumerate(messages):
        timestamp = extract_timestamp(message)
        if timestamp is None:
            continue

        text = flatten_text(message.get("text"))
        token_address = extract_token_address(text)
        if not token_address:
            continue

        message_id = str(message.get("id", index))
        results.append(
            SignalMessage(
                source_file=source_file,
                channel_name=channel_name,
                message_id=message_id,
                timestamp=timestamp,
                signal_time_iso=datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
                token_address=token_address,
                raw_text=text,
                raw_message=message,
            )
        )
    return results


def parse_export_file(path: Union[str, Path], channel_name: Optional[str] = None) -> List[SignalMessage]:
    file_path = Path(path)
    messages = load_exported_messages(file_path)
    resolved_channel_name = channel_name or file_path.stem
    return iter_signal_messages(messages, source_file=str(file_path), channel_name=resolved_channel_name)
