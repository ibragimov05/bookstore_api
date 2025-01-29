from http.client import HTTPException

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models import Book
from app.schemes.book_scheme import BookCreate
from app.services.auth_service import verify_token

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(prefix='/books', tags=['books'])


@router.get("/")
def read_books(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	print(f"Access granted for user: {user_data.username}")

	all_books = db.query(Book).all()
	# Return the books
	return {"success": True, "message": f"Books retrieved for user: {user_data.username}", "response": all_books}


@router.post("/create")
def create_book(db: DB_DEPENDENCY, book_create: BookCreate, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
	if not user_data.is_admin:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ony admins are allowed to create book")

	create_book_model = Book(
		title=book_create.title,
		description=book_create.description,
		price=book_create.price,
		stock=book_create.stock,
		author_id=book_create.author_id,
		category_id=book_create.author_id,
		published_year=book_create.published_year
	)

	try:
		db.add(create_book_model)
		db.commit()
		db.refresh(create_book_model)
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# id = Column(Integer, primary_key=True, index=True)
# 	title = Column(String, nullable=False)
# 	description = Column(Text, nullable=True)
# 	price = Column(Float, nullable=False)
# 	stock = Column(Integer, default=0)
# 	author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
# 	category_id = Column(String, nullable=False)
# 	published_year = Column(Integer, nullable=True)
#
# 	# Relationships
# 	author = relationship("Author", back_populates="books")
# 	reviews = relationship("Review", back_populates="book")
# 	order_items = relationship("OrderItem", back_populates="book")
