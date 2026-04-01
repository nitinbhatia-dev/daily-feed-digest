# 🗞 Daily Feed Digest

An AI-powered CLI agent that fetches your daily feeds from **Twitter/X**, **GitHub**, **Slack**, and **Reddit** — then uses Claude to summarize each source and produce a sharp cross-source synthesis.

## Features

- Fetches from all 4 sources concurrently
- Per-source Claude summary with your custom instructions
- Cross-source synthesis to surface dominant themes
- Saves output as `.md`, `.json`, or `.txt`
- GitHub Actions workflow for automated daily runs (9:30 AM IST by default)

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/daily-feed-digest
cd daily-feed-digest
pip install -e .

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Run
python -m src.main
# or
digest
```

## Configuration

Copy `.env.example` to `.env` and fill in your keys. All settings are via environment variables.

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | Your Anthropic API key |
| `TWITTER_BEARER_TOKEN` | Twitter | From [developer.twitter.com](https://developer.twitter.com) |
| `TWITTER_QUERY` | Twitter | Search query e.g. `#AINews OR from:sama` |
| `GITHUB_TOKEN` | Optional | PAT for private repos; public repos work without |
| `GITHUB_REPOS` | GitHub | Comma-separated `owner/repo` list |
| `GITHUB_FETCH_TYPE` | GitHub | `commits`, `issues`, `pulls`, or `releases` |
| `SLACK_BOT_TOKEN` | Slack | Bot token with `channels:history` scope |
| `SLACK_CHANNEL_IDS` | Slack | Comma-separated channel IDs |
| `REDDIT_CLIENT_ID` | Reddit | From [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) (script app) |
| `REDDIT_CLIENT_SECRET` | Reddit | Script app secret |
| `REDDIT_USERNAME` | Reddit | Your Reddit username |
| `REDDIT_PASSWORD` | Reddit | Your Reddit password |
| `REDDIT_SUBREDDITS` | Reddit | Comma-separated subreddit names (no `r/`) |
| `OUTPUT_FILE` | Optional | Save path: `digest.md`, `digest.json`, or `digest.txt` |
| `DIGEST_INSTRUCTIONS` | Optional | Custom instructions for the Claude summarizer |

## Enabling individual sources

Each source can be toggled independently:

```bash
TWITTER_ENABLED=false   # skip Twitter entirely
GITHUB_ENABLED=true
SLACK_ENABLED=true
REDDIT_ENABLED=true
```

## Automated daily runs (GitHub Actions)

The included workflow runs every day at 9:30 AM IST. To enable it:

1. Push this repo to GitHub
2. Go to **Settings → Secrets and variables → Actions**
3. Add all your API keys as **Secrets**
4. Add non-secret config (queries, repos, channels) as **Variables**
5. Go to **Actions → Daily Feed Digest → Run workflow** to test

The digest is uploaded as a workflow artifact and retained for 30 days.

## Project structure

```
daily-feed-digest/
├── src/
│   ├── main.py          # CLI entry point + agent loop
│   ├── config.py        # Config dataclass loaded from env
│   ├── summarizer.py    # Claude API calls
│   ├── output.py        # Terminal + file output
│   └── fetchers/
│       ├── twitter.py   # Twitter v2 search API
│       ├── github.py    # GitHub REST API v3
│       ├── slack.py     # Slack Web API
│       └── reddit.py    # Reddit OAuth + REST API
├── .github/
│   └── workflows/
│       └── daily.yml    # Scheduled GitHub Actions workflow
├── .env.example
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.11+
- An Anthropic API key
- API credentials for whichever sources you want to enable
