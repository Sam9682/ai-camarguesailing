"""
Database module for Camargue Sailing website.

This module initializes the database connection using SQLAlchemy
and provides the base model class for all database models.

Requirements: 9.2
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from src.config import Config

# Create database engine
engine = create_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Set to True for SQL query logging during development
)

# Create session factory
session_factory = sessionmaker(bind=engine)

# Create scoped session for thread-safe database access
db_session = scoped_session(session_factory)

# Create base class for all models
Base = declarative_base()

# Bind the base to the engine
Base.query = db_session.query_property()


def init_db():
    """
    Initialize the database by creating all tables.
    
    This function should be called when setting up the application
    for the first time or when running migrations.
    """
    # Import all models here to ensure they are registered with Base
    from src.models import User, VerificationToken  # noqa: F401
    Base.metadata.create_all(bind=engine)


def close_db():
    """
    Close the database session.
    
    This function should be called when shutting down the application
    or at the end of a request to clean up database connections.
    """
    db_session.remove()
