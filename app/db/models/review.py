from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Review(Base):
	__tablename__ = "reviews"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
	rating = Column(Float, nullable=False)  # Rating between 1 and 5
	content = Column(Text, nullable=True)  # Optional review content
	created_at = Column(DateTime, default=datetime.utcnow)

	# Relationships
	user = relationship("User", back_populates="reviews")
	book = relationship("Book", back_populates="reviews")

	def __repr__(self):
		return f"<Review(user_id={self.user_id}, book_id={self.book_id}, rating={self.rating})>"
