from fastapi import HTTPException
from email.message import EmailMessage
import smtplib, ssl
from .config import settings

def send_email(to_email: str, subject: str, body_text: str = "", body_html: str = None):
    if not all([settings.smtp_host, settings.smtp_port, settings.smtp_user, settings.smtp_password]):
        raise HTTPException(status_code=500, detail="SMTP configuration incomplete")

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.smtp_user
        msg["To"] = to_email
        msg.set_content(body_text)
        if body_html:
            msg.add_alternative(body_html, subtype="html")

        if settings.smtp_use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as server:
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)

        return True
    except Exception as e:
        print("Error sending email:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
