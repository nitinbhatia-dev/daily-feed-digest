"""Summarization via the Anthropic Claude API."""

import os
import anthropic

_client: anthropic.AsyncAnthropic | None = None

SOURCE_LABELS = {
    "twitter": "Twitter/X",
    "github":  "GitHub",
    "slack":   "Slack",
    "reddit":  "Reddit",
}


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


async def summarize_source(source: str, raw_content: str, instructions: str) -> str:
    label = SOURCE_LABELS.get(source, source)
    prompt = (
        f"You are a daily feed digest agent. Below is the raw content fetched from {label}.\n\n"
        f"{raw_content}\n\n"
        f"Instructions: {instructions}\n\n"
        f"Summarize only this source's content. Use bullet points. Be concise and direct. No preamble."
    )
    client = _get_client()
    msg = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


async def synthesize_all(summaries: dict[str, str], instructions: str) -> str:
    combined = "\n\n".join(
        f"=== {SOURCE_LABELS.get(k, k).upper()} ===\n{v}"
        for k, v in summaries.items()
    )
    prompt = (
        "You are a daily digest agent. Here are individual source summaries:\n\n"
        f"{combined}\n\n"
        "Write a sharp 3–4 sentence cross-source synthesis. "
        "What are the dominant themes today? "
        "Any tensions or notable overlaps between sources? "
        "What should the reader pay most attention to? Be direct."
    )
    client = _get_client()
    msg = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
