"""Point d'entrée : collecte -> nettoyage -> synthèse -> archive -> email."""
import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from dotenv import load_dotenv

from . import clean, collect, deliver, render, summarize

ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger("digest")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="n'envoie rien et ne met pas à jour la mémoire")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    load_dotenv(ROOT / ".env")

    config = yaml.safe_load((ROOT / "config" / "sources.yaml").read_text())
    settings = config["settings"]
    now = datetime.now(timezone.utc)
    seen_path = ROOT / "data" / "seen.json"
    seen = clean.load_seen(seen_path)

    items = clean.clean(collect.collect_all(config), seen, settings, now)
    log.info("%d nouveaux éléments après nettoyage", len(items))
    if not items:
        log.info("Rien de nouveau : aucun email envoyé.")
        return 0
    items = items[:settings["max_items"]]

    digest = summarize.build_digest(items, settings)
    if not digest["count"]:
        log.error("Aucune synthèse produite (Gemini indisponible ?)")
        return 1

    day = now.astimezone(ZoneInfo("Europe/Paris")).date()
    md = render.to_markdown(digest, day)
    log.info("Digest : %d éléments, ~%d mots", digest["count"], render.word_count(digest))
    if args.dry_run:
        print(md)
        return 0

    archive = ROOT / "digests" / f"{day.isoformat()}.md"
    archive.parent.mkdir(exist_ok=True)
    archive.write_text(md)
    deliver.send_email(f"Digest cyber du {day.strftime('%d/%m/%Y')}", md, render.to_html(digest, day))

    # Mémoire mise à jour uniquement pour les éléments réellement résumés et envoyés.
    for idx in digest["summarized_ids"]:
        for key in clean.item_keys(items[idx]):
            seen[key] = now.isoformat()
    clean.save_seen(seen_path, seen, now, settings["seen_retention_days"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
