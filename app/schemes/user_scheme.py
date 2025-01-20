from pydantic import BaseModel, EmailStr, Field


class CreateUserScheme(BaseModel):
	username: str = Field(min_length=5, max_length=99, description='User name')
	email: str = Field(EmailStr, description='User email')
	password: str = Field(..., description='Password')
	is_admin: bool = Field(..., description='Boolean to check whether user is admin or not')
