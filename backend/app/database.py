"""
Database configuration using SQLAlchemy.

The backend uses a lightweight SQLite database to persist request logs.  The
database file location is configured via the `DB_PATH` environment variable
(defaulting to `app.db` in the working directory).  If you wish to use a
different database (for example, PostgreSQL or Azure SQL), update the
`DATABASE_URL` accordingly and install the appropriate SQLAlchemy driver.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Determine path to database file.  When running inside a container the
# working directory is the repository root (see Dockerfile).
db_path = os.getenv("DB_PATH", "app.db")
DATABASE_URL = f"sqlite:///{db_path}"

# The `connect_args` ensure SQLite can operate in a multi‑threaded context
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()