import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger("library.database")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("database_url is not set in environment variables")


engine = create_engine(
    database_url,
    pool_pre_ping=True
)

session_local = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()