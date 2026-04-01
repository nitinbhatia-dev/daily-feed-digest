"""Terminal output and file saving."""

import json
from datetime import datetime
from pathlib import Path


ICONS = {
    "twitter": "𝕏",
    "github":  "⊙",
    "slack":   "#",
    "reddit":  "◉",
}

LABELS = {
    "twitter": "Twitter / X",
    "github":  "GitHub",
    "slack":   "Slack",
    "reddit":  "Reddit",
}


def print_digest(result: dict) -> None:
    sources = result.get("sources", {})
    digest  = result.get("digest")

    for key, summary in sources.items():
        icon  = ICONS.get(key, "•")
        label = LABELS.get(key, key.title())
        bar   = "─" * (len(label) + 4)
        print(f"┌─{bar}─┐")
        print(f"│  {icon}  {label}  │")
        print(f"└─{bar}─┘")
        for line in summary.strip().splitlines():
            print(f"  {line}")
        print()

    if digest:
        print("━" * 52)
        print("  Cross-source synthesis")
        print("━" * 52)
        for line in digest.strip().splitlines():
            print(f"  {line}")
        print()


def save_digest(result: dict, path: str) -> None:
    p = Path(path)
    ext = p.suffix.lower()

    if ext == ".json":
        p.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    elif ext == ".md":
        _save_markdown(result, p)
    else:
        # Plain text fallback
        lines = []
        ts = result.get("timestamp", datetime.now().isoformat())
        lines.append(f"# Daily Feed Digest — {ts}\n")
        for key, summary in result.get("sources", {}).items():
            lines.append(f"## {LABELS.get(key, key.title())}\n")
            lines.append(summary.strip())
            lines.append("")
        if result.get("digest"):
            lines.append("## Cross-source synthesis\n")
            lines.append(result["digest"].strip())
        p.write_text("\n".join(lines))


def _save_markdown(result: dict, path: Path) -> None:
    ts = result.get("timestamp", datetime.now().isoformat())
    date_str = ts[:10]
    lines = [f"# Daily Feed Digest — {date_str}\n"]
    for key, summary in result.get("sources", {}).items():
        icon  = ICONS.get(key, "•")
        label = LABELS.get(key, key.title())
        lines.append(f"## {icon} {label}\n")
        lines.append(summary.strip())
        lines.append("")
    if result.get("digest"):
        lines.append("## Cross-source synthesis\n")
        lines.append(result["digest"].strip())
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
