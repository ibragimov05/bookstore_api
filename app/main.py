import uvicorn
from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.db.base import Base, engine

app = FastAPI()


@app.get('/', name='Health check')
def health_check():
	return {'status': 'HEALTHY'}


def main() -> None:
	Base.metadata.create_all(bind=engine)

	app.include_router(auth_router)

	uvicorn.run(app, port=8080, host="0.0.0.0")


if __name__ == '__main__':
	main()
