from fastapi import APIRouter, Depends, HTTPException, status

from app.api.routes.auth_api import oauth2_bearer
from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models import Book, Review
from app.schemes.review_scheme import ReviewCreate
from app.services.auth_service import verify_token

router = APIRouter(prefix='/review', tags=['review'])


@router.post('/create')
def post_review(db: DB_DEPENDENCY, review_create: ReviewCreate, token: str = Depends(oauth2_bearer)):
	try:
		user_data = verify_token(token)

		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		book = db.query(Book).filter(Book.id == review_create.book_id).first()

		if book is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

		if review_create.rating < 1 or review_create.rating > 5:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 1 and 5")

		review = Review(
			user_id=user_data.user_id,
			book_id=review_create.book_id,
			rating=review_create.rating,
			content=review_create.content,
		)

		db.add(review)
		db.commit()

		return {"success": True, "message": "Review created successfully"}

	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete('/delete/{review_id}')
def delete_review(db: DB_DEPENDENCY, review_id: int, token: str = Depends(oauth2_bearer)):
	try:
		user_data = verify_token(token)

		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		review = db.query(Review).filter(Review.id == review_id).first()

		if review is None:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

		if review.user_id != user_data.user_id and not user_data.is_admin:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="You are not allowed to delete this review",
			)

		db.delete(review)
		db.commit()

		return {"success": True, "message": "Review deleted successfully"}
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
