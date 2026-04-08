from __future__ import annotations

import time
import uuid
from typing import Final

import jwt

from app.core.config import settings

JWT_ALG: Final[str] = "HS256"


def issue_session() -> tuple[str, str]:
    """
    Create a new signed session token for the current user (MVP).

    Returns:
        (user_id, token)
    """

    user_id = uuid.uuid4().hex
    now = int(time.time())
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + settings.auth_token_ttl_seconds,
    }
    token = jwt.encode(payload, settings.auth_secret, algorithm=JWT_ALG)
    return user_id, token


def verify_session(token: str) -> str:
    """
    Verify and decode a signed session token.

    Args:
        token: Bearer token string.

    Returns:
        user_id encoded in the token.
    """

    try:
        payload = jwt.decode(token, settings.auth_secret, algorithms=[JWT_ALG])
        sub = payload.get("sub")
        if not isinstance(sub, str) or not sub:
            raise jwt.InvalidTokenError("Invalid token subject.")
        return sub
    except jwt.ExpiredSignatureError as e:
        raise PermissionError("Session token expired.") from e
    except jwt.PyJWTError as e:
        raise PermissionError("Invalid session token.") from e


def try_get_user_id_from_authorization(authorization: str | None) -> str | None:
    """
    Extract a bearer token from `Authorization` header and verify it.

    Returns:
        user_id if valid, otherwise None.
    """

    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return verify_session(token)
    except PermissionError:
        return None

