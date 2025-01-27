from http.client import HTTPException

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.services.auth_service import verify_token

SECRET_KEY = "6+/L7jDALfjgmikWi9gsWDwIlklsjF+7DcTZfG1val6nM2a40Yts9AN1fLbdrm5r"
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")  # Token endpoint for obtaining tokens

router = APIRouter(prefix='/books', tags=['books'])


@router.get("/")
def get_books(token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	print(f"Access granted for user: {user_data.username}")

	# Return the books
	return {"success": True, "message": f"Books retrieved for user: {user_data.username}"}
