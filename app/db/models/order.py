from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Order(Base):
	__tablename__ = 'orders'

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
	total_amount = Column(Float, nullable=False)
	status = Column(String, default='PENDING')
	created_at = Column(DateTime, default=datetime)
	updated_at = Column(DateTime, default=datetime)

	user = relationship("User", back_populates="orders")
	order_items = relationship("OrderItem", back_populates="Order", cascade="all, delete-orphan")

	def __repr__(self):
		return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status}, total_amount={self.total_amount})>"
