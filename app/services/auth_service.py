from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.db.models import User

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

SECRET_KEY = "6+/L7jDALfjgmikWi9gsWDwIlklsjF+7DcTZfG1val6nM2a40Yts9AN1fLbdrm5r"
ALGORITHM = "HS256"


def create_token(user: User, expired_delta: timedelta, is_refresh_token: bool) -> str:
	to_encode = {
		"sub": user.username,
		"id": user.id,
		"email": user.email,
		"is_admin": user.is_admin,
		"is_refresh_token": is_refresh_token,
	}

	expire = datetime.now() + expired_delta

	to_encode.update({"exp": expire})

	token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

	print(f"TOKEN: {token}")

	return token


def hash_password(plain_password: str) -> str:
	return bcrypt_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return bcrypt_context.verify(plain_password, hashed_password)


def decode_token(token: str) -> dict[str, any]:
	return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
