import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.auth_api import router as auth_router
from app.api.routes.author_api import router as author_router
from app.api.routes.book_api import router as book_router
from app.api.routes.category_api import router as category_router
from app.api.routes.order_api import router as order_router
from app.api.routes.review_api import router as review_router
from app.api.routes.user_api import router as user_router
from app.db.base import Base, engine
from app.services.bot_instance import bot_service


@asynccontextmanager
async def lifespan(application: FastAPI):
	# Create database tables
	Base.metadata.create_all(bind=engine)

	# Start the Telegram bot
	try:
		bot_task = asyncio.create_task(bot_service.run())
		yield
	finally:
		# Properly shutdown the bot when the application stops
		if hasattr(bot_service.application, 'stop'):
			await bot_service.application.stop()
		if hasattr(bot_service.application, 'shutdown'):
			await bot_service.application.shutdown()

		# Cancel the bot task
		if 'bot_task' in locals():
			bot_task.cancel()
			try:
				await bot_task
			except asyncio.CancelledError:
				pass


app = FastAPI(lifespan=lifespan)


@app.get('/', name='Health check')
def health_check():
	return {'status': 'HEALTHY'}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(book_router)
app.include_router(order_router)
app.include_router(author_router)
app.include_router(category_router)
app.include_router(review_router)
