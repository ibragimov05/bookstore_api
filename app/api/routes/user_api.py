from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload

from app.api.routes.auth_api import oauth2_bearer
from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models import User
from app.services.auth_service import verify_token

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
def get_user(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	user = db.query(User) \
		.options(joinedload(User.reviews)) \
		.options(joinedload(User.orders)) \
		.filter(User.id == user_data.user_id).first()

	return {'success': True, 'response': user}
