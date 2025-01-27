from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.db.base import Base, engine

app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get('/', name='Health check')
def health_check():
	return {'status': 'HEALTHY'}


app.include_router(auth_router)
