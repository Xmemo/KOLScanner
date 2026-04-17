from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import List, Optional

from .market_data import FixtureMarketDataClient, SolanaTrackerClient
from .models import SignalEvaluation, SignalMessage
from .report import write_channel_report, write_workspace_summary
from .scoring import evaluate_signal, score_channel
from .telegram_export import load_exported_messages, iter_signal_messages


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def _iter_input_files(inputs: List[str]) -> List[Path]:
    files: List[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        else:
            files.append(path)
    return files


def _build_market_client(args: argparse.Namespace):
    if args.market_fixture:
        return FixtureMarketDataClient(args.market_fixture)
    api_key = args.api_key or os.getenv("SOLANA_TRACKER_API_KEY", "")
    if api_key:
        return SolanaTrackerClient(api_key=api_key)
    return None


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Signal quality audit toolkit for exported Telegram histories")
    parser.add_argument("inputs", nargs="+", help="Telegram export JSON file(s) or directories")
    parser.add_argument("--output-dir", default="outputs", help="Output directory for reports")
    parser.add_argument("--channel-name", help="Override the channel name for a single input file")
    parser.add_argument("--market-fixture", help="CSV fixture with token_address,timestamp,price columns")
    parser.add_argument("--api-key", help="Solana Tracker API key (defaults to SOLANA_TRACKER_API_KEY)")
    parser.add_argument("--lookahead-hours", type=int, default=int(os.getenv("DEFAULT_LOOKAHEAD_HOURS", "24")))
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    args = parser.parse_args(argv)

    _configure_logging(args.log_level)
    logger = logging.getLogger("signal_qa.cli")

    market_client = _build_market_client(args)
    if market_client is None:
        logger.warning("No market-data source configured. Reports will contain parse-only results.")

    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    channel_summaries = []
    input_files = _iter_input_files(args.inputs)
    if not input_files:
        logger.error("No input files found.")
        return 2

    for index, file_path in enumerate(input_files, start=1):
        channel_name = args.channel_name if len(input_files) == 1 and args.channel_name else file_path.stem
        logger.info("Processing %s (%d/%d)", file_path, index, len(input_files))

        try:
            raw_messages = load_exported_messages(file_path)
        except Exception as exc:
            logger.exception("Failed to read %s: %s", file_path, exc)
            continue

        signals: List[SignalMessage] = iter_signal_messages(raw_messages, source_file=str(file_path), channel_name=channel_name)
        evaluations: List[SignalEvaluation] = []
        if market_client is not None:
            for signal in signals:
                evaluations.append(evaluate_signal(signal, market_client, lookahead_hours=args.lookahead_hours))

        summary = score_channel(
            channel_name=channel_name,
            source_files=[str(file_path)],
            total_messages=len(raw_messages),
            evaluations=evaluations,
        )
        channel_summaries.append(summary)
        write_channel_report(
            output_root=output_root,
            channel_name=channel_name,
            source_files=[str(file_path)],
            messages=signals,
            evaluations=evaluations,
            summary=summary,
        )

    if channel_summaries:
        write_workspace_summary(output_root, channel_summaries)
        logger.info("Wrote workspace summary for %d channel(s) to %s", len(channel_summaries), output_root)
        return 0

    logger.error("No channel summaries were produced.")
    return 1
