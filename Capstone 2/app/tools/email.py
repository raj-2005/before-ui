# app/tools/email.py

import smtplib
from email.message import EmailMessage
from typing import Optional


def send_email(
    to: str,
    subject: str,
    body: str,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    """
    Sends an email using SMTP.

    If username/password not provided,
    it will simulate sending (safe mode).
    """

    if not username or not password:
        return f"[SIMULATION MODE] Email to {to} with subject '{subject}'"

    try:
        msg = EmailMessage()
        msg["From"] = username
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)

        return f"✅ Email successfully sent to {to}"

    except smtplib.SMTPAuthenticationError:
        raise RuntimeError("❌ Authentication failed. Check your App Password.")
    except Exception as e:
        raise RuntimeError(f"❌ Email sending failed: {str(e)}")