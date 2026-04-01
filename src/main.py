"""
Daily Feed Digest Agent
Fetches from Twitter/X, GitHub, Slack, and Reddit — summarized by Claude.
"""

import asyncio
import sys
from datetime import datetime

from .config import Config
from .fetchers.twitter import fetch_twitter
from .fetchers.github import fetch_github
from .fetchers.slack import fetch_slack
from .fetchers.reddit import fetch_reddit
from .summarizer import summarize_source, synthesize_all
from .output import print_digest, save_digest


async def run_digest(config: Config) -> dict:
    sources = {}

    fetchers = {
        "twitter": (fetch_twitter, config.twitter),
        "github":  (fetch_github,  config.github),
        "slack":   (fetch_slack,   config.slack),
        "reddit":  (fetch_reddit,  config.reddit),
    }

    for name, (fetcher, cfg) in fetchers.items():
        if not cfg.enabled:
            print(f"  ⊘  {name} — skipped")
            continue
        print(f"  ↓  {name} — fetching…", end="", flush=True)
        try:
            raw = await fetcher(cfg)
            print(f"\r  ✓  {name} — fetched {len(raw.splitlines())} items, summarizing…", end="", flush=True)
            summary = await summarize_source(name, raw, config.instructions)
            sources[name] = summary
            print(f"\r  ✓  {name} — done{' ' * 20}")
        except Exception as e:
            print(f"\r  ✗  {name} — error: {e}{' ' * 20}")

    digest = None
    if len(sources) >= 2:
        print("  ↓  synthesizing cross-source digest…", end="", flush=True)
        try:
            digest = await synthesize_all(sources, config.instructions)
            print(f"\r  ✓  digest — done{' ' * 20}")
        except Exception as e:
            print(f"\r  ✗  digest — error: {e}")

    return {"sources": sources, "digest": digest, "timestamp": datetime.now().isoformat()}


def main():
    config = Config.from_env()
    print(f"\n🗞  Daily Feed Digest — {datetime.now().strftime('%A, %d %b %Y')}\n")
    result = asyncio.run(run_digest(config))
    print()
    print_digest(result)
    if config.output_file:
        save_digest(result, config.output_file)
        print(f"\n📄  Saved to {config.output_file}")
    print()


if __name__ == "__main__":
    main()
