from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError

from app.core.utils.get_db import DB_DEPENDENCY
from app.core.utils.helpers import is_valid_email
from app.schemes.user_scheme import CreateUserScheme
from app.services.auth_service import *

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
	db: DB_DEPENDENCY,
	form_data: OAuth2PasswordRequestForm = Depends(),
):
	user = db.query(User).filter(User.username == form_data.username).first()

	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid username or password"
		)

	if not verify_password(form_data.password, user.hashed_password):
		return HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid username or password"
		)

	if not user.is_active:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Account is inactive. Please contact support.",
		)

	a_token = create_token(
		user=user,
		expired_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
		is_refresh_token=False,
	)
	r_token = create_token(
		user=user,
		expired_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
		is_refresh_token=True,
	)

	return {
		"token": {
			"access_token": a_token,
			"refresh_token": r_token,
			"token_type": "BEARER",
		},
		"user": {
			"id": user.id,
			"username": user.username,
			"email": user.email,
			"is_admin": user.is_admin,
			"created_at": user.created_at,
		}
	}


@router.post("/sign_in", status_code=status.HTTP_201_CREATED)
async def sign_in(db: DB_DEPENDENCY, create_user_request: CreateUserScheme):
	# Check if the username or email already exists
	existing_user = db.query(User).filter(
		(User.username == create_user_request.username) |
		(User.email == create_user_request.email)
	).first()

	if existing_user:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Username or email already registered"
		)
	elif not is_valid_email(create_user_request.email):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail='Invalid email address. Please check the format.'
		)

	create_user_model = User(
		username=create_user_request.username,
		email=create_user_request.email,
		is_active=True,
		is_admin=create_user_request.is_admin,
		hashed_password=hash_password(create_user_request.password)
	)

	db.add(create_user_model)

	try:
		db.commit()
		db.refresh(create_user_model)

		return create_user_model
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(db: DB_DEPENDENCY, token: str):
	try:
		payload = decode_token(token)
		print(payload)

		is_refresh_token = payload.get("is_refresh_token")

		if not is_refresh_token or is_refresh_token is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		username = payload.get("sub")
		if username is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		user = db.query(User).filter(User.username == username).first()

		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

		new_access_token = create_token(
			user=user,
			expired_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
			is_refresh_token=False,
		)

		new_refresh_token = create_token(
			user=user,
			expired_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS),
			is_refresh_token=True,
		)

		return {
			"token_type": "bearer",
			"access_token": new_access_token,
			"refresh_token": new_refresh_token,
		}


	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
