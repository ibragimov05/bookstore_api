from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Category(Base):
	__tablename__ = "category"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False, unique=True)

	books = relationship("Book", back_populates="category")  # Fixed back_populates name
