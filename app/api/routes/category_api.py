from sqlite3 import IntegrityError

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.routes.auth_api import oauth2_bearer
from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models import Category
from app.schemes.category_scheme import CategoryCreate, CategoryUpdate
from app.services.auth_service import verify_token

router = APIRouter(prefix='/category', tags=['category'])


@router.get('/')
def read_categories(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	all_categories = db.query(Category).all()

	return {'success': True, 'response': all_categories}


from sqlalchemy.exc import IntegrityError
import pymysql


@router.post('/create')
def create_category(db: DB_DEPENDENCY, category_create: CategoryCreate, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Only admins are allowed to create categories",
		)

	try:
		create_category_model = Category(name=category_create.name)

		db.add(create_category_model)
		db.commit()
		db.refresh(create_category_model)

		return {'success': True, 'message': 'category created successfully', 'response': create_category_model}

	except IntegrityError as e:
		db.rollback()

		# noinspection PyUnresolvedReferences
		if isinstance(e.orig, pymysql.MySQLError) and e.orig.args[0] == 1062:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
		else:
			raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/update/{category_id}')
def update_category(
	db: DB_DEPENDENCY,
	category_id: int,
	category_update: CategoryUpdate,
	token: str = Depends(oauth2_bearer),
):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Ony admins are allowed to update category",
		)

	category = db.query(Category).filter(Category.id == category_id).first()

	if category is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

	for key, value in category_update.model_dump().items():
		setattr(category, key, value)

	try:
		db.add(category)
		db.commit()
		db.refresh(category)

		return {'success': True, 'message': 'category updated successfully', 'response': category}
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete('/delete/{category_id}')
def delete_category(db: DB_DEPENDENCY, category_id: int, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		                    detail="Ony admins are allowed to delete category")

	category = db.query(Category).filter(Category.id == category_id).first()

	if category is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

	try:
		db.delete(category)
		db.commit()

		return {'success': True, 'message': 'category deleted successfully'}
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
