"""
Tests for the forum module.

This module contains unit tests for the forum functions,
including get_all_posts(), create_post(), and create_reply().

Requirements: 8.1, 8.2, 8.4
"""

import pytest
from src.forum import get_all_posts, create_post, create_reply
from src.models import User, ForumPost, ForumReply
from src.database import db_session, Base, engine


@pytest.fixture(scope='function')
def setup_database():
    """Create tables and clean up after each test."""
    Base.metadata.create_all(bind=engine)
    yield
    db_session.rollback()
    db_session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(setup_database):
    """Create a test user for forum tests."""
    user = User(email='test@example.com', is_verified=True)
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_user2(setup_database):
    """Create a second test user for forum tests."""
    user = User(email='test2@example.com', is_verified=True)
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


class TestGetAllPosts:
    """Tests for get_all_posts() function."""
    
    def test_empty_forum(self, setup_database):
        """Test getting posts when forum is empty."""
        posts = get_all_posts()
        assert posts == []
    
    def test_single_post(self, test_user):
        """Test getting a single forum post."""
        # Create a post
        post = ForumPost(
            user_id=test_user.id,
            title='Test Post',
            content='This is a test post content'
        )
        db_session.add(post)
        db_session.commit()
        
        # Fetch all posts
        posts = get_all_posts()
        
        assert len(posts) == 1
        assert posts[0].title == 'Test Post'
        assert posts[0].content == 'This is a test post content'
        assert posts[0].user_id == test_user.id
        assert posts[0].user.email == test_user.email
    
    def test_multiple_posts_ordered_by_date(self, test_user, test_user2):
        """Test getting multiple posts ordered by creation date (newest first)."""
        # Create multiple posts
        post1 = ForumPost(
            user_id=test_user.id,
            title='First Post',
            content='Content 1'
        )
        db_session.add(post1)
        db_session.commit()
        
        post2 = ForumPost(
            user_id=test_user2.id,
            title='Second Post',
            content='Content 2'
        )
        db_session.add(post2)
        db_session.commit()
        
        post3 = ForumPost(
            user_id=test_user.id,
            title='Third Post',
            content='Content 3'
        )
        db_session.add(post3)
        db_session.commit()
        
        # Fetch all posts
        posts = get_all_posts()
        
        assert len(posts) == 3
        # Should be ordered newest first
        assert posts[0].title == 'Third Post'
        assert posts[1].title == 'Second Post'
        assert posts[2].title == 'First Post'
    
    def test_posts_with_replies(self, test_user, test_user2):
        """Test getting posts that have replies."""
        # Create a post
        post = ForumPost(
            user_id=test_user.id,
            title='Post with Replies',
            content='Original content'
        )
        db_session.add(post)
        db_session.commit()
        
        # Add replies
        reply1 = ForumReply(
            post_id=post.id,
            user_id=test_user2.id,
            content='First reply'
        )
        reply2 = ForumReply(
            post_id=post.id,
            user_id=test_user.id,
            content='Second reply'
        )
        db_session.add(reply1)
        db_session.add(reply2)
        db_session.commit()
        
        # Fetch all posts
        posts = get_all_posts()
        
        assert len(posts) == 1
        assert len(posts[0].replies) == 2
        assert posts[0].replies[0].content == 'First reply'
        assert posts[0].replies[1].content == 'Second reply'


class TestCreatePost:
    """Tests for create_post() function."""
    
    def test_create_post_success(self, test_user):
        """Test successful post creation."""
        post = create_post(
            user_id=test_user.id,
            title='My First Post',
            content='This is the content of my first post'
        )
        
        assert post is not None
        assert post.id is not None
        assert post.user_id == test_user.id
        assert post.title == 'My First Post'
        assert post.content == 'This is the content of my first post'
        assert post.created_at is not None
        assert post.updated_at is not None
    
    def test_create_post_strips_whitespace(self, test_user):
        """Test that post creation strips leading/trailing whitespace."""
        post = create_post(
            user_id=test_user.id,
            title='  Title with spaces  ',
            content='  Content with spaces  '
        )
        
        assert post.title == 'Title with spaces'
        assert post.content == 'Content with spaces'
    
    def test_create_post_empty_title(self, test_user):
        """Test post creation with empty title."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            create_post(
                user_id=test_user.id,
                title='   ',
                content='Valid content'
            )
    
    def test_create_post_empty_content(self, test_user):
        """Test post creation with empty content."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            create_post(
                user_id=test_user.id,
                title='Valid Title',
                content='   '
            )
    
    def test_create_post_missing_title(self, test_user):
        """Test post creation with missing title."""
        with pytest.raises(ValueError, match="Title is required"):
            create_post(
                user_id=test_user.id,
                title=None,
                content='Valid content'
            )
    
    def test_create_post_missing_content(self, test_user):
        """Test post creation with missing content."""
        with pytest.raises(ValueError, match="Content is required"):
            create_post(
                user_id=test_user.id,
                title='Valid Title',
                content=None
            )
    
    def test_create_post_invalid_title_type(self, test_user):
        """Test post creation with non-string title."""
        with pytest.raises(ValueError, match="Title is required and must be a string"):
            create_post(
                user_id=test_user.id,
                title=123,
                content='Valid content'
            )
    
    def test_create_post_invalid_content_type(self, test_user):
        """Test post creation with non-string content."""
        with pytest.raises(ValueError, match="Content is required and must be a string"):
            create_post(
                user_id=test_user.id,
                title='Valid Title',
                content=123
            )
    
    def test_create_post_title_too_long(self, test_user):
        """Test post creation with title exceeding maximum length."""
        long_title = 'A' * 256  # Exceeds 255 character limit
        
        with pytest.raises(ValueError, match="Title is too long"):
            create_post(
                user_id=test_user.id,
                title=long_title,
                content='Valid content'
            )
    
    def test_create_post_nonexistent_user(self, setup_database):
        """Test post creation with non-existent user ID."""
        with pytest.raises(ValueError, match="User with id 99999 does not exist"):
            create_post(
                user_id=99999,
                title='Valid Title',
                content='Valid content'
            )
    
    def test_create_post_persists_to_database(self, test_user):
        """Test that created post is persisted to database."""
        post = create_post(
            user_id=test_user.id,
            title='Persistent Post',
            content='This should be saved'
        )
        post_id = post.id
        
        # Clear session and query again to verify persistence
        db_session.expire_all()
        
        retrieved_post = db_session.query(ForumPost).filter_by(id=post_id).first()
        assert retrieved_post is not None
        assert retrieved_post.title == 'Persistent Post'
        assert retrieved_post.content == 'This should be saved'
        assert retrieved_post.user_id == test_user.id
    
    def test_create_multiple_posts_same_user(self, test_user):
        """Test creating multiple posts by the same user."""
        post1 = create_post(test_user.id, 'Post 1', 'Content 1')
        post2 = create_post(test_user.id, 'Post 2', 'Content 2')
        
        assert post1.id != post2.id
        assert post1.user_id == post2.user_id
        
        posts = get_all_posts()
        assert len(posts) == 2
    
    def test_create_posts_different_users(self, test_user, test_user2):
        """Test creating posts by different users."""
        post1 = create_post(test_user.id, 'User 1 Post', 'Content 1')
        post2 = create_post(test_user2.id, 'User 2 Post', 'Content 2')
        
        assert post1.user_id != post2.user_id
        assert post1.user.email == 'test@example.com'
        assert post2.user.email == 'test2@example.com'


class TestCreateReply:
    """Tests for create_reply() function."""
    
    def test_create_reply_success(self, test_user, test_user2):
        """Test successful reply creation."""
        # Create a post first
        post = create_post(test_user.id, 'Original Post', 'Original content')
        
        # Create a reply
        reply = create_reply(
            post_id=post.id,
            user_id=test_user2.id,
            content='This is my reply'
        )
        
        assert reply is not None
        assert reply.id is not None
        assert reply.post_id == post.id
        assert reply.user_id == test_user2.id
        assert reply.content == 'This is my reply'
        assert reply.created_at is not None
    
    def test_create_reply_strips_whitespace(self, test_user):
        """Test that reply creation strips leading/trailing whitespace."""
        post = create_post(test_user.id, 'Post', 'Content')
        
        reply = create_reply(
            post_id=post.id,
            user_id=test_user.id,
            content='  Reply with spaces  '
        )
        
        assert reply.content == 'Reply with spaces'
    
    def test_create_reply_empty_content(self, test_user):
        """Test reply creation with empty content."""
        post = create_post(test_user.id, 'Post', 'Content')
        
        with pytest.raises(ValueError, match="Content cannot be empty"):
            create_reply(
                post_id=post.id,
                user_id=test_user.id,
                content='   '
            )
    
    def test_create_reply_missing_content(self, test_user):
        """Test reply creation with missing content."""
        post = create_post(test_user.id, 'Post', 'Content')
        
        with pytest.raises(ValueError, match="Content is required"):
            create_reply(
                post_id=post.id,
                user_id=test_user.id,
                content=None
            )
    
    def test_create_reply_invalid_content_type(self, test_user):
        """Test reply creation with non-string content."""
        post = create_post(test_user.id, 'Post', 'Content')
        
        with pytest.raises(ValueError, match="Content is required and must be a string"):
            create_reply(
                post_id=post.id,
                user_id=test_user.id,
                content=123
            )
    
    def test_create_reply_nonexistent_post(self, test_user):
        """Test reply creation with non-existent post ID."""
        with pytest.raises(ValueError, match="Forum post with id 99999 does not exist"):
            create_reply(
                post_id=99999,
                user_id=test_user.id,
                content='Valid content'
            )
    
    def test_create_reply_nonexistent_user(self, test_user):
        """Test reply creation with non-existent user ID."""
        post = create_post(test_user.id, 'Post', 'Content')
        
        with pytest.raises(ValueError, match="User with id 99999 does not exist"):
            create_reply(
                post_id=post.id,
                user_id=99999,
                content='Valid content'
            )
    
    def test_create_reply_persists_to_database(self, test_user):
        """Test that created reply is persisted to database."""
        post = create_post(test_user.id, 'Post', 'Content')
        reply = create_reply(post.id, test_user.id, 'My reply')
        reply_id = reply.id
        
        # Clear session and query again to verify persistence
        db_session.expire_all()
        
        retrieved_reply = db_session.query(ForumReply).filter_by(id=reply_id).first()
        assert retrieved_reply is not None
        assert retrieved_reply.content == 'My reply'
        assert retrieved_reply.post_id == post.id
        assert retrieved_reply.user_id == test_user.id
    
    def test_create_multiple_replies_same_post(self, test_user, test_user2):
        """Test creating multiple replies on the same post."""
        post = create_post(test_user.id, 'Post', 'Content')
        
        reply1 = create_reply(post.id, test_user2.id, 'First reply')
        reply2 = create_reply(post.id, test_user.id, 'Second reply')
        reply3 = create_reply(post.id, test_user2.id, 'Third reply')
        
        assert reply1.id != reply2.id != reply3.id
        assert reply1.post_id == reply2.post_id == reply3.post_id == post.id
        
        # Verify post has all replies
        db_session.expire_all()
        retrieved_post = db_session.query(ForumPost).filter_by(id=post.id).first()
        assert len(retrieved_post.replies) == 3
    
    def test_create_reply_user_can_reply_to_own_post(self, test_user):
        """Test that a user can reply to their own post."""
        post = create_post(test_user.id, 'My Post', 'My content')
        reply = create_reply(post.id, test_user.id, 'Replying to myself')
        
        assert reply.user_id == post.user_id
        assert reply.post_id == post.id
    
    def test_create_replies_different_posts(self, test_user, test_user2):
        """Test creating replies on different posts."""
        post1 = create_post(test_user.id, 'Post 1', 'Content 1')
        post2 = create_post(test_user2.id, 'Post 2', 'Content 2')
        
        reply1 = create_reply(post1.id, test_user2.id, 'Reply to post 1')
        reply2 = create_reply(post2.id, test_user.id, 'Reply to post 2')
        
        assert reply1.post_id == post1.id
        assert reply2.post_id == post2.id
        assert reply1.post_id != reply2.post_id
    
    def test_reply_relationships(self, test_user, test_user2):
        """Test that reply relationships are correctly established."""
        post = create_post(test_user.id, 'Post', 'Content')
        reply = create_reply(post.id, test_user2.id, 'Reply')
        
        # Test reply -> post relationship
        assert reply.post.id == post.id
        assert reply.post.title == 'Post'
        
        # Test reply -> user relationship
        assert reply.user.id == test_user2.id
        assert reply.user.email == 'test2@example.com'
        
        # Test post -> replies relationship
        db_session.expire_all()
        retrieved_post = db_session.query(ForumPost).filter_by(id=post.id).first()
        assert len(retrieved_post.replies) == 1
        assert retrieved_post.replies[0].id == reply.id
