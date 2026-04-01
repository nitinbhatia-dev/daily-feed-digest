"""Reddit fetcher — uses OAuth2 password grant for script apps."""

import httpx
from ..config import RedditConfig

USER_AGENT = "daily-feed-digest/1.0 (by /u/{username})"


async def _get_token(cfg: RedditConfig, client: httpx.AsyncClient) -> str:
    if not all([cfg.client_id, cfg.client_secret, cfg.username, cfg.password]):
        raise ValueError(
            "Reddit requires REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, "
            "REDDIT_USERNAME, and REDDIT_PASSWORD"
        )

    res = await client.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(cfg.client_id, cfg.client_secret),
        data={
            "grant_type": "password",
            "username": cfg.username,
            "password": cfg.password,
        },
        headers={"User-Agent": USER_AGENT.format(username=cfg.username)},
    )
    res.raise_for_status()
    data = res.json()
    if "error" in data:
        raise ValueError(f"Reddit auth failed: {data['error']}")
    return data["access_token"]


async def fetch_reddit(cfg: RedditConfig) -> str:
    if not cfg.subreddits:
        raise ValueError("REDDIT_SUBREDDITS is not set")

    ua = USER_AGENT.format(username=cfg.username or "anonymous")

    async with httpx.AsyncClient(timeout=15) as client:
        token = await _get_token(cfg, client)
        headers = {"Authorization": f"Bearer {token}", "User-Agent": ua}

        lines = []
        for sub in cfg.subreddits[:8]:
            params = {"limit": cfg.limit}
            if cfg.sort == "top":
                params["t"] = "day"

            res = await client.get(
                f"https://oauth.reddit.com/r/{sub}/{cfg.sort}",
                params=params,
                headers=headers,
            )
            if res.status_code == 404:
                lines.append(f"\n=== r/{sub} ===\n  Subreddit not found")
                continue
            res.raise_for_status()

            posts = res.json().get("data", {}).get("children", [])
            lines.append(f"\n=== r/{sub} ({cfg.sort}) ===")
            for p in posts:
                d = p["data"]
                score    = d.get("score", 0)
                title    = d.get("title", "")
                comments = d.get("num_comments", 0)
                flair    = d.get("link_flair_text") or ""
                flair_str = f" [{flair}]" if flair else ""
                lines.append(f"  • [{score:,} pts]{flair_str} {title}  ({comments} comments)")

    return "\n".join(lines).strip()
