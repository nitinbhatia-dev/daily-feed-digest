"""Slack fetcher — uses the Web API conversations.history endpoint."""

import time
import httpx
from ..config import SlackConfig


async def fetch_slack(cfg: SlackConfig) -> str:
    if not cfg.bot_token:
        raise ValueError("SLACK_BOT_TOKEN is not set")
    if not cfg.channel_ids:
        raise ValueError("SLACK_CHANNEL_IDS is not set")

    oldest = str(time.time() - cfg.lookback_hours * 3600)
    lines = []

    async with httpx.AsyncClient(base_url="https://slack.com", timeout=15) as client:
        headers = {"Authorization": f"Bearer {cfg.bot_token}"}

        # Resolve channel names for readability
        ch_names: dict[str, str] = {}
        try:
            info_res = await client.get("/api/conversations.list?limit=200", headers=headers)
            for ch in info_res.json().get("channels", []):
                ch_names[ch["id"]] = ch["name"]
        except Exception:
            pass

        for ch_id in cfg.channel_ids[:8]:
            ch_label = ch_names.get(ch_id, ch_id)
            res = await client.get(
                f"/api/conversations.history?channel={ch_id}&oldest={oldest}&limit=30",
                headers=headers,
            )
            data = res.json()
            if not data.get("ok"):
                lines.append(f"\n=== #{ch_label} ===\n  Error: {data.get('error', 'unknown')}")
                continue

            messages = [m for m in data.get("messages", []) if not m.get("subtype")]
            lines.append(f"\n=== #{ch_label} ({len(messages)} messages) ===")
            for m in messages[:15]:
                text = m.get("text", "").replace("\n", " ")[:300]
                if text:
                    lines.append(f"  • {text}")

    return "\n".join(lines).strip()
