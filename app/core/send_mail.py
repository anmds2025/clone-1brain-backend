from mailjet_rest import Client
from fastapi import HTTPException
from .config import settings

def send_email(to_email: str, subject: str, body_text: str = "", body_html: str = None):
    try:
        mailjet = Client(auth=(settings.smtp_user, settings.smtp_password), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": settings.mail_from,  # ✅ Verified sender
                        "Name": "1brain"
                    },
                    "To": [{"Email": to_email}],
                    "Subject": subject,
                    "TextPart": body_text or "",
                    "HTMLPart": body_html or "",
                }
            ]
        }
        result = mailjet.send.create(data=data)
        if result.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {result.json()}")
        return True
    except Exception as e:
        print("Error sending email:", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
