from typing import Any, Dict
from fastapi import HTTPException, Request
from app.core.config import settings
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions

import logging
logger = logging.getLogger(__name__)

def _get_clerk_client() -> Clerk:
    return Clerk(bearer_auth=settings.clerk_secret_key)

def _authorized_parties() -> list[str]:
    return [settings.front_end_link]

async def require_clerk_identity(request: Request) -> Dict[str, Any]:
    clerk_client = _get_clerk_client()
    try:
        auth_state = clerk_client.authenticate_request(
            request,
            AuthenticateRequestOptions(authorized_parties=_authorized_parties()),
        )

        if not getattr(auth_state, "is_signed_in", False):
            logger.warning("❌ Clerk auth failed: %s", getattr(auth_state, "reason", None))
            raise HTTPException(status_code=401, detail="Invalid or expired session token")

        claims: Dict[str, Any] = getattr(auth_state, "payload", None) or {}

        clerk_id = claims.get("sub") or claims.get("clerk_id") or getattr(auth_state, "user_id", None)

        if not clerk_id:
            raise HTTPException(status_code=401, detail="Missing clerk_id in token")

        logger.info("✅ Clerk auth OK for clerk_id=%s", clerk_id)
        return {"clerk_id": clerk_id, "claims": claims}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clerk authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid Clerk token")
