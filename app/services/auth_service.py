import logging
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from app.db.models import User

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

SECRET_KEY = "6+/L7jDALfjgmikWi9gsWDwIlklsjF+7DcTZfG1val6nM2a40Yts9AN1fLbdrm5r"
ALGORITHM = "HS256"


def create_token(user: User, expired_delta: timedelta) -> str:
	to_encode = {
		"sub": user.username,
		"id": user.id,
		"email": user.email,
		"is_admin": user.is_admin,
	}

	expire = datetime.now() + expired_delta
	to_encode.update({"exp": expire})
	token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

	logging.log(msg=f"TOKEN: {token}", level=1)
	return token


def hash_password(plain_password: str) -> str:
	return bcrypt_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return bcrypt_context.verify(plain_password, hashed_password)


def decode_token(token: str) -> dict[str, any]:
	return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


class UserModel(BaseModel):
	user_id: int
	username: str
	email: str
	is_admin: bool


def verify_token(token: str) -> UserModel:
	"""Helper function to verify and decode the JWT token."""
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

		username: str = payload.get("sub")
		email: str = payload.get("email")
		is_admin: bool = payload.get("is_admin", False)
		user_id: bool = payload.get("id")

		if not username or not email or not user_id:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail='INVALID  TOKEN'
			)

		return UserModel(
			username=username,
			email=email,
			is_admin=is_admin,
			user_id=user_id,
		)
	except ExpiredSignatureError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token has expired",
			headers={"WWW-Authenticate": "Bearer"},
		)
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid or expired token",
			headers={"WWW-Authenticate": "Bearer"},
		)
