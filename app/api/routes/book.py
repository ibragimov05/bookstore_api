from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

SECRET_KEY = "6+/L7jDALfjgmikWi9gsWDwIlklsjF+7DcTZfG1val6nM2a40Yts9AN1fLbdrm5r"
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")  # Token endpoint for obtaining tokens

router = APIRouter(prefix='/books', tags=['books'])


def verify_token(token: str) -> dict:
	"""Helper function to verify and decode the JWT token."""
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")

		if not username:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Token payload invalid",
			)
		return payload  # Return decoded payload for further use
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid or expired token",
			headers={"WWW-Authenticate": "Bearer"},
		)


@router.get("/")
def get_books(token: str = Depends(oauth2_bearer)):
	"""
	Secure endpoint to fetch books.
	User must provide a valid access token to access this endpoint.
	"""
	user_data = verify_token(token)  # Decode and verify the token

	# Example: Log or use `user_data` (decoded token payload)
	print(f"Access granted for user: {user_data['sub']}")

	# Return the books
	return {"success": True, "message": f"Books retrieved for user: {user_data['sub']}"}
