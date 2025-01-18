import bcrypt


def bcrypt_pwd(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def verify_bcrypt_pwd(pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), hashed_pwd.encode())
