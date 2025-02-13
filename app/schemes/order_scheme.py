from typing import List

from pydantic import BaseModel, Field


class OrderItemScheme(BaseModel):
	book_id: int
	quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")

	class Config:
		orm_mode = True


class OrderScheme(BaseModel):
	order_items: List[OrderItemScheme] = Field(OrderItemScheme, description="List of order items")

	class Config:
		orm_mode = True


class OrderCreate(OrderScheme):
	pass
