'''
🧠 Correct one-line summaries to keep in your head

Engine
📌 “The engine manages the connection pool and knows how to connect to DB.”

SessionLocal
📌 “A session factory that can give me a session when needed.”

Session from get_db
📌 “A session is one unit of work for one API request.”

get_db dependency
📌 “FastAPI will give me a fresh session per request and close it after.”
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings

DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(DATABASE_URL, 
                    pool_size=10, 
                    max_overflow=20, 
                    pool_pre_ping=True
            )

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()   

         