from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQL_ALCHEMY_DATABASE_URL = 'sqlite:///./bookstore.db'
MYSQL_DATABASE_URL = "mysql+pymysql://root:community@127.0.0.1:3306/books_api_database"

engine = create_engine(MYSQL_DATABASE_URL)

SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
