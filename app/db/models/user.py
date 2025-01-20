from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True, nullable=False)
	email = Column(String, unique=True, nullable=False)
	hashed_password = Column(String, nullable=False)
	is_active = Column(Boolean, default=True)
	is_admin = Column(Boolean, default=True)
	created_at = Column(DateTime, default=datetime.now())

	# Relationships
	orders = relationship("Order", back_populates="user")

	def __repr__(self):
		return f"<User(username={self.username}, is_admin={self.is_admin})>"
