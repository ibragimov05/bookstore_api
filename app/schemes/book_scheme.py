from pydantic import BaseModel


class BookBase(BaseModel):
	title: str
	description: str | None = None
	price: float
	stock: int
	published_year: int | None = None
	category_id: int


class BookCreate(BookBase):
	author_id: int


class BookUpdate(BookBase):
	author_id: int


class BookResponse(BookBase):
	id: int
	author: str
	category: str

	class Config:
		orm_mode = True
