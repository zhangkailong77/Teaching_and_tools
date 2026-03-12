from datetime import timedelta
from typing import Any, Callable, Dict
from uuid import uuid4

from jose import JWTError, jwt

from app.core import security
from app.core.config import settings
from app.core.redis import consume_once_key, set_once_key

FEDERATION_TICKET_TYPE = "federation_sso_ticket"
FEDERATION_TICKET_KEY_PREFIX = "federation:sso:jti:"


def _jti_key(jti: str) -> str:
    return f"{FEDERATION_TICKET_KEY_PREFIX}{jti}"


def issue_federation_ticket(
    *,
    user_id: int,
    username: str,
    role: str,
    school_id: str,
    ttl_seconds: int,
    store_jti_fn: Callable[[str, int], bool] = set_once_key,
) -> Dict[str, Any]:
    jti = uuid4().hex
    if not store_jti_fn(_jti_key(jti), ttl_seconds):
        raise ValueError("failed to store federation ticket nonce")

    ticket = security.create_access_token(
        subject={
            "typ": FEDERATION_TICKET_TYPE,
            "jti": jti,
            "sub": username,
            "uid": user_id,
            "role": role,
            "school_id": school_id,
        },
        expires_delta=timedelta(seconds=ttl_seconds),
    )
    return {"ticket": ticket, "expires_in": ttl_seconds}


def consume_federation_ticket(
    *,
    ticket: str,
    consume_jti_fn: Callable[[str], bool] = consume_once_key,
) -> Dict[str, Any]:
    try:
        payload = jwt.decode(ticket, settings.secret_key, algorithms=[security.ALGORITHM])
    except JWTError as exc:
        raise ValueError("invalid federation ticket") from exc

    if payload.get("typ") != FEDERATION_TICKET_TYPE:
        raise ValueError("invalid federation ticket type")

    jti = payload.get("jti")
    if not jti:
        raise ValueError("missing federation ticket jti")

    if not consume_jti_fn(_jti_key(jti)):
        raise ValueError("federation ticket already used or expired")

    return {
        "user_id": payload.get("uid"),
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "school_id": payload.get("school_id"),
    }
