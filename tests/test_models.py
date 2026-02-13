"""
Unit tests for database models.

This module tests the User and VerificationToken models to ensure
they are correctly defined and relationships work as expected.

Requirements: 2.2, 3.1, 3.2
"""

import pytest
from datetime import datetime, timedelta
from src.models import User, VerificationToken
from src.database import Base, engine, db_session


@pytest.fixture(scope='function')
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    db_session.remove()
    Base.metadata.drop_all(bind=engine)


def test_verification_token_creation(setup_database):
    """Test that VerificationToken can be created with user relationship."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create a verification token
    token = VerificationToken(
        user_id=user.id,
        token='test_token_12345',
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db_session.add(token)
    db_session.commit()
    
    # Verify the token was created
    assert token.id is not None
    assert token.user_id == user.id
    assert token.token == 'test_token_12345'
    assert token.expires_at > datetime.utcnow()
    assert token.created_at is not None


def test_verification_token_user_relationship(setup_database):
    """Test that VerificationToken has correct relationship with User."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create a verification token
    token = VerificationToken(
        user_id=user.id,
        token='test_token_12345',
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db_session.add(token)
    db_session.commit()
    
    # Test relationship from token to user
    assert token.user is not None
    assert token.user.email == 'test@example.com'
    
    # Test relationship from user to tokens
    assert len(user.verification_tokens) == 1
    assert user.verification_tokens[0].token == 'test_token_12345'


def test_verification_token_is_expired(setup_database):
    """Test the is_expired method of VerificationToken."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create an expired token
    expired_token = VerificationToken(
        user_id=user.id,
        token='expired_token',
        expires_at=datetime.utcnow() - timedelta(hours=1)
    )
    db_session.add(expired_token)
    
    # Create a valid token
    valid_token = VerificationToken(
        user_id=user.id,
        token='valid_token',
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db_session.add(valid_token)
    db_session.commit()
    
    # Test expiration
    assert expired_token.is_expired() is True
    assert valid_token.is_expired() is False


def test_verification_token_unique_constraint(setup_database):
    """Test that token field has unique constraint."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create first token
    token1 = VerificationToken(
        user_id=user.id,
        token='duplicate_token',
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db_session.add(token1)
    db_session.commit()
    
    # Try to create second token with same token string
    token2 = VerificationToken(
        user_id=user.id,
        token='duplicate_token',
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db_session.add(token2)
    
    # Should raise an integrity error
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        db_session.commit()


def test_verification_token_cascade_delete(setup_database):
    """Test that deleting a user cascades to delete verification tokens."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create verification tokens
    token1 = VerificationToken(
        user_id=user.id,
        token='token1',
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    token2 = VerificationToken(
        user_id=user.id,
        token='token2',
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db_session.add_all([token1, token2])
    db_session.commit()
    
    user_id = user.id
    
    # Delete the user
    db_session.delete(user)
    db_session.commit()
    
    # Verify tokens were deleted
    remaining_tokens = db_session.query(VerificationToken).filter_by(user_id=user_id).all()
    assert len(remaining_tokens) == 0



def test_booking_creation(setup_database):
    """Test that Booking can be created with valid dates."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create a booking
    from datetime import date
    from src.models import Booking
    
    booking = Booking(
        user_id=user.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 8),
        status='confirmed'
    )
    db_session.add(booking)
    db_session.commit()
    
    # Verify the booking was created
    assert booking.id is not None
    assert booking.user_id == user.id
    assert booking.start_date == date(2024, 6, 1)
    assert booking.end_date == date(2024, 6, 8)
    assert booking.status == 'confirmed'
    assert booking.created_at is not None


def test_booking_user_relationship(setup_database):
    """Test that Booking has correct relationship with User."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create bookings
    from datetime import date
    from src.models import Booking
    
    booking1 = Booking(
        user_id=user.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 8)
    )
    booking2 = Booking(
        user_id=user.id,
        start_date=date(2024, 7, 1),
        end_date=date(2024, 7, 8)
    )
    db_session.add_all([booking1, booking2])
    db_session.commit()
    
    # Test relationship from booking to user
    assert booking1.user is not None
    assert booking1.user.email == 'test@example.com'
    
    # Test relationship from user to bookings
    assert len(user.bookings) == 2


def test_booking_end_date_constraint(setup_database):
    """Test that end_date must be after start_date (database constraint)."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Try to create a booking with end_date before start_date
    from datetime import date
    from src.models import Booking
    
    booking = Booking(
        user_id=user.id,
        start_date=date(2024, 6, 8),
        end_date=date(2024, 6, 1)  # Before start_date
    )
    db_session.add(booking)
    
    # Should raise an integrity error due to check constraint
    with pytest.raises(Exception):
        db_session.commit()


def test_booking_end_date_validation(setup_database):
    """Test that end_date validation works at the model level."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create a booking with valid dates first
    from datetime import date
    from src.models import Booking
    
    booking = Booking(
        user_id=user.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 8)
    )
    db_session.add(booking)
    db_session.commit()
    
    # Try to update end_date to be before start_date
    with pytest.raises(ValueError, match='End date must be after start date'):
        booking.end_date = date(2024, 5, 1)


def test_booking_cascade_delete(setup_database):
    """Test that deleting a user cascades to delete bookings."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create bookings
    from datetime import date
    from src.models import Booking
    
    booking1 = Booking(
        user_id=user.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 8)
    )
    booking2 = Booking(
        user_id=user.id,
        start_date=date(2024, 7, 1),
        end_date=date(2024, 7, 8)
    )
    db_session.add_all([booking1, booking2])
    db_session.commit()
    
    user_id = user.id
    
    # Delete the user
    db_session.delete(user)
    db_session.commit()
    
    # Verify bookings were deleted
    from src.models import Booking
    remaining_bookings = db_session.query(Booking).filter_by(user_id=user_id).all()
    assert len(remaining_bookings) == 0


def test_booking_default_status(setup_database):
    """Test that Booking has default status of 'confirmed'."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create a booking without specifying status
    from datetime import date
    from src.models import Booking
    
    booking = Booking(
        user_id=user.id,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 8)
    )
    db_session.add(booking)
    db_session.commit()
    
    # Verify default status
    assert booking.status == 'confirmed'



def test_forum_post_creation(setup_database):
    """Test that ForumPost can be created with user relationship."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create a forum post
    from src.models import ForumPost
    
    post = ForumPost(
        user_id=user.id,
        title='Test Post Title',
        content='This is the content of the test post.'
    )
    db_session.add(post)
    db_session.commit()
    
    # Verify the post was created
    assert post.id is not None
    assert post.user_id == user.id
    assert post.title == 'Test Post Title'
    assert post.content == 'This is the content of the test post.'
    assert post.created_at is not None
    assert post.updated_at is not None


def test_forum_post_user_relationship(setup_database):
    """Test that ForumPost has correct relationship with User."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create forum posts
    from src.models import ForumPost
    
    post1 = ForumPost(
        user_id=user.id,
        title='First Post',
        content='Content of first post'
    )
    post2 = ForumPost(
        user_id=user.id,
        title='Second Post',
        content='Content of second post'
    )
    db_session.add_all([post1, post2])
    db_session.commit()
    
    # Test relationship from post to user
    assert post1.user is not None
    assert post1.user.email == 'test@example.com'
    
    # Test relationship from user to posts
    assert len(user.forum_posts) == 2


def test_forum_reply_creation(setup_database):
    """Test that ForumReply can be created with post and user relationships."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create a forum post
    from src.models import ForumPost, ForumReply
    
    post = ForumPost(
        user_id=user.id,
        title='Test Post',
        content='Test content'
    )
    db_session.add(post)
    db_session.commit()
    
    # Create a reply
    reply = ForumReply(
        post_id=post.id,
        user_id=user.id,
        content='This is a reply to the post.'
    )
    db_session.add(reply)
    db_session.commit()
    
    # Verify the reply was created
    assert reply.id is not None
    assert reply.post_id == post.id
    assert reply.user_id == user.id
    assert reply.content == 'This is a reply to the post.'
    assert reply.created_at is not None


def test_forum_reply_relationships(setup_database):
    """Test that ForumReply has correct relationships with Post and User."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create a forum post
    from src.models import ForumPost, ForumReply
    
    post = ForumPost(
        user_id=user.id,
        title='Test Post',
        content='Test content'
    )
    db_session.add(post)
    db_session.commit()
    
    # Create replies
    reply1 = ForumReply(
        post_id=post.id,
        user_id=user.id,
        content='First reply'
    )
    reply2 = ForumReply(
        post_id=post.id,
        user_id=user.id,
        content='Second reply'
    )
    db_session.add_all([reply1, reply2])
    db_session.commit()
    
    # Test relationship from reply to post
    assert reply1.post is not None
    assert reply1.post.title == 'Test Post'
    
    # Test relationship from reply to user
    assert reply1.user is not None
    assert reply1.user.email == 'test@example.com'
    
    # Test relationship from post to replies
    assert len(post.replies) == 2
    
    # Test relationship from user to replies
    assert len(user.forum_replies) == 2


def test_forum_post_cascade_delete(setup_database):
    """Test that deleting a user cascades to delete forum posts."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create forum posts
    from src.models import ForumPost
    
    post1 = ForumPost(
        user_id=user.id,
        title='Post 1',
        content='Content 1'
    )
    post2 = ForumPost(
        user_id=user.id,
        title='Post 2',
        content='Content 2'
    )
    db_session.add_all([post1, post2])
    db_session.commit()
    
    user_id = user.id
    
    # Delete the user
    db_session.delete(user)
    db_session.commit()
    
    # Verify posts were deleted
    from src.models import ForumPost
    remaining_posts = db_session.query(ForumPost).filter_by(user_id=user_id).all()
    assert len(remaining_posts) == 0


def test_forum_reply_cascade_delete_with_post(setup_database):
    """Test that deleting a post cascades to delete replies."""
    # Create a user
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Create a forum post
    from src.models import ForumPost, ForumReply
    
    post = ForumPost(
        user_id=user.id,
        title='Test Post',
        content='Test content'
    )
    db_session.add(post)
    db_session.commit()
    
    # Create replies
    reply1 = ForumReply(
        post_id=post.id,
        user_id=user.id,
        content='Reply 1'
    )
    reply2 = ForumReply(
        post_id=post.id,
        user_id=user.id,
        content='Reply 2'
    )
    db_session.add_all([reply1, reply2])
    db_session.commit()
    
    post_id = post.id
    
    # Delete the post
    db_session.delete(post)
    db_session.commit()
    
    # Verify replies were deleted
    from src.models import ForumReply
    remaining_replies = db_session.query(ForumReply).filter_by(post_id=post_id).all()
    assert len(remaining_replies) == 0


def test_forum_reply_cascade_delete_with_user(setup_database):
    """Test that deleting a user cascades to delete their replies."""
    # Create users
    user1 = User(email='user1@example.com')
    user1.set_password('password123')
    user2 = User(email='user2@example.com')
    user2.set_password('password123')
    db_session.add_all([user1, user2])
    db_session.commit()
    
    # Create a forum post by user1
    from src.models import ForumPost, ForumReply
    
    post = ForumPost(
        user_id=user1.id,
        title='Test Post',
        content='Test content'
    )
    db_session.add(post)
    db_session.commit()
    
    # Create replies by both users
    reply1 = ForumReply(
        post_id=post.id,
        user_id=user1.id,
        content='Reply by user1'
    )
    reply2 = ForumReply(
        post_id=post.id,
        user_id=user2.id,
        content='Reply by user2'
    )
    db_session.add_all([reply1, reply2])
    db_session.commit()
    
    user2_id = user2.id
    
    # Delete user2
    db_session.delete(user2)
    db_session.commit()
    
    # Verify user2's reply was deleted but user1's reply remains
    from src.models import ForumReply
    remaining_replies = db_session.query(ForumReply).filter_by(post_id=post.id).all()
    assert len(remaining_replies) == 1
    assert remaining_replies[0].user_id == user1.id
    
    # Verify no replies exist for user2
    user2_replies = db_session.query(ForumReply).filter_by(user_id=user2_id).all()
    assert len(user2_replies) == 0
