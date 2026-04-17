from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Union

import pandas as pd

from .models import ChannelSummary, SignalEvaluation, SignalMessage


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_channel_report(
    output_root: Union[str, Path],
    channel_name: str,
    source_files: List[str],
    messages: Iterable[SignalMessage],
    evaluations: Iterable[SignalEvaluation],
    summary: ChannelSummary,
) -> Path:
    channel_dir = _ensure_dir(Path(output_root) / "channels" / channel_name)

    signals_df = pd.DataFrame([item.to_dict() for item in messages])
    evals_df = pd.DataFrame([item.to_dict() for item in evaluations])
    signals_df.to_csv(channel_dir / "signals.csv", index=False)
    evals_df.to_csv(channel_dir / "signal_evaluations.csv", index=False)

    summary_data = summary.to_dict()
    summary_data["source_files"] = source_files

    (channel_dir / "channel_summary.json").write_text(
        json.dumps(summary_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    md_lines = [
        f"# {channel_name}",
        "",
        "## Summary",
        "",
        f"- Source files: {len(source_files)}",
        f"- Total messages: {summary.total_messages}",
        f"- Parsed signals: {summary.parsed_signals}",
        f"- Evaluated signals: {summary.evaluated_signals}",
        f"- Coverage: {summary.coverage:.2%}",
        f"- Win rate: {summary.win_rate:.2%}" if summary.win_rate is not None else "- Win rate: N/A",
        f"- Avg return multiple: {summary.avg_return_multiple:.4f}" if summary.avg_return_multiple is not None else "- Avg return multiple: N/A",
        f"- Median return multiple: {summary.median_return_multiple:.4f}" if summary.median_return_multiple is not None else "- Median return multiple: N/A",
        f"- Std return multiple: {summary.std_return_multiple:.4f}" if summary.std_return_multiple is not None else "- Std return multiple: N/A",
        f"- Quality score: {summary.quality_score}" if summary.quality_score is not None else "- Quality score: N/A",
        f"- Grade: {summary.grade}",
        "",
        "## Notes",
        "",
        summary.notes or "-",
    ]
    (channel_dir / "channel_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    html = [
        "<html><head><meta charset='utf-8'><title>Channel Summary</title>",
        "<style>body{font-family:Arial,sans-serif;max-width:1100px;margin:40px auto;padding:0 16px;} table{border-collapse:collapse;width:100%;} th,td{border:1px solid #ddd;padding:8px;text-align:left;} th{background:#f6f6f6;}</style>",
        "</head><body>",
        f"<h1>{channel_name}</h1>",
        "<h2>Summary</h2>",
        pd.DataFrame([summary_data]).to_html(index=False, escape=False),
        "<h2>Signals</h2>",
        signals_df.to_html(index=False, escape=False) if not signals_df.empty else "<p>No parsed signals.</p>",
        "<h2>Evaluations</h2>",
        evals_df.to_html(index=False, escape=False) if not evals_df.empty else "<p>No priced evaluations.</p>",
        "</body></html>",
    ]
    (channel_dir / "channel_summary.html").write_text("\n".join(html), encoding="utf-8")
    return channel_dir


def write_workspace_summary(output_root: Union[str, Path], summaries: Iterable[ChannelSummary]) -> Path:
    output_root = Path(output_root)
    _ensure_dir(output_root)
    rows = [summary.to_dict() for summary in summaries]
    df = pd.DataFrame(rows)
    csv_path = output_root / "workspace_summary.csv"
    df.to_csv(csv_path, index=False)
    (output_root / "workspace_summary.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return csv_path
