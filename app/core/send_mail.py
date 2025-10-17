from fastapi import HTTPException
from email.message import EmailMessage
import smtplib, ssl
from .config import settings

def send_email(to_email: str, subject: str, body_text: str = "", body_html: str = None):
    """
    Gửi email thông qua Mailjet SMTP.
    Hoạt động trên Render / Railway / Vercel vì Mailjet dùng cổng 587 (TLS).
    """

    # Kiểm tra cấu hình SMTP
    if not all([settings.smtp_host, settings.smtp_port, settings.smtp_user, settings.smtp_password]):
        raise HTTPException(status_code=500, detail="SMTP configuration incomplete")

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.mail_from
        msg["To"] = to_email

        # Nội dung email
        if body_html:
            msg.set_content(body_text or "This email requires HTML support.")
            msg.add_alternative(body_html, subtype="html")
        else:
            msg.set_content(body_text)

        # Kết nối SMTP Mailjet (port 587 + STARTTLS)
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls(context=context)
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        print("✅ Email sent successfully to", to_email)
        return True

    except Exception as e:
        print("❌ Error sending email:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
