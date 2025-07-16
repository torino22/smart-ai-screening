from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Add event listener to set WAL mode
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

