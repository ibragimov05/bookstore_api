from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models.user import User
from app.schemes.user_scheme import CreateUserScheme

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

router = APIRouter(prefix='/auth', tags=['auth'])

SECRET_KEY = "6+/L7jDALfjgmikWi9gsWDwIlklsjF+7DcTZfG1val6nM2a40Yts9AN1fLbdrm5r"
ALGORITHM = "HS256"


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

	# Create the new user model
	create_user_model = User(
		username=create_user_request.username,
		email=create_user_request.email,
		is_active=True,
		is_admin=create_user_request.is_admin,
		hashed_password=bcrypt_context.hash(create_user_request.password)
	)

	db.add(create_user_model)

	try:
		db.commit()
		db.refresh(create_user_model)
		return create_user_model
	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
