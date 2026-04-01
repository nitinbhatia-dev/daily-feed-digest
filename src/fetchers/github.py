"""GitHub fetcher — uses the REST API v3."""

import httpx
from ..config import GitHubConfig


ENDPOINTS = {
    "commits":  "/repos/{repo}/commits?per_page={n}",
    "issues":   "/repos/{repo}/issues?state=open&per_page={n}",
    "pulls":    "/repos/{repo}/pulls?state=open&per_page={n}",
    "releases": "/repos/{repo}/releases?per_page={n}",
}


async def fetch_github(cfg: GitHubConfig) -> str:
    if not cfg.repos:
        raise ValueError("GITHUB_REPOS is not set")

    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if cfg.token:
        headers["Authorization"] = f"Bearer {cfg.token}"

    endpoint_tpl = ENDPOINTS.get(cfg.fetch_type, ENDPOINTS["commits"])
    lines = []

    async with httpx.AsyncClient(base_url="https://api.github.com", timeout=15, headers=headers) as client:
        for repo in cfg.repos[:8]:
            url = endpoint_tpl.format(repo=repo, n=cfg.per_repo)
            res = await client.get(url)
            if res.status_code == 404:
                lines.append(f"[{repo}] Not found (private repo or typo?)")
                continue
            if res.status_code == 403:
                lines.append(f"[{repo}] Rate limited or no access")
                continue
            res.raise_for_status()
            items = res.json()

            lines.append(f"\n=== {repo} ({cfg.fetch_type}) ===")
            for item in items[:cfg.per_repo]:
                if cfg.fetch_type == "commits":
                    msg = item["commit"]["message"].split("\n")[0]
                    author = item["commit"]["author"]["name"]
                    lines.append(f"  • {msg}  — {author}")
                elif cfg.fetch_type in ("issues", "pulls"):
                    num   = item["number"]
                    title = item["title"]
                    login = item.get("user", {}).get("login", "?")
                    lines.append(f"  • #{num} {title}  (@{login})")
                elif cfg.fetch_type == "releases":
                    name = item.get("name") or item.get("tag_name", "?")
                    date = item.get("published_at", "")[:10]
                    lines.append(f"  • {name}  ({date})")

    return "\n".join(lines).strip()
