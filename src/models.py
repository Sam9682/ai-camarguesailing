"""
Database models for Camargue Sailing website.

This module defines all SQLAlchemy models for the application,
including User, VerificationToken, Booking, ForumPost, and ForumReply.

Requirements: 2.2, 2.5, 3.1, 3.2, 7.2, 7.5
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, validates
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
        verification_tokens: Relationship to VerificationToken model
    
    Requirements: 2.2, 2.5
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False, server_default='false')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    verification_tokens = relationship('VerificationToken', back_populates='user', cascade='all, delete-orphan')
    bookings = relationship('Booking', back_populates='user', cascade='all, delete-orphan')
    forum_posts = relationship('ForumPost', back_populates='user', cascade='all, delete-orphan')
    forum_replies = relationship('ForumReply', back_populates='user', cascade='all, delete-orphan')
    
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



class VerificationToken(Base):
    """
    VerificationToken model for email verification.
    
    This model stores unique tokens sent to users for email verification.
    Each token has an expiration time to ensure security.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to the User who owns this token
        token: Unique verification token string
        expires_at: Timestamp when the token expires
        created_at: Timestamp when the token was created
        user: Relationship to the User model
    
    Requirements: 3.1, 3.2
    """
    __tablename__ = 'verification_tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='verification_tokens')
    
    def is_expired(self) -> bool:
        """
        Check if the verification token has expired.
        
        Returns:
            True if the token has expired, False otherwise
        
        Requirements: 3.4
        """
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<VerificationToken {self.token[:8]}... for user_id={self.user_id}>'


class Booking(Base):
    """
    Booking model representing voyage reservations.
    
    This model stores booking information for sailing voyages, including
    the user who made the booking, the date range, and booking status.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to the User who made the booking
        start_date: Start date of the booking period
        end_date: End date of the booking period
        status: Booking status (default: 'confirmed')
        created_at: Timestamp when the booking was created
        updated_at: Timestamp when the booking was last updated
        user: Relationship to the User model
    
    Constraints:
        - end_date must be greater than start_date
        - No overlapping bookings (enforced at application level)
    
    Requirements: 7.2, 7.5
    """
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    status = Column(String(50), default='confirmed', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='bookings')
    
    # Table-level constraint: end_date must be greater than start_date
    __table_args__ = (
        CheckConstraint('end_date > start_date', name='check_end_date_after_start_date'),
    )
    
    @validates('start_date', 'end_date')
    def validate_dates(self, key, value):
        """
        Validate booking dates.
        
        This validator only checks dates when updating existing bookings.
        For new bookings, the database constraint will enforce the rule.
        
        Args:
            key: The field being validated ('start_date' or 'end_date')
            value: The date value to validate
        
        Returns:
            The validated date value
        
        Raises:
            ValueError: If dates are invalid during update
        
        Requirements: 7.2, 7.5
        """
        # Only validate if this is an update (object already has an id)
        # For new objects, let the database constraint handle it
        if self.id is not None:
            if key == 'end_date' and hasattr(self, 'start_date') and self.start_date:
                if value <= self.start_date:
                    raise ValueError('End date must be after start date')
        return value
    
    def __repr__(self):
        return f'<Booking {self.id} user_id={self.user_id} {self.start_date} to {self.end_date}>'


class ForumPost(Base):
    """
    ForumPost model representing discussion forum posts.
    
    This model stores forum posts created by registered users, including
    the post title, content, author, and timestamps.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to the User who created the post
        title: Title of the forum post
        content: Text content of the post
        created_at: Timestamp when the post was created
        updated_at: Timestamp when the post was last updated
        user: Relationship to the User model
        replies: Relationship to ForumReply model
    
    Requirements: 8.2, 8.5
    """
    __tablename__ = 'forum_posts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(String, nullable=False)  # Text type for longer content
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='forum_posts')
    replies = relationship('ForumReply', back_populates='post', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ForumPost {self.id} "{self.title}" by user_id={self.user_id}>'


class ForumReply(Base):
    """
    ForumReply model representing replies to forum posts.
    
    This model stores replies to forum posts, including the reply content,
    author, and the post being replied to.
    
    Attributes:
        id: Primary key
        post_id: Foreign key to the ForumPost being replied to
        user_id: Foreign key to the User who created the reply
        content: Text content of the reply
        created_at: Timestamp when the reply was created
        post: Relationship to the ForumPost model
        user: Relationship to the User model
    
    Requirements: 8.4, 8.5
    """
    __tablename__ = 'forum_replies'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('forum_posts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = Column(String, nullable=False)  # Text type for longer content
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship('ForumPost', back_populates='replies')
    user = relationship('User', back_populates='forum_replies')
    
    def __repr__(self):
        return f'<ForumReply {self.id} on post_id={self.post_id} by user_id={self.user_id}>'
