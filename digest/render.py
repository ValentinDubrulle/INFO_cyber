"""Rendu Markdown (archive) et HTML (email) du digest."""
from datetime import date
from html import escape

from .summarize import CATEGORIES


def word_count(digest: dict) -> int:
    parts = list(digest["highlights"])
    for entries in digest["sections"].values():
        for e in entries:
            parts += [e["titre"], e["resume"]]
    return sum(len(p.split()) for p in parts)


def to_markdown(digest: dict, day: date) -> str:
    out = [f"# Digest cybersécurité — {day.strftime('%d/%m/%Y')}", "", "## À retenir", ""]
    out += [f"- {h}" for h in digest["highlights"]] or ["- Rien de majeur aujourd'hui."]
    for cat, label in CATEGORIES.items():
        entries = digest["sections"][cat]
        if not entries:
            continue
        out += ["", f"## {label}", ""]
        for e in entries:
            tag = " 🔥 KEV" if e["kev"] else ""
            out += [f"### {e['titre']}{tag}", e["resume"], "",
                    f"[{e['source']}]({e['url']})", ""]
    return "\n".join(out).rstrip() + "\n"


def to_html(digest: dict, day: date) -> str:
    h = ['<div style="font-family:Arial,sans-serif;max-width:720px;margin:auto;color:#222;line-height:1.5">',
         f'<h1 style="border-bottom:3px solid #c0392b;padding-bottom:6px">Digest cybersécurité — {day.strftime("%d/%m/%Y")}</h1>',
         '<h2>À retenir</h2><ul>']
    h += [f"<li>{escape(x)}</li>" for x in digest["highlights"]] or ["<li>Rien de majeur aujourd'hui.</li>"]
    h.append("</ul>")
    for cat, label in CATEGORIES.items():
        entries = digest["sections"][cat]
        if not entries:
            continue
        h.append(f'<h2 style="margin-top:32px;color:#c0392b">{label}</h2>')
        for e in entries:
            tag = ' <span style="background:#c0392b;color:#fff;font-size:11px;padding:1px 6px;border-radius:3px">KEV</span>' if e["kev"] else ""
            h.append(
                f'<h3 style="margin-bottom:4px">{escape(e["titre"])}{tag}</h3>'
                f'<p style="margin:4px 0">{escape(e["resume"])}</p>'
                f'<p style="margin:2px 0 16px;font-size:13px"><a href="{escape(e["url"], quote=True)}">{escape(e["source"])} →</a></p>'
            )
    h.append('<hr><p style="color:#888;font-size:12px">Généré par un modèle de langage : se référer à la source originale pour toute décision de sécurité.</p></div>')
    return "\n".join(h)
