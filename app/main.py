from fastapi import Depends, FastAPI, HTTPException, status

from app.api.routes.auth_api import oauth2_bearer, router as auth_router
from app.api.routes.author_api import router as author_router
from app.api.routes.book_api import router as book_router
from app.api.routes.category_api import router as category_router
from app.db.base import Base, engine
from app.services.auth_service import verify_token

app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get('/', name='Health check')
def health_check(token: str = Depends(oauth2_bearer)):
	user_data = verify_token(token)

	if user_data is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	return {'status': 'HEALTHY'}


app.include_router(auth_router)
app.include_router(book_router)
app.include_router(author_router)
app.include_router(category_router)
