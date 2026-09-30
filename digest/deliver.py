"""Envoi de l'email via SMTP Gmail (mot de passe d'application)."""
import os
import smtplib
from email.message import EmailMessage


def send_email(subject: str, text: str, html: str) -> None:
    sender = os.environ["GMAIL_ADDRESS"]
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = os.environ["RECIPIENT_EMAIL"]
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as smtp:
        smtp.login(sender, os.environ["GMAIL_APP_PASSWORD"])
        smtp.send_message(msg)
