from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from dotenv import load_dotenv


load_dotenv()
SECRET = os.getenv("SECRET_KEY", "default_secret")
ALG = "HS256"
TTL_MIN = 60 * 24 * 7

def create_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=TTL_MIN)).timestamp()),
    }
    return jwt.encode(payload, SECRET, algorithm=ALG)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALG])
