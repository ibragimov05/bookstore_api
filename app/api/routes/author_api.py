from fastapi import APIRouter, Depends, HTTPException, status

from app.api.routes.auth_api import oauth2_bearer
from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models import Author
from app.schemes.author_scheme import AuthorCreate, AuthorUpdate
from app.services.auth_service import verify_token

router = APIRouter(prefix='/author', tags=['author'])


@router.get('/')
def read_authors(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	all_authors = db.query(Author).all()

	return {'success': True, 'response': all_authors}


@router.get('/{author_id}')
def read_single_author(db: DB_DEPENDENCY, author_id: int, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	single_author = db.query(Author).filter(Author.id == author_id).first()

	if single_author is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

	return {'success': True, 'response': single_author}


@router.post('/create')
def create_new_author(db: DB_DEPENDENCY, author_create: AuthorCreate, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Only admins are allowed to create author')

	try:
		create_author_model = Author(name=author_create.name, biography=author_create.biography)

		db.add(create_author_model)
		db.commit()
		db.refresh(create_author_model)

		return {'success': True, 'message': 'author created successfully', 'response': create_author_model}
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/update/{author_id}')
def update_author(db: DB_DEPENDENCY, author_id: int, author_update: AuthorUpdate, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Only admins are allowed to update author')

	author = db.query(Author).filter(Author.id == author_id).first()

	if author is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Author with the given id not found')

	for key, value in author_update.model_dump().items():
		setattr(author, key, value)

	try:
		db.add(author)
		db.commit()
		db.refresh(author)

		return {'success': True, 'message': 'author updated successfully', 'response': author}
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete('/delete/{author_id}')
def delete_author(db: DB_DEPENDENCY, author_id: int, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Only admins are allowed to delete author')

	author = db.query(Author).filter(Author.id == author_id).first()

	if author is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Author with the given id not found')

	try:
		db.delete(author)
		db.commit()

		return {'success': True, 'message': 'author deleted successfully'}
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
