from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SignalMessage:
    source_file: str
    channel_name: str
    message_id: str
    timestamp: int
    signal_time_iso: str
    token_address: str
    raw_text: str
    raw_message: Dict[str, Any] = field(repr=False, default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SignalEvaluation:
    signal_id: str
    source_file: str
    channel_name: str
    message_id: str
    token_address: str
    signal_timestamp: int
    signal_time_iso: str
    lookahead_hours: int
    entry_price: Optional[float]
    entry_timestamp: Optional[int]
    peak_price: Optional[float]
    peak_timestamp: Optional[int]
    return_multiple: Optional[float]
    return_pct: Optional[float]
    status: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChannelSummary:
    channel_name: str
    source_files: List[str]
    total_messages: int
    parsed_signals: int
    evaluated_signals: int
    coverage: float
    win_rate: Optional[float]
    avg_return_multiple: Optional[float]
    median_return_multiple: Optional[float]
    std_return_multiple: Optional[float]
    quality_score: Optional[float]
    grade: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
