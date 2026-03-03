from functools import lru_cache

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings


@lru_cache(maxsize=1)
def _fetch_jwks() -> list[dict]:
    """Fetch Supabase public JWKS once and cache for the process lifetime."""
    url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    resp = httpx.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json().get("keys", [])


def validate_token(token: str) -> dict:
    """Validate a Supabase JWT (ES256 or legacy HS256) and return the decoded payload."""
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")

        if alg == "ES256":
            keys = _fetch_jwks()
            kid = header.get("kid")
            # Match by kid, fall back to first key
            key = next((k for k in keys if k.get("kid") == kid), None) or (keys[0] if keys else None)
            if key is None:
                raise JWTError("No public key available")
            payload: dict = jwt.decode(
                token,
                key,
                algorithms=["ES256"],
                options={"verify_aud": False},
            )
        else:
            # Legacy HS256 (projects that haven't rotated to ECC yet)
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
