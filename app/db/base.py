from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQL_ALCHEMY_DATABASE_URL = 'sqlite:///./bookstore.db'
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:community@127.0.0.1:3306/TodoApplicationDatabase"

engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
