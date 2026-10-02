"""Envoi de l'email via SMTP Gmail (mot de passe d'application)."""
import os
import re
import smtplib
from email.message import EmailMessage


def parse_recipients(raw: str) -> list[str]:
    """Accepte plusieurs adresses séparées par des virgules, points-virgules ou espaces."""
    return [a for a in re.split(r"[,\s;]+", raw) if a]


def send_email(subject: str, text: str, html: str) -> None:
    sender = os.environ["GMAIL_ADDRESS"]
    recipients = parse_recipients(os.environ["RECIPIENT_EMAIL"])
    if not recipients:
        raise ValueError("RECIPIENT_EMAIL est vide")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = sender  # les vrais destinataires sont en copie cachée (non listés dans les en-têtes)
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as smtp:
        smtp.login(sender, os.environ["GMAIL_APP_PASSWORD"])
        smtp.send_message(msg, to_addrs=recipients)
