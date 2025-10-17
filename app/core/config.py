import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    app_name: str = "FastAPI Clerk Backend"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "info")
    allowed_origins = ["*"]
    allowed_methods = ["*"]
    allowed_headers = ["*"]
    clerk_secret_key: str = os.getenv("CLERK_SECRET_KEY", "")
    clerk_frontend_api: str = os.getenv("CLERK_FRONTEND_API", "")
    front_end_link: str = os.getenv("FRONT_END_LINK", "")

    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "false").lower() in ("1", "true", "yes")
    smtp_host: str = os.getenv("SMTP_HOST", "")
    mail_from: str = os.getenv("MAIL_FROM", "")

settings = Settings()
