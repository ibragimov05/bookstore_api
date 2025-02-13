from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.logger import logger
from sqlalchemy.orm import joinedload

from app.api.routes.auth_api import oauth2_bearer
from app.core.utils.get_db import DB_DEPENDENCY
from app.core.utils.order_status import OrderStatus
from app.core.utils.telegram_bot_response import send_order_notification_to_telegram
from app.db.models import Book, Order
from app.db.models.order import OrderItem
from app.schemes.order_scheme import OrderCreate
from app.services.auth_service import verify_token

router = APIRouter(prefix='/order', tags=['order'])


@router.get('/')
def get_all_orders(db: DB_DEPENDENCY, filter_by: str = None, token: str = Depends(oauth2_bearer)):
	logger.log(msg=f"Filter by: {filter_by}", level=1)
	user_data = verify_token(token)

	try:
		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
		if not user_data.is_admin:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Only admins are allowed to get all orders",
			)
		if filter_by is not None:
			filter_by = filter_by.upper()

			if filter_by not in [s.value for s in OrderStatus]:
				raise HTTPException(
					status_code=status.HTTP_400_BAD_REQUEST,
					detail='Give valid status [PAID, DELIVERED, PENDING]',
				)
			else:
				all_orders = db.query(Order). \
					options(joinedload(Order.order_items)). \
					filter(Order.status == filter_by). \
					all()
		else:
			all_orders = db.query(Order).options(joinedload(Order.order_items)).all()

		return {'success': True, 'response': all_orders}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/user')
def get_user_orders(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	try:
		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		user_orders = db.query(Order) \
			.options(joinedload(Order.order_items)) \
			.filter(Order.user_id == user_data.user_id).all()

		return {'success': True, 'response': user_orders}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/create')
async def create_order(db: DB_DEPENDENCY, order_create: OrderCreate, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	try:
		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		books_in_db = []

		for i in order_create.order_items:
			book = db.query(Book).filter(Book.id == i.book_id).first()
			if book is None:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail=f"Book with the given ID {i.book_id} not found",
				)
			books_in_db.append(book)

		total_amount = sum(item.quantity * book.price for item, book in zip(order_create.order_items, books_in_db))
		total_quantity = sum(item.quantity for item in order_create.order_items)

		order = Order(
			user_id=user_data.user_id,
			total_amount=total_amount,
			total_quantity=total_quantity,
		)

		db.add(order)
		db.flush()

		order_items = [
			OrderItem(
				order_id=order.id,
				book_id=item.book_id,
				quantity=item.quantity,
				price_per_item=book.price,
			)
			for item, book in zip(order_create.order_items, books_in_db)
		]

		db.add_all(order_items)
		db.commit()
		db.refresh(order)

		telegram_bot_response = await send_order_notification_to_telegram(order)

		return {
			"success": True,
			"message": "Order created successfully",
			"response": order,
			"telegram_bot_response": telegram_bot_response
		}

	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/update/{order_id}')
def order_to_paid_status(db: DB_DEPENDENCY, order_id: int, new_status: str, token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	try:
		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		if not user_data.is_admin:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Only admins are allowed to update order status",
			)
		new_status = new_status.upper()
		if new_status != OrderStatus.PAID.value and new_status != OrderStatus.DELIVERED.value and new_status != OrderStatus.PENDING.value:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail='Give valid status [PAID, DELIVERED, PENDING]',
			)

		order = db.query(Order).filter(Order.id == order_id).first()

		if order is None:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"Order with the given id {order_id} not found",
			)

		if order.status == new_status:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Order with id {order_id} is already in {order.status} status",
			)

		order.status = new_status
		order.updated_at = datetime.now()

		db.commit()
		db.refresh(order)

		return {"success": True, "message": "Order status updated to PAID", "response": order}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
