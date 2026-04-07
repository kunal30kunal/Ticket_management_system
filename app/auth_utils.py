import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, UTC
from typing import Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

# Load env
load_dotenv()

# Config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_LIFETIME_MIN = int(os.getenv("TOKEN_LIFETIME_MIN", 60))

password_ctx = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


#  Hash password
def generate_hash(raw_password: str) -> str:
    return password_ctx.hash(raw_password)


# Verify password
def check_hash(raw_password: str, stored_hash: str) -> bool:
    return password_ctx.verify(raw_password, stored_hash)


# jwt token
def build_token(payload: Dict[str, Any]) -> str:
    token_data = payload.copy()

    expiry_time = datetime.now(UTC) + timedelta(minutes=TOKEN_LIFETIME_MIN)
    token_data["exp"] = expiry_time

    encoded_jwt = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None