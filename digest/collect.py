"""Collecte des flux RSS et du catalogue CISA KEV."""
import calendar
import html
import logging
import re
from datetime import datetime, timezone

import feedparser
import requests

from .models import Item

log = logging.getLogger(__name__)
UA = {"User-Agent": "cyber-daily-digest/1.0 (+https://github.com/ValentinDubrulle/INFO_cyber)"}
TAG_RE = re.compile(r"<[^>]+>")


def _clean_text(raw: str, limit: int = 3000) -> str:
    text = html.unescape(TAG_RE.sub(" ", raw or ""))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _entry_date(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)
    return None


def collect_feed(feed: dict) -> list[Item]:
    resp = requests.get(feed["url"], headers=UA, timeout=30)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    items = []
    for e in parsed.entries:
        date = _entry_date(e)
        url = e.get("link")
        if not date or not url:
            continue
        body = e["content"][0]["value"] if e.get("content") else e.get("summary", "")
        items.append(Item(
            id=e.get("id") or url,
            title=_clean_text(e.get("title", ""), 300),
            url=url,
            source=feed["name"],
            published=date,
            text=_clean_text(body),
        ))
    return items


def collect_kev(cfg: dict) -> list[Item]:
    resp = requests.get(cfg["url"], headers=UA, timeout=60)
    resp.raise_for_status()
    items = []
    for v in resp.json().get("vulnerabilities", []):
        cve = v["cveID"]
        added = datetime.strptime(v["dateAdded"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        text = (
            f"{v.get('vendorProject', '')} {v.get('product', '')} : {v.get('vulnerabilityName', '')}. "
            f"{v.get('shortDescription', '')} Action requise : {v.get('requiredAction', '')} "
            f"Échéance CISA : {v.get('dueDate', '?')}. "
            f"Utilisée dans des campagnes ransomware : {v.get('knownRansomwareCampaignUse', 'Unknown')}."
        )
        items.append(Item(
            id=f"kev:{cve}",
            title=f"{cve} ajoutée au catalogue KEV ({v.get('vendorProject', '')} {v.get('product', '')})".strip(),
            url=f"https://nvd.nist.gov/vuln/detail/{cve}",
            source="CISA KEV",
            published=added,
            text=_clean_text(text),
            kind="kev",
        ))
    return items


def collect_all(config: dict) -> list[Item]:
    items: list[Item] = []
    for feed in config["feeds"]:
        try:
            got = collect_feed(feed)
            log.info("%s : %d entrées", feed["name"], len(got))
            items += got
        except Exception as exc:  # une source en panne ne doit pas bloquer le digest
            log.warning("Source %s ignorée : %s", feed["name"], exc)
    if config.get("kev", {}).get("enabled"):
        try:
            got = collect_kev(config["kev"])
            log.info("CISA KEV : %d entrées", len(got))
            items += got
        except Exception as exc:
            log.warning("CISA KEV ignoré : %s", exc)
    return items
