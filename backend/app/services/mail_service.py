import smtplib
from email.mime.text import MIMEText
from ..core.config import Settings

def send_email_code(email: str, code: str):
    if not Settings.SMTP_USER or not Settings.SMTP_PASSWORD:
        print("SMTP credentials are not configured, skipping email send")
        return

    msg = MIMEText(f"Ваш код подтверждения: {code}")
    msg["Subject"] = "Подтверждение почты"
    msg["From"] = Settings.SMTP_USER
    msg["To"] = email

    with smtplib.SMTP(Settings.SMTP_HOST, Settings.SMTP_PORT) as server:
        server.starttls()
        server.login(Settings.SMTP_USER, Settings.SMTP_PASSWORD)
        server.send_message(msg)