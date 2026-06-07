from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time


def hash_password(password: str, salt: str | None = None, iterations: int = 390_000) -> str:
    salt_bytes = bytes.fromhex(salt) if salt else secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, iterations)
    return f"pbkdf2_sha256${iterations}${salt_bytes.hex()}${derived.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    algorithm, iterations, salt_hex, expected_hex = password_hash.split("$", 3)
    if algorithm != "pbkdf2_sha256":
        return False
    actual = hash_password(password, salt=salt_hex, iterations=int(iterations))
    return hmac.compare_digest(actual, password_hash)


def create_access_token(subject: str, secret: str, expires_minutes: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": subject, "iat": now, "exp": now + expires_minutes * 60}
    header_part = _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_part = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret.encode("utf-8"), f"{header_part}.{payload_part}".encode("utf-8"), hashlib.sha256).digest()
    return f"{header_part}.{payload_part}.{_b64url(signature)}"


def decode_access_token(token: str, secret: str) -> str:
    header_part, payload_part, signature_part = token.split(".")
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        f"{header_part}.{payload_part}".encode("utf-8"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(_unb64url(signature_part), expected_signature):
        raise ValueError("Invalid token signature")
    payload = json.loads(_unb64url(payload_part))
    if int(payload["exp"]) < int(time.time()):
        raise ValueError("Token expired")
    return str(payload["sub"])


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64url(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)
