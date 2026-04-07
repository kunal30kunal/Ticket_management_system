from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
Database_URL = "sqlite:///./tickets.db"

engine= create_engine(Database_URL, connect_args={"check_same_thread": False})
sessionlocal = sessionmaker(bind=engine,autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()