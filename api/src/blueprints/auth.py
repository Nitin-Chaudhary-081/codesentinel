"""Authentication blueprint — register, login, token management."""

import re
import time
import uuid
from collections import defaultdict

from flask import Blueprint, request, jsonify

from src.database import get_db
from src.models import User
from src.auth import create_access_token, get_password_hash, verify_password
from src.config import settings

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8

MAX_LOGIN_ATTEMPTS = 20
LOGIN_WINDOW_SECONDS = 300
REDIS_PREFIX = "codesentinel:ratelimit:"

_login_attempts: dict[str, list[float]] = defaultdict(list)

_redis = None
if settings.redis_url:
    try:
        import redis as _redis_mod

        _redis = _redis_mod.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        _redis = None

__all__ = ["bp", "_reset_rate_limits"]


def _client_key() -> str:
    """Best-effort client identifier.

    Uses the real peer address. When the request originates from a configured
    trusted proxy, the original client is taken from the first X-Forwarded-For
    entry instead (avoids the per-proxy IP collapse behind a load balancer).
    """
    remote = request.remote_addr or "unknown"
    trusted = settings.trusted_proxy
    if trusted:
        trusted_ips = {ip.strip() for ip in trusted.split(",")}
        if remote in trusted_ips:
            xff = request.headers.get("X-Forwarded-For")
            if xff:
                return xff.split(",")[0].strip()
    return remote


def _reset_rate_limits():
    """Clear all rate limit tracking. For testing only."""
    _login_attempts.clear()
    if _redis is not None:
        try:
            keys = _redis.keys(REDIS_PREFIX + "*")
            if keys:
                _redis.delete(*keys)
        except Exception:
            pass


def _check_rate_limit(key: str) -> tuple[bool, int]:
    """Check if rate limit is exceeded. Returns (allowed, retry_after).

    Uses a shared Redis backend when configured (survives restarts and is
    consistent across workers); otherwise falls back to in-process memory.
    """
    now = time.time()
    if _redis is not None:
        rkey = REDIS_PREFIX + key
        member = f"{now}:{uuid.uuid4().hex}"
        pipe = _redis.pipeline()
        pipe.zremrangebyscore(rkey, 0, now - LOGIN_WINDOW_SECONDS)
        pipe.zadd(rkey, {member: now})
        pipe.zcard(rkey)
        pipe.expire(rkey, LOGIN_WINDOW_SECONDS)
        try:
            _, _, count, _ = pipe.execute()
        except Exception:
            count = 0
        if count > MAX_LOGIN_ATTEMPTS:
            try:
                _redis.zrem(rkey, member)
                oldest = _redis.zrange(rkey, 0, 0, withscores=True)
                retry_after = (
                    int(LOGIN_WINDOW_SECONDS - (now - oldest[0][1]))
                    if oldest
                    else LOGIN_WINDOW_SECONDS
                )
            except Exception:
                retry_after = LOGIN_WINDOW_SECONDS
            return False, max(retry_after, 1)
        return True, 0

    attempts = _login_attempts[key]
    _login_attempts[key] = [t for t in attempts if now - t < LOGIN_WINDOW_SECONDS]
    if len(_login_attempts[key]) >= MAX_LOGIN_ATTEMPTS:
        oldest = min(_login_attempts[key])
        retry_after = int(LOGIN_WINDOW_SECONDS - (now - oldest))
        return False, max(retry_after, 1)
    _login_attempts[key].append(now)
    return True, 0


def _validate_auth_fields(data: dict) -> tuple[str | None, str | None]:
    """Validate email and password presence/format. Returns (error_type, message) or (None, None)."""
    if not data:
        return "validation_error", "Request body is required"
    email = data.get("email")
    password = data.get("password")
    if not email or not isinstance(email, str):
        return "validation_error", "Email is required"
    if not password or not isinstance(password, str):
        return "validation_error", "Password is required"
    if not EMAIL_RE.match(email):
        return "validation_error", "Invalid email format"
    if len(password) < MIN_PASSWORD_LENGTH:
        return "validation_error", f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    return None, None


@bp.route("/register", methods=["POST"])
def register():
    allowed, retry_after = _check_rate_limit(f"register:{_client_key()}")
    if not allowed:
        return jsonify({
            "status": "error",
            "error_type": "rate_limited",
            "message": "Too many registration attempts, please try again later",
        }), 429

    data = request.get_json()
    error_type, message = _validate_auth_fields(data)
    if error_type:
        return jsonify({"status": "error", "error_type": error_type, "message": message}), 400

    db = get_db()
    try:
        existing = db.query(User).filter(User.email == data["email"]).first()
        if existing:
            return jsonify({
                "status": "error",
                "error_type": "conflict",
                "message": "Email already registered",
            }), 409

        user = User(email=data["email"], password_hash=get_password_hash(data["password"]))
        db.add(user)
        db.commit()
        db.refresh(user)
        return jsonify({
            "status": "ok",
            "data": {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
            },
        }), 201
    finally:
        db.close()


@bp.route("/login", methods=["POST"])
def login():
    allowed, retry_after = _check_rate_limit(f"login:{_client_key()}")
    if not allowed:
        resp = jsonify({
            "status": "error",
            "error_type": "rate_limited",
            "message": "Too many login attempts, please try again later",
        })
        resp.status_code = 429
        resp.headers["Retry-After"] = str(retry_after)
        return resp

    data = request.get_json()
    error_type, message = _validate_auth_fields(data)
    if error_type:
        return jsonify({"status": "error", "error_type": error_type, "message": message}), 400

    db = get_db()
    try:
        user = db.query(User).filter(User.email == data["email"]).first()
        if not user or not verify_password(data["password"], user.password_hash):
            return jsonify({
                "status": "error",
                "error_type": "invalid_credentials",
                "message": "Invalid email or password",
            }), 401

        token = create_access_token({"sub": str(user.id)})
        return jsonify({
            "status": "ok",
            "data": {
                "access_token": token,
                "token_type": "bearer",
            },
        })
    finally:
        db.close()
