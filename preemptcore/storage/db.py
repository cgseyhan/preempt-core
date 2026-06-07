"""Database setup and SQLModel engine initialization."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

# Import models so SQLModel knows about them before create_all
from preemptcore.storage.models_db import DBFinding, DBScanResult, DBScanTarget  # noqa: F401

sqlite_file_name = "preemptcore.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables() -> None:
    """Create the SQLite database and all tables."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    with Session(engine) as session:
        yield session
