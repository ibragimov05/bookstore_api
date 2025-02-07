from sqlalchemy import Column, Integer, String

from app.db.base import Base


class TelegramUser(Base):
	__tablename__ = "telegram_users"

	id = Column(Integer, primary_key=True, index=True)
	chat_id = Column(Integer, unique=True, nullable=False)
	username = Column(String, nullable=True)

	def __repr__(self):
		return f"TelegramUser(id={self.id}, chat_id={self.chat_id}, username={self.username})"
