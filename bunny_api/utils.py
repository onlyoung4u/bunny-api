from functools import lru_cache

import bcrypt
from fastapi import Request


def bcrypt_pwd(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


@lru_cache(maxsize=1000)
def verify_bcrypt_pwd(pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), hashed_pwd.encode())


def get_real_ip(request: Request) -> str:
    real_ip = request.headers.get('X-Real-IP')

    if real_ip:
        return real_ip

    x_forwarded_for = request.headers.get('X-Forwarded-For')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()

    return request.client.host
