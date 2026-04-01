# CLAUDE.md — Daily Feed Digest

This file tells Claude Code how to work with this project.

## Project overview

A Python CLI agent that fetches daily feeds from Twitter/X, GitHub, Slack, and Reddit, then uses the Anthropic Claude API to produce per-source summaries and a cross-source synthesis. Runs as a scheduled GitHub Actions workflow at 9:30 AM IST.

## Project structure

```
src/
  main.py          — CLI entry point and async agent loop
  config.py        — Config dataclass loaded from environment variables
  summarizer.py    — All Claude API calls (per-source + synthesis)
  output.py        — Terminal printing and file output (.md / .json / .txt)
  fetchers/
    twitter.py     — Twitter v2 recent search API
    github.py      — GitHub REST API v3 (commits, issues, PRs, releases)
    slack.py       — Slack Web API (conversations.history)
    reddit.py      — Reddit OAuth2 password grant + REST API
.github/workflows/
  daily.yml        — Scheduled GitHub Actions workflow
```

## Commands

```bash
# Install
pip install -e .

# Run the agent
python -m src.main
# or after install:
digest

# Run a single fetcher in isolation (useful for debugging)
python -c "
import asyncio
from src.config import Config
from src.fetchers.github import fetch_github
c = Config.from_env()
print(asyncio.run(fetch_github(c.github)))
"
```

## Environment setup

Copy `.env.example` to `.env` and fill in credentials. All configuration is via environment variables — no config files. See `.env.example` for the full list.

Minimum required:
- `ANTHROPIC_API_KEY` — always required
- Per-source tokens (only needed for enabled sources)

## Architecture

The agent runs sources **sequentially** (not concurrently) to keep error output readable and avoid rate-limit pile-ups. Each source follows: fetch raw content → pass to Claude for summarization. After all sources complete, a second Claude call synthesizes across sources.

The `Config.from_env()` pattern means you can override any setting by setting an env var — no code changes needed.

## Adding a new source

1. Create `src/fetchers/yourservice.py` with an `async def fetch_yourservice(cfg) -> str` function that returns raw text lines
2. Add a config dataclass in `src/config.py` and wire it into `Config.from_env()`
3. Register the fetcher in `src/main.py` in the `fetchers` dict
4. Add the relevant env vars to `.env.example`

## Key dependencies

- `anthropic` — Claude API (use `claude-sonnet-4-20250514` model)
- `httpx` — async HTTP for all 4 API fetchers
- `python-dotenv` — loads `.env` file automatically

## GitHub Actions

The workflow in `.github/workflows/daily.yml` runs at `0 4 * * *` UTC (9:30 AM IST). All secrets go in **Settings → Secrets and variables → Actions → Secrets**. Non-secret config (queries, repo lists, subreddits) goes in **Variables** in the same section.

The digest output is uploaded as a workflow artifact (`digest.md`) and retained for 30 days.

## Common tasks

**Change the Claude model**: edit the `model=` argument in `src/summarizer.py`

**Change the schedule**: edit the `cron:` line in `.github/workflows/daily.yml` (use UTC)

**Add email delivery**: after `synthesize_all()` in `main.py`, add an smtp or SendGrid call using the `digest` string

**Disable a source without touching code**: set `TWITTER_ENABLED=false` in `.env`

## Style conventions

- Async throughout — use `httpx.AsyncClient` for all HTTP, `anthropic.AsyncAnthropic` for Claude
- Raise `ValueError` for bad config, `RuntimeError` for API-level errors (rate limits, etc.)
- Each fetcher returns a plain multiline string — no structured objects passed to Claude
- Keep fetchers stateless and independently testable
