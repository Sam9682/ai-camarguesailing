"""
Unit tests for database module.

Tests database connection initialization and base model class.
Requirements: 9.2
"""

import pytest
from sqlalchemy import Column, Integer, String
from src.database import Base, engine, db_session, init_db, close_db


def test_base_model_exists():
    """Test that Base model class is properly initialized."""
    assert Base is not None
    assert hasattr(Base, 'metadata')


def test_engine_exists():
    """Test that database engine is properly initialized."""
    assert engine is not None
    assert engine.url is not None


def test_db_session_exists():
    """Test that database session is properly initialized."""
    assert db_session is not None


def test_create_simple_model():
    """Test that we can create a simple model using Base."""
    
    class TestModel(Base):
        __tablename__ = 'test_model'
        id = Column(Integer, primary_key=True)
        name = Column(String(50))
    
    # Verify the model has the correct table name
    assert TestModel.__tablename__ == 'test_model'
    
    # Verify the model has the correct columns
    assert 'id' in TestModel.__table__.columns
    assert 'name' in TestModel.__table__.columns


def test_init_db_callable():
    """Test that init_db function is callable."""
    assert callable(init_db)


def test_close_db_callable():
    """Test that close_db function is callable."""
    assert callable(close_db)


def test_session_query_property():
    """Test that Base has query property for session."""
    assert hasattr(Base, 'query')
