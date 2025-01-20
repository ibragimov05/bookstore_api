from pydantic import BaseModel


class BookBase(BaseModel):
	title: str
	description: str | None = None
	price: float
	stock: int
	isbn: str | None = None
	published_year: int | None = None


class BookCreate(BookBase):
	author_id: int
	category_id: int


class BookResponse(BookBase):
	id: int
	author: str
	category: str

	class Config:
		orm_mode = True
