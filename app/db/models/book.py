from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Book(Base):
	__tablename__ = 'books'

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String, nullable=False)
	description = Column(Text, nullable=True)
	price = Column(Float, nullable=False)
	stock = Column(Integer, default=0)
	author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
	category_id = Column(Integer, ForeignKey('category.id'), nullable=False)  # Fixed ForeignKey type
	published_year = Column(Integer, nullable=True)

	# Relationships
	author = relationship("Author", back_populates="books")
	reviews = relationship("Review", back_populates="book")
	order_items = relationship("OrderItem", back_populates="book")
	category = relationship("Category", back_populates="books")  # Fixed back_populates

	def __repr__(self):
		return f"<Book(title={self.title}, price={self.price})>"
