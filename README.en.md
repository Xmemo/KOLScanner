# Signal QA for Solana Meme Coin Channels

> Audit exported Telegram channel history and turn noisy signal streams into evidence.

A signal quality audit toolkit for exported Telegram channel history.

## Why this exists

Crypto Telegram is full of fast signal streams, but most of them are noisy.
The real problem is not finding signals. The real problem is identifying quality.

This toolkit helps you audit channels instead of trusting hype.

## What it does

- Ingest exported Telegram channel history files
- Normalize noisy messages into structured signal records
- Connect each signal to post-hoc market data
- Score channels with win rate, EV proxy, lift, and stability metrics
- Generate CSV, JSON, Markdown, HTML, and dashboard views

## What it is not

- Not a trading bot
- Not an automatic Telegram scraper
- Not a guaranteed alpha generator
- Not a promise of profit

## Input model

1. Export a Telegram channel history locally from Telegram Desktop or a similar export flow
2. Pass the JSON file, or a folder of JSON files, into the CLI
3. Optionally use a Solana Tracker API key or a local market-data fixture CSV

## Outputs

Each channel produces:

- `signals.csv`
- `signal_evaluations.csv`
- `channel_summary.json`
- `channel_summary.md`
- `channel_summary.html`

For multi-channel runs:

- `workspace_summary.csv`
- `workspace_summary.json`

## Quick start

```bash
cd signal_qa_open_source
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
PYTHONPATH=src python3 -m signal_qa examples/sample_telegram_export.json \
  --market-fixture examples/sample_market_prices.csv \
  --output-dir outputs/demo
```

Live API mode:

```bash
export SOLANA_TRACKER_API_KEY="your-key"
PYTHONPATH=src python3 -m signal_qa path/to/exported_channel.json --output-dir outputs/live
```

## Dashboard

A minimal Streamlit dashboard is included for browsing channel summaries.
It shows top channels, quality score, coverage, win rate, and grade distribution.

Run it:

```bash
PYTHONPATH=src streamlit run dashboard/app_streamlit.py
```

## Security posture

- No API keys are committed
- No private datasets are included
- Raw exports and generated outputs are ignored by default
- Live credentials stay in local `.env` files

See [`security/README.md`](security/README.md) for the threat model and operational constraints.

## Repo layout

```text
signal_qa_open_source/
  src/signal_qa/
  dashboard/
  examples/
  security/
  tests/
```

## Who this is for

- Traders who want to filter noisy Telegram channels
- Researchers who want reproducible signal audits
- Builders who want a neutral evaluation layer before adding AI or ML

## Short version

A Telegram signal QA toolkit for Solana meme coins and altcoins.

