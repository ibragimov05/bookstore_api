import uvicorn
from fastapi import FastAPI

from app.db.base import Base, engine

app = FastAPI()


@app.get('/', name='Health check')
def health_check():
	return {'status': 'HEALTHY'}


if __name__ == '__main__':
	Base.metadata.create_all(bind=engine)

	uvicorn.run(app, port=8080, host="0.0.0.0")
