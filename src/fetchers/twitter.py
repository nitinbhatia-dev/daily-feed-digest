"""Twitter/X fetcher — uses the v2 recent search endpoint."""

import httpx
from ..config import TwitterConfig


async def fetch_twitter(cfg: TwitterConfig) -> str:
    if not cfg.bearer_token:
        raise ValueError("TWITTER_BEARER_TOKEN is not set")

    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": cfg.query,
        "max_results": min(max(cfg.max_results, 10), 100),
        "tweet.fields": "created_at,author_id,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,name",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {cfg.bearer_token}"},
        )

    if res.status_code == 401:
        raise ValueError("Invalid Twitter bearer token")
    if res.status_code == 429:
        raise RuntimeError("Twitter rate limit exceeded — try again later")
    res.raise_for_status()

    data = res.json()
    users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
    tweets = data.get("data", [])

    if not tweets:
        return "No tweets found for this query."

    lines = []
    for t in tweets:
        user = users.get(t["author_id"], {})
        handle = user.get("username", t["author_id"])
        metrics = t.get("public_metrics", {})
        likes = metrics.get("like_count", 0)
        rts   = metrics.get("retweet_count", 0)
        lines.append(f"@{handle}: {t['text']}  [❤ {likes}  RT {rts}]")

    return "\n".join(lines)
