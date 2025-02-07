from typing import List, Optional

from pydantic import BaseModel


class FromUser(BaseModel):
	id: int
	is_bot: bool
	first_name: str
	last_name: Optional[str] = None
	username: Optional[str] = None
	language_code: Optional[str] = None


class Chat(BaseModel):
	id: int
	first_name: str
	last_name: Optional[str] = None
	username: Optional[str] = None
	type: str


class Message(BaseModel):
	message_id: int
	from_: FromUser
	chat: Chat
	date: int
	text: Optional[str] = None

	class Config:
		fields = {'from_': 'from'}


class Update(BaseModel):
	update_id: int
	message: Message


class TelegramResponse(BaseModel):
	ok: bool
	result: List[Update]
