from pydantic import BaseModel, Field


class ReviewScheme(BaseModel):
	content: str
	rating: int = Field(gt=0, lt=6)
	book_id: int


class ReviewCreate(ReviewScheme):
	pass
