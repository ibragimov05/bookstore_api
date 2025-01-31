from pydantic import BaseModel


class AuthorBase(BaseModel):
	name: str
	biography: str | None = None


class AuthorCreate(AuthorBase):
	pass
