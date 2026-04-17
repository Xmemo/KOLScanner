from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


DEFAULT_SUMMARY_PATH = Path("outputs/workspace_summary.csv")


def load_summary(path: str) -> Optional[pd.DataFrame]:
    summary_path = Path(path)
    if not summary_path.exists():
        return None
    df = pd.read_csv(summary_path)
    if df.empty:
        return None
    return df


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(229, 159, 44, 0.10), transparent 24%),
                radial-gradient(circle at top right, rgba(75, 85, 99, 0.18), transparent 22%),
                linear-gradient(180deg, #0B0F14 0%, #0F141B 38%, #121821 100%);
            color: #E5E7EB;
        }
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(10, 14, 20, 0.98));
            border-right: 1px solid rgba(148, 163, 184, 0.12);
        }
        .hero {
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 28px;
            padding: 28px 28px 20px 28px;
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(17, 24, 39, 0.76)),
                radial-gradient(circle at top right, rgba(217, 119, 6, 0.18), transparent 35%);
            box-shadow: 0 24px 70px rgba(0, 0, 0, 0.28);
            margin-bottom: 18px;
        }
        .eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.18em;
            color: #F59E0B;
            font-size: 0.74rem;
            margin-bottom: 10px;
        }
        .hero h1 {
            margin: 0;
            font-size: 3.0rem;
            line-height: 1.0;
            color: #F8FAFC;
        }
        .hero p {
            margin: 14px 0 0 0;
            max-width: 900px;
            color: #CBD5E1;
            font-size: 1.03rem;
        }
        .kpi-card {
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 22px;
            padding: 18px 18px 14px 18px;
            background: rgba(15, 23, 42, 0.76);
            box-shadow: 0 14px 40px rgba(0, 0, 0, 0.20);
        }
        .kpi-label {
            color: #94A3B8;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 10px;
        }
        .kpi-value {
            color: #F8FAFC;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.0;
        }
        .kpi-sub {
            color: #CBD5E1;
            font-size: 0.9rem;
            margin-top: 8px;
        }
        .section-title {
            color: #F8FAFC;
            font-size: 1.1rem;
            font-weight: 700;
            margin: 10px 0 12px 0;
            letter-spacing: 0.01em;
        }
        .soft-panel {
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 22px;
            padding: 18px;
            background: rgba(15, 23, 42, 0.72);
        }
        .muted {
            color: #94A3B8;
            font-size: 0.94rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, subtext: str = "") -> str:
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{subtext}</div>
    </div>
    """


def format_pct(value: float) -> str:
    return f"{value:.1%}"


def main() -> None:
    st.set_page_config(page_title="Signal QA Dashboard", layout="wide", page_icon="◼")
    apply_styles()

    st.sidebar.title("Signal QA")
    st.sidebar.caption("Channel audit workspace")
    summary_path = st.sidebar.text_input("Summary CSV", value=str(DEFAULT_SUMMARY_PATH))
    min_messages = st.sidebar.number_input("Min total messages", min_value=0, value=0, step=1)
    min_coverage = st.sidebar.slider("Min coverage", 0.0, 1.0, 0.0, 0.01)

    grade_default = ["A", "B", "C", "D", "F"]
    grade_filter = st.sidebar.multiselect("Grades", grade_default, default=grade_default)
    sort_mode = st.sidebar.selectbox(
        "Sort by",
        ["quality_score", "coverage", "win_rate", "total_messages"],
        index=0,
    )
    top_n = st.sidebar.slider("Top N channels", 5, 50, 15, 1)

    df = load_summary(summary_path)
    if df is None:
        st.markdown(
            """
            <div class="hero">
              <div class="eyebrow">Signal QA Dashboard</div>
              <h1>Audit Telegram channel quality.</h1>
              <p>
                Load a workspace summary and inspect which channels are actually useful.
                This dashboard is designed to surface stable signal sources, not hype.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("No summary CSV found yet. Run the CLI first, then open the dashboard again.")
        st.code(
            "PYTHONPATH=src python3 -m signal_qa examples/sample_telegram_export.json "
            "--market-fixture examples/sample_market_prices.csv --output-dir outputs/demo"
        )
        return

    required = {"grade", "coverage", "total_messages", "channel_name"}
    missing = sorted(required.difference(df.columns))
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        return

    filtered = df.copy()
    filtered = filtered[filtered["total_messages"] >= min_messages]
    filtered = filtered[filtered["coverage"].fillna(0.0) >= min_coverage]
    filtered = filtered[filtered["grade"].isin(grade_filter)]

    if filtered.empty:
        st.warning("No rows match the current filters.")
        return

    if sort_mode in filtered.columns:
        filtered = filtered.sort_values(by=sort_mode, ascending=False)
    elif "quality_score" in filtered.columns:
        filtered = filtered.sort_values(by="quality_score", ascending=False)

    if top_n < len(filtered):
        ranked = filtered.head(top_n).copy()
    else:
        ranked = filtered.copy()

    score_series = ranked["quality_score"].dropna() if "quality_score" in ranked.columns else pd.Series(dtype=float)
    score_mean = score_series.mean() if not score_series.empty else None
    win_series = ranked["win_rate"].dropna() if "win_rate" in ranked.columns else pd.Series(dtype=float)
    win_mean = win_series.mean() if not win_series.empty else None
    coverage_mean = ranked["coverage"].fillna(0.0).mean()
    grade_a_share = (ranked["grade"] == "A").mean()

    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">Signal QA / Solana Meme Coin Channels</div>
          <h1>Audit the quality of Telegram signal channels.</h1>
          <p>
            This workspace turns exported Telegram histories into channel-level evidence:
            quality scores, win rate, coverage, and comparison views that help you separate
            useful channels from noisy ones.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(metric_card("Channels", str(len(ranked)), f"From {len(filtered)} filtered rows"), unsafe_allow_html=True)
    k2.markdown(
        metric_card(
            "Avg quality score",
            f"{score_mean:.1f}" if score_mean is not None and not pd.isna(score_mean) else "N/A",
            "Higher means more repeatable channel quality",
        ),
        unsafe_allow_html=True,
    )
    k3.markdown(
        metric_card(
            "Avg win rate",
            format_pct(win_mean) if win_mean is not None and not pd.isna(win_mean) else "N/A",
            "Share of evaluated signals that beat entry price",
        ),
        unsafe_allow_html=True,
    )
    k4.markdown(
        metric_card(
            "A-grade share",
            format_pct(grade_a_share),
            f"{format_pct(coverage_mean)} average coverage",
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Channel comparison</div>', unsafe_allow_html=True)
    left, right = st.columns([1.2, 1.0])

    with left:
        st.markdown('<div class="soft-panel">', unsafe_allow_html=True)
        chart_df = ranked[[col for col in ["channel_name", "quality_score", "coverage", "win_rate"] if col in ranked.columns]].copy()
        chart_df = chart_df.set_index("channel_name")
        st.write("Quality score by channel")
        if "quality_score" in chart_df.columns:
            st.bar_chart(chart_df["quality_score"])
        else:
            st.info("No quality_score column found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="soft-panel">', unsafe_allow_html=True)
        scatter_cols = [col for col in ["coverage", "quality_score", "win_rate"] if col in ranked.columns]
        st.write("Coverage vs quality")
        if len(scatter_cols) >= 2:
            scatter_df = ranked[scatter_cols + ["channel_name"]].dropna()
            if {"coverage", "quality_score"}.issubset(scatter_df.columns):
                st.scatter_chart(scatter_df.rename(columns={"coverage": "x", "quality_score": "y"})[["x", "y"]])
            else:
                st.info("Coverage and quality_score are required for this plot.")
        else:
            st.info("Not enough columns for channel comparison plot.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Channel ranking</div>', unsafe_allow_html=True)
    display_cols = [
        col
        for col in [
            "channel_name",
            "grade",
            "quality_score",
            "coverage",
            "win_rate",
            "parsed_signals",
            "evaluated_signals",
            "total_messages",
            "avg_return_multiple",
            "median_return_multiple",
        ]
        if col in ranked.columns
    ]
    st.dataframe(ranked[display_cols], use_container_width=True, height=360)

    bottom_left, bottom_right = st.columns([1.0, 1.1])
    with bottom_left:
        st.markdown('<div class="section-title">Grade distribution</div>', unsafe_allow_html=True)
        st.markdown('<div class="soft-panel">', unsafe_allow_html=True)
        st.bar_chart(ranked["grade"].value_counts())
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_right:
        st.markdown('<div class="section-title">Selected channel detail</div>', unsafe_allow_html=True)
        st.markdown('<div class="soft-panel">', unsafe_allow_html=True)
        selected = st.selectbox("Choose a channel", ranked["channel_name"].tolist())
        selected_row = ranked[ranked["channel_name"] == selected].iloc[0].to_dict()

        detail_cols = {
            key: selected_row.get(key)
            for key in [
                "channel_name",
                "grade",
                "quality_score",
                "coverage",
                "win_rate",
                "parsed_signals",
                "evaluated_signals",
                "total_messages",
                "avg_return_multiple",
                "median_return_multiple",
                "std_return_multiple",
                "notes",
            ]
            if key in selected_row
        }
        st.json(detail_cols)
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
