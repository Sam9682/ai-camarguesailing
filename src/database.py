"""
Database module for Camargue Sailing website.

This module initializes the database connection using SQLAlchemy
and provides the base model class for all database models.

Requirements: 9.2
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError, IntegrityError, DatabaseError
from src.config import Config

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine with error handling
try:
    engine = create_engine(
        Config.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=False           # Set to True for SQL query logging during development
    )
    
    # Test the connection
    with engine.connect() as connection:
        logger.info("Database connection established successfully")
        
except OperationalError as e:
    logger.error(f"Failed to connect to database: {str(e)}")
    raise RuntimeError(f"Database connection failed: {str(e)}")
except Exception as e:
    logger.error(f"Unexpected error during database initialization: {str(e)}")
    raise RuntimeError(f"Database initialization failed: {str(e)}")

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
    
    Raises:
        RuntimeError: If database initialization fails
    """
    try:
        # Import all models here to ensure they are registered with Base
        from src.models import User, VerificationToken, Booking, ForumPost, ForumReply  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except OperationalError as e:
        logger.error(f"Database connection error during initialization: {str(e)}")
        raise RuntimeError(f"Failed to initialize database - connection error: {str(e)}")
    except DatabaseError as e:
        logger.error(f"Database error during table creation: {str(e)}")
        raise RuntimeError(f"Failed to create database tables: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        raise RuntimeError(f"Database initialization failed: {str(e)}")


def close_db():
    """
    Close the database session.
    
    This function should be called when shutting down the application
    or at the end of a request to clean up database connections.
    """
    try:
        db_session.remove()
    except Exception as e:
        logger.warning(f"Error while closing database session: {str(e)}")
