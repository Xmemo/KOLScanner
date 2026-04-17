# Dashboard

Minimal Streamlit UI for channel-quality summaries.

## What it does

- loads a `workspace_summary.csv` file
- shows channel-level quality scores
- lets you sort channels by grade, coverage, or win rate
- provides a quick visual check before reading the full reports

## Run

```bash
PYTHONPATH=src streamlit run dashboard/app_streamlit.py
```

## Input

By default, the dashboard looks for:

- `outputs/workspace_summary.csv`

You can also paste a different path in the sidebar.

