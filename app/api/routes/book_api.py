from http.client import HTTPException

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload

from app.api.routes.auth_api import oauth2_bearer
from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models import Author, Book, Category
from app.schemes.book_scheme import BookCreate, BookUpdate
from app.services.auth_service import verify_token

router = APIRouter(prefix='/books', tags=['books'])


@router.get("/")
def read_books(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	all_books = db.query(Book).all()

	return {"success": True, "response": all_books}


@router.get('/{book_id}')
def read_single_book(db: DB_DEPENDENCY, book_id: int, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	single_book = (db.query(Book).options(
		joinedload(Book.author),
		joinedload(Book.category),
		joinedload(Book.reviews),
	).filter(Book.id == book_id).first())

	if single_book is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

	return {"success": True, "response": single_book}


@router.post("/create")
def create_book(db: DB_DEPENDENCY, book_create: BookCreate, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ony admins are allowed to create book")
	if db.query(Author).filter(Author.id == book_create.author_id).first() is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author with the given id not found")
	if db.query(Category).filter(Category.id == book_create.category_id).first() is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category with the given id not found")

	create_book_model = Book(
		title=book_create.title,
		description=book_create.description,
		price=book_create.price,
		stock=book_create.stock,
		author_id=book_create.author_id,
		category_id=book_create.category_id,
		published_year=book_create.published_year
	)

	try:
		db.add(create_book_model)
		db.commit()
		db.refresh(create_book_model)

		return {"success": True, "message": "book created successfully", 'response': create_book_model}

	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/update/{book_id}")
def update_book(db: DB_DEPENDENCY, book_id: int, book_update: BookUpdate, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ony admins are allowed to create book")

	author = db.query(Author).filter(Author.id == book_update.author_id).first()
	book = db.query(Book).filter(book_id == Book.id).first()

	if book is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book with the given id not found')
	if author is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author with the given id not found")

	for key, value in book_update.model_dump().items():
		setattr(book, key, value)

	db.add(book)
	db.commit()
