import jwt
import datetime
from app.config import SECRET_KEY


def generate_jwt_token(payload={}, expiration_days=1):
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(
        days=expiration_days
    )
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def validate_jwt_token(token):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True
    except Exception:
        return False
