from fastapi import FastAPI

from app.api.routes.auth_api import router as auth_router
from app.api.routes.author_api import router as author_router
from app.api.routes.book_api import router as book_router
from app.api.routes.category_api import router as category_router
from app.api.routes.review_api import router as review_router
from app.api.routes.user_api import router as user_router
from app.db.base import Base, engine

app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get('/', name='Health check')
def health_check():
	return {'status': 'HEALTHY'}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(book_router)
app.include_router(author_router)
app.include_router(category_router)
app.include_router(review_router)
