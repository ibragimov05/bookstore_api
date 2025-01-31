from fastapi import APIRouter, Depends, HTTPException, status

from app.api.routes.auth_api import oauth2_bearer
from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models import Category
from app.schemes.category_scheme import CategoryCreate
from app.services.auth_service import verify_token

router = APIRouter(prefix='/category', tags=['category'])


@router.post('/create')
def create_category(db: DB_DEPENDENCY, category_create: CategoryCreate, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Ony admins are allowed to create category",
		)

	try:
		create_category_model = Category(name=category_create.name)

		db.add(create_category_model)
		db.commit()
		db.refresh(create_category_model)

		return {'success': True, 'message': 'category created successfully', 'response': create_category_model}
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
