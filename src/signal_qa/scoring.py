from __future__ import annotations

import logging
import math
import statistics
from typing import Any, Dict, Iterable, List, Optional

from .models import ChannelSummary, SignalEvaluation, SignalMessage

logger = logging.getLogger(__name__)


def _extract_price(response: Any) -> Optional[float]:
    if not isinstance(response, dict):
        return None
    for key in ("price", "p1", "value"):
        value = response.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    price = response.get("price")
    if isinstance(price, dict):
        for key in ("price", "value"):
            nested = price.get(key)
            if isinstance(nested, (int, float)):
                return float(nested)
        highest = price.get("highest")
        if isinstance(highest, dict):
            nested = highest.get("price")
            if isinstance(nested, (int, float)):
                return float(nested)
    return None


def _extract_timestamp(response: Any) -> Optional[int]:
    if not isinstance(response, dict):
        return None
    for key in ("timestamp", "time", "ts"):
        value = response.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    price = response.get("price")
    if isinstance(price, dict):
        highest = price.get("highest")
        if isinstance(highest, dict):
            value = highest.get("time")
            if isinstance(value, (int, float)):
                return int(value)
    return None


def evaluate_signal(
    signal: SignalMessage,
    market_client: Any,
    lookahead_hours: int = 24,
) -> SignalEvaluation:
    signal_id = f"{signal.channel_name}:{signal.message_id}:{signal.token_address}"
    entry_response = market_client.get_price_at_timestamp(signal.token_address, signal.timestamp) if market_client else None
    entry_price = _extract_price(entry_response)
    entry_timestamp = _extract_timestamp(entry_response)

    range_response = (
        market_client.get_price_history_range(
            signal.token_address,
            signal.timestamp,
            signal.timestamp + (lookahead_hours * 3600),
        )
        if market_client
        else None
    )
    peak_price = None
    peak_timestamp = None
    if isinstance(range_response, dict):
        highest = range_response.get("price", {}).get("highest") if isinstance(range_response.get("price"), dict) else None
        if isinstance(highest, dict):
            price_value = highest.get("price")
            time_value = highest.get("time")
            if isinstance(price_value, (int, float)):
                peak_price = float(price_value)
            if isinstance(time_value, (int, float)):
                peak_timestamp = int(time_value)

    if entry_price is None:
        return SignalEvaluation(
            signal_id=signal_id,
            source_file=signal.source_file,
            channel_name=signal.channel_name,
            message_id=signal.message_id,
            token_address=signal.token_address,
            signal_timestamp=signal.timestamp,
            signal_time_iso=signal.signal_time_iso,
            lookahead_hours=lookahead_hours,
            entry_price=None,
            entry_timestamp=entry_timestamp,
            peak_price=peak_price,
            peak_timestamp=peak_timestamp,
            return_multiple=None,
            return_pct=None,
            status="unpriced",
            notes="No entry price was returned by the market-data source.",
        )

    if peak_price is None:
        return SignalEvaluation(
            signal_id=signal_id,
            source_file=signal.source_file,
            channel_name=signal.channel_name,
            message_id=signal.message_id,
            token_address=signal.token_address,
            signal_timestamp=signal.timestamp,
            signal_time_iso=signal.signal_time_iso,
            lookahead_hours=lookahead_hours,
            entry_price=entry_price,
            entry_timestamp=entry_timestamp,
            peak_price=None,
            peak_timestamp=peak_timestamp,
            return_multiple=None,
            return_pct=None,
            status="missing_range",
            notes="No peak price was returned for the lookahead window.",
        )

    return_multiple = peak_price / entry_price if entry_price else None
    return_pct = ((return_multiple - 1.0) * 100.0) if return_multiple is not None else None
    status = "win" if return_multiple is not None and return_multiple > 1.0 else "loss"
    return SignalEvaluation(
        signal_id=signal_id,
        source_file=signal.source_file,
        channel_name=signal.channel_name,
        message_id=signal.message_id,
        token_address=signal.token_address,
        signal_timestamp=signal.timestamp,
        signal_time_iso=signal.signal_time_iso,
        lookahead_hours=lookahead_hours,
        entry_price=entry_price,
        entry_timestamp=entry_timestamp,
        peak_price=peak_price,
        peak_timestamp=peak_timestamp,
        return_multiple=return_multiple,
        return_pct=return_pct,
        status=status,
        notes="",
    )


def score_channel(channel_name: str, source_files: List[str], total_messages: int, evaluations: Iterable[SignalEvaluation]) -> ChannelSummary:
    all_evaluations = list(evaluations)
    evals = [item for item in all_evaluations if item.return_multiple is not None]
    parsed_signals = len(all_evaluations)
    evaluated_signals = len(evals)
    coverage = (evaluated_signals / parsed_signals) if parsed_signals else 0.0

    if evals:
        return_multiples = [item.return_multiple for item in evals if item.return_multiple is not None]
        win_rate = sum(1 for item in evals if item.return_multiple and item.return_multiple > 1.0) / len(evals)
        avg_return_multiple = statistics.mean(return_multiples)
        median_return_multiple = statistics.median(return_multiples)
        std_return_multiple = statistics.pstdev(return_multiples) if len(return_multiples) > 1 else 0.0
        edge_component = max(0.0, min(1.0, (avg_return_multiple - 1.0)))
        stability_component = 1.0 / (1.0 + std_return_multiple)
        confidence_component = min(1.0, evaluated_signals / 25.0)
        raw_score = (0.45 * win_rate) + (0.25 * coverage) + (0.20 * edge_component) + (0.10 * stability_component)
        quality_score = round(100.0 * raw_score * confidence_component, 1)
    else:
        win_rate = None
        avg_return_multiple = None
        median_return_multiple = None
        std_return_multiple = None
        quality_score = None

    grade = "N/A"
    if quality_score is not None:
        if quality_score >= 80:
            grade = "A"
        elif quality_score >= 65:
            grade = "B"
        elif quality_score >= 50:
            grade = "C"
        elif quality_score >= 35:
            grade = "D"
        else:
            grade = "F"

    return ChannelSummary(
        channel_name=channel_name,
        source_files=source_files,
        total_messages=total_messages,
        parsed_signals=parsed_signals,
        evaluated_signals=evaluated_signals,
        coverage=round(coverage, 4),
        win_rate=round(win_rate, 4) if win_rate is not None else None,
        avg_return_multiple=round(avg_return_multiple, 4) if avg_return_multiple is not None else None,
        median_return_multiple=round(median_return_multiple, 4) if median_return_multiple is not None else None,
        std_return_multiple=round(std_return_multiple, 4) if std_return_multiple is not None else None,
        quality_score=quality_score,
        grade=grade,
        notes="" if evals else "No priced evaluations were available for this channel.",
    )
