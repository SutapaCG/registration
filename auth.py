
# auth.py
import os
import bcrypt
import redis
from datetime import datetime
from typing import Optional, Dict

def get_redis_client() -> redis.Redis:
    """
    Create a Redis client from environment or Streamlit secrets.
    Supports Redis with/without TLS.
    """
    # Fallbacks for local dev (no TLS) or managed Redis (TLS).
    # host = os.environ.get("REDIS_HOST") or os.environ.get("REDIS_URL_HOST")
    # port = int(os.environ.get("REDIS_PORT", "6379"))
    # password = os.environ.get("REDIS_PASSWORD")
    # ssl = os.environ.get("REDIS_SSL", "false").lower() == "true"
    host = 'redis-17415.c74.us-east-1-4.ec2.cloud.redislabs.com'
    port = 17415
    password = '93xVoKj0Px5MD0gvQv8f0gSYd5ZyuJnw'
    # ssl = "true"

    # Streamlit Cloud: pull from st.secrets if present
    try:
        import streamlit as st
        if "redis" in st.secrets:
            host = st.secrets["redis"].get("host", host)
            port = int(st.secrets["redis"].get("port", port))
            password = st.secrets["redis"].get("password", password)
            # ssl = bool(st.secrets["redis"].get("ssl", ssl))
    except Exception:
        pass

    pool = redis.ConnectionPool(
        host=host or "localhost",
        port=port,
        password=password,
        # ssl=ssl,
        # ssl_cert_reqs=None,
        # ssl_cert_reqs=None if ssl else None,
        decode_responses=True,  # work with str
    )
    return redis.Redis(connection_pool=pool)


def email_exists(r: redis.Redis, email: str) -> bool:
    return r.sismember("users:emails", email)


def register_user(r: redis.Redis, name: str, email: str, password: str) -> bool:
    """
    Creates a new user if email not taken.
    Returns True on success, False if email exists.
    """
    email = email.strip().lower()
    if email_exists(r, email):
        return False

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    pipe = r.pipeline()
    pipe.hset(f"user:{email}", mapping={
        "email": email,
        "name": name.strip(),
        "password_hash": password_hash,
        "created_at": datetime.utcnow().isoformat(),
    })
    pipe.sadd("users:emails", email)
    pipe.execute()
    return True


def verify_login(r: redis.Redis, email: str, password: str) -> Optional[Dict]:
    """
    Returns user dict if password is correct, else None.
    """
    email = email.strip().lower()
    if not email_exists(r, email):
        return None
    user = r.hgetall(f"user:{email}")
    if not user or "password_hash" not in user:
        return None
    ok = bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8"))
    return user if ok else None
