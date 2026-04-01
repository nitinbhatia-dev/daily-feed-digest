"""
Configuration — loaded from environment variables or .env file.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class TwitterConfig:
    enabled: bool
    bearer_token: str
    query: str
    max_results: int = 20


@dataclass
class GitHubConfig:
    enabled: bool
    token: Optional[str]        # optional for public repos
    repos: list[str]            # ["owner/repo", ...]
    fetch_type: str = "commits" # commits | issues | pulls | releases
    per_repo: int = 5


@dataclass
class SlackConfig:
    enabled: bool
    bot_token: str
    channel_ids: list[str]
    lookback_hours: int = 24


@dataclass
class RedditConfig:
    enabled: bool
    client_id: str
    client_secret: str
    username: str
    password: str
    subreddits: list[str]       # ["MachineLearning", "programming", ...]
    sort: str = "hot"           # hot | new | top
    limit: int = 10


@dataclass
class Config:
    twitter: TwitterConfig
    github: GitHubConfig
    slack: SlackConfig
    reddit: RedditConfig
    instructions: str
    output_file: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        def _bool(key: str, default: bool = True) -> bool:
            return os.getenv(key, str(default)).lower() not in ("0", "false", "no")

        def _list(key: str, sep: str = ",") -> list[str]:
            val = os.getenv(key, "")
            return [v.strip() for v in val.split(sep) if v.strip()]

        twitter = TwitterConfig(
            enabled=_bool("TWITTER_ENABLED"),
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN", ""),
            query=os.getenv("TWITTER_QUERY", "#AINews OR #LLM"),
            max_results=int(os.getenv("TWITTER_MAX_RESULTS", "20")),
        )

        github = GitHubConfig(
            enabled=_bool("GITHUB_ENABLED"),
            token=os.getenv("GITHUB_TOKEN"),
            repos=_list("GITHUB_REPOS"),
            fetch_type=os.getenv("GITHUB_FETCH_TYPE", "commits"),
            per_repo=int(os.getenv("GITHUB_PER_REPO", "5")),
        )

        slack = SlackConfig(
            enabled=_bool("SLACK_ENABLED"),
            bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
            channel_ids=_list("SLACK_CHANNEL_IDS"),
            lookback_hours=int(os.getenv("SLACK_LOOKBACK_HOURS", "24")),
        )

        reddit = RedditConfig(
            enabled=_bool("REDDIT_ENABLED"),
            client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            username=os.getenv("REDDIT_USERNAME", ""),
            password=os.getenv("REDDIT_PASSWORD", ""),
            subreddits=_list("REDDIT_SUBREDDITS"),
            sort=os.getenv("REDDIT_SORT", "hot"),
            limit=int(os.getenv("REDDIT_LIMIT", "10")),
        )

        instructions = os.getenv(
            "DIGEST_INSTRUCTIONS",
            "Summarize the key stories, trends, and notable discussions. "
            "Group by theme where possible. Flag anything urgent or time-sensitive. "
            "Keep it concise — 3 to 5 bullet points per source.",
        )

        return cls(
            twitter=twitter,
            github=github,
            slack=slack,
            reddit=reddit,
            instructions=instructions,
            output_file=os.getenv("OUTPUT_FILE"),
        )
