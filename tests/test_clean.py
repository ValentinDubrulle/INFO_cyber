from datetime import datetime, timedelta, timezone

from digest import clean
from digest.models import Item

NOW = datetime(2026, 9, 30, 6, 0, tzinfo=timezone.utc)
S = {"window_hours": 24, "kev_window_days": 2}


def item(id, title, url, hours_ago, kind="article"):
    return Item(id, title, url, "src", NOW - timedelta(hours=hours_ago), kind=kind)


def test_window_dedup_and_seen():
    items = [
        item("1", "Alpha", "https://www.a.com/x/", 2),
        item("2", "Alpha bis", "https://a.com/x", 3),      # même URL normalisée
        item("3", "ALPHA", "https://b.com/y", 4),          # même titre normalisé
        item("4", "Old", "https://c.com/z", 30),           # hors fenêtre
        item("5", "Seen", "https://d.com/w", 1),
        item("kev:CVE-1", "KEV", "https://nvd/CVE-1", 40, kind="kev"),  # KEV : fenêtre 2 jours
    ]
    seen = {clean.norm_url("https://d.com/w"): "x"}
    out = clean.clean(items, seen, S, NOW)
    assert {i.id for i in out} == {"1", "kev:CVE-1"}
