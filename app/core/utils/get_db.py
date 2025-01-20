from app.db.base import SESSION_LOCAL


def get_db():
	db = SESSION_LOCAL()

	try:
		yield db
	finally:
		db.close()
