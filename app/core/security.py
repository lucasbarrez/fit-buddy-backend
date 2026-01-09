"""
Security utilities for JWT verification from Next.js (Better Auth)
"""

import base64
import hashlib
import hmac
from datetime import UTC, datetime
from typing import Any
from urllib.parse import unquote

from sqlalchemy import text

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.logging import app_logger
from app.core.user_db import async_session_factory


def verify_session_signature(session_token: str, secret: str) -> bool:
    """
    Verify the signature of a session token
    Format: "data.signature"
    """
    try:
        parts = session_token.split(".")
        if len(parts) != 2:
            return False

        data_encoded = parts[0]
        signature_encoded = parts[1]

        # URL decode data and signature
        data = unquote(data_encoded)
        # Add padding for base64 decoding if needed
        padding = "=" * (4 - len(unquote(signature_encoded)) % 4)
        signature_expected_bytes = base64.urlsafe_b64decode(unquote(signature_encoded) + padding)

        # Calculate HMAC-SHA256 signature
        hmac_obj = hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256)
        signature_actual_bytes = hmac_obj.digest()

        # Compare signatures
        return hmac.compare_digest(signature_actual_bytes, signature_expected_bytes)

    except Exception as e:
        app_logger.error(f"Signature verification failed: {e}")
        return False


async def verify_session_token(token: str) -> dict[str, Any]:
    """
    Verify Better Auth session token
    1. Verify HMAC signature
    2. Check DB for session validity and expiry
    3. Return user data

    Format:
    "data.signature" => We extract the "data" part after having verified the signature
    """
    # 1. Verify Signature
    if not verify_session_signature(token, settings.BETTER_AUTH_SECRET):
        raise UnauthorizedException(
            message="Invalid session signature", details={"error": "invalid_signature"}
        )

    # Extract clean token (the data part before the dot)
    clean_token = unquote(token.split(".")[0])

    # 2. Lookup Session in DB (PostgreSQL / Prisma)
    async with async_session_factory() as session:
        try:
            # Sanitize => ORM
            query = text(
                """
                SELECT
                    s."expiresAt",
                    u.id, u.email, u.name, u."emailVerified"
                FROM session s
                JOIN "user" u ON s."userId" = u.id
                WHERE s.token = :token
                """
            )

            result = await session.execute(query, {"token": clean_token})
            row = result.mappings().one_or_none()

            if not row:
                raise UnauthorizedException(message="Session not found")

            # 3. Check Expiry
            expires_at = row["expiresAt"]
            print("expires_at", expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=UTC)

            if expires_at < datetime.now(UTC):
                raise UnauthorizedException(
                    message="Session expired", details={"error": "expired_session"}
                )

            # 4. Return User Data (normalized)
            return {
                "id": row["id"],
                "email": row["email"],
                "name": row["name"],
                "image": row.get("image"),
                "email_verified": row.get("emailVerified", False),
                "role": "user",
            }
        except UnauthorizedException:
            raise
        except Exception as e:
            app_logger.error(f"Session verification failed: {e}")
            raise UnauthorizedException(
                message="Session verification failed", details={"error": str(e)}
            ) from e
