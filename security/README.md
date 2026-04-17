# Security Notes

This repository is sanitized for open source use.

## Threat model

Primary risks:

- accidental inclusion of API keys or private exports
- publishing raw Telegram history with sensitive channel content
- over-trusting third-party market-data APIs
- logging message bodies verbatim into shared reports

## Default controls

- `.env` is ignored by default
- `outputs/` is ignored by default
- `data/` is ignored by default except for example fixtures
- live market-data calls require an explicit API key
- the CLI can run in fixture mode for offline demos

## Operational guidance

- do not commit private Telegram exports
- do not commit live API responses unless they are sanitized
- do not store secret-bearing logs in the repository
- rotate keys if they were ever written into shell history or notebooks

## Review note

The legacy workspace that inspired this repo contains examples of hard-coded API keys in older scripts. Those files are intentionally not copied here.

