from pydantic import BaseModel


class ReviewScheme(BaseModel):
	content: str
	rating: int
	book_id: int


class ReviewCreate(ReviewScheme):
	pass
