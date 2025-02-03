from fastapi import APIRouter, Depends, HTTPException, status

from app.api.routes.auth_api import oauth2_bearer
from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models import Order
from app.services.auth_service import verify_token

router = APIRouter(prefix='/order', tags=['order'])


@router.get('/')
def get_all_orders(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	try:
		user_data = verify_token(token)

		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
		if not user_data.is_admin:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Only admins are allowed to get all orders",
			)

		all_orders = db.query(Order).all()

		return {'success': True, 'response': all_orders}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/user')
def get_user_orders(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	try:
		user_data = verify_token(token)

		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		user_orders = db.query(Order).filter(Order.user_id == user_data.user_id).all()

		return {'success': True, 'response': user_orders}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
