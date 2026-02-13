"""
Database models for Camargue Sailing website.

This module defines all SQLAlchemy models for the application,
including User, VerificationToken, Booking, ForumPost, and ForumReply.

Requirements: 2.2, 2.5
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from src.database import Base


class User(Base):
    """
    User model representing registered users in the system.
    
    Attributes:
        id: Primary key
        email: Unique email address for the user
        password_hash: Hashed password (never store plaintext passwords)
        is_verified: Whether the user has verified their email address
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
    
    Requirements: 2.2, 2.5
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def set_password(self, password: str) -> None:
        """
        Hash and store the user's password.
        
        Args:
            password: Plaintext password to hash
        
        Requirements: 2.5
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plaintext password to verify
        
        Returns:
            True if the password matches, False otherwise
        
        Requirements: 2.5
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'
