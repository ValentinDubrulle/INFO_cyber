"""Filtre temporel, dédoublonnage et mémoire des articles déjà vus."""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

from .models import Item


def norm_url(url: str) -> str:
    p = urlsplit(url)
    return f"{p.netloc.lower().removeprefix('www.')}{p.path.rstrip('/')}"


def norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def load_seen(path: Path) -> dict[str, str]:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_seen(path: Path, seen: dict[str, str], now: datetime, retention_days: int) -> None:
    cutoff = (now - timedelta(days=retention_days)).isoformat()
    kept = {k: v for k, v in seen.items() if v >= cutoff}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(kept, indent=0, sort_keys=True))


def clean(items: list[Item], seen: dict[str, str], settings: dict, now: datetime) -> list[Item]:
    out, urls, titles = [], set(), set()
    for it in sorted(items, key=lambda i: i.published, reverse=True):
        window = timedelta(days=settings["kev_window_days"]) if it.kind == "kev" \
            else timedelta(hours=settings["window_hours"])
        if now - it.published > window or it.published > now + timedelta(hours=1):
            continue
        key = norm_url(it.url)
        if key in seen or it.id in seen or key in urls or norm_title(it.title) in titles:
            continue
        urls.add(key)
        titles.add(norm_title(it.title))
        out.append(it)
    return out


def item_keys(item: Item) -> list[str]:
    return [norm_url(item.url), item.id]
