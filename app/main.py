from fastapi import FastAPI

from app.api.routes.auth_api import router as auth_router
from app.api.routes.book_api import router as book_router
from app.db.base import Base, engine

app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get('/', name='Health check')
def health_check():
	return {'status': 'HEALTHY'}


app.include_router(auth_router)
app.include_router(book_router)
