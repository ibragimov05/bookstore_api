from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload

from app.api.routes.auth_api import oauth2_bearer
from app.core.utils.get_db import DB_DEPENDENCY
from app.db.models import Book, Order
from app.db.models.order import OrderItem
from app.schemes.order_scheme import OrderCreate
from app.services.auth_service import verify_token

router = APIRouter(prefix='/order', tags=['order'])


@router.get('/')
def get_all_orders(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	try:
		user_data = verify_token(token)

		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
		if not user_data.is_admin:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Only admins are allowed to get all orders",
			)

		all_orders = db.query(Order).options(joinedload(Order.order_items)).all()

		return {'success': True, 'response': all_orders}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/user')
def get_user_orders(db: DB_DEPENDENCY, token: str = Depends(oauth2_bearer)):
	try:
		user_data = verify_token(token)

		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		user_orders = db.query(Order) \
			.options(joinedload(Order.order_items)) \
			.filter(Order.user_id == user_data.user_id).all()

		return {'success': True, 'response': user_orders}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/create')
def create_order(db: DB_DEPENDENCY, order_create: OrderCreate, token: str = Depends(oauth2_bearer)):
	try:
		user_data = verify_token(token)

		if user_data is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

		for i in order_create.order_items:
			book = db.query(Book).filter(Book.id == i.book_id).first()

			if book is None:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail=f"Book with the given id {i.book_id} not found",
				)

		total_amount = sum(item.price_per_item * item.quantity for item in order_create.order_items)
		total_quantity = sum(item.quantity for item in order_create.order_items)

		for item in order_create.order_items:
			total_amount += (item.price_per_item * item.quantity)

		order = Order(
			user_id=user_data.user_id,
			total_amount=total_amount,
			total_quantity=total_quantity,
		)

		db.add(order)
		db.flush()

		order_items = []
		for item in order_create.order_items:
			order_item = OrderItem(
				order_id=order.id,
				book_id=item.book_id,
				quantity=item.quantity,
				price_per_item=item.price_per_item,
			)
			order_items.append(order_item)

		db.add_all(order_items)
		db.commit()
		db.refresh(order)

		order_db = db.query(Order).options(joinedload(Order.order_items)).filter(Order.id == order.id).first()

		return {
			"success": True, "message": "Order created successfully",
			"response": order_db,
		}
	except Exception as e:
		db.rollback()

		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
