"""
Forum module for Camargue Sailing website.

This module provides functions for managing forum posts and replies,
including fetching posts with replies, creating new posts, and adding replies.

Requirements: 8.1, 8.2, 8.4
"""

from typing import List, Optional
from src.database import db_session
from src.models import ForumPost, ForumReply, User


def get_all_posts() -> List[ForumPost]:
    """
    Fetch all forum posts with their replies, ordered by creation date.
    
    This function retrieves all forum posts from the database, ordered by
    creation date (newest first). Each post includes its associated user
    and replies through SQLAlchemy relationships.
    
    Returns:
        A list of ForumPost objects, each with user and replies loaded
    
    Requirements: 8.1
    """
    try:
        # Query all posts ordered by creation date (newest first)
        posts = db_session.query(ForumPost).order_by(
            ForumPost.created_at.desc()
        ).all()
        
        return posts
    except Exception as e:
        # Log database errors during post retrieval
        import logging
        logging.error(f"Database error during forum post retrieval: {str(e)}")
        # Return empty list on error to allow page to render
        return []


def create_post(user_id: int, title: str, content: str) -> ForumPost:
    """
    Create a new forum post.
    
    This function validates the input data and creates a new forum post
    associated with the specified user. The post is stored in the database
    with the current timestamp.
    
    Args:
        user_id: ID of the user creating the post
        title: Title of the forum post
        content: Text content of the post
    
    Returns:
        The newly created ForumPost object
    
    Raises:
        ValueError: If validation fails or user doesn't exist
    
    Requirements: 8.2
    """
    # Validate inputs
    if not title or not isinstance(title, str):
        raise ValueError("Title is required and must be a string")
    
    if not content or not isinstance(content, str):
        raise ValueError("Content is required and must be a string")
    
    if len(title.strip()) == 0:
        raise ValueError("Title cannot be empty")
    
    if len(content.strip()) == 0:
        raise ValueError("Content cannot be empty")
    
    if len(title) > 255:
        raise ValueError("Title is too long (maximum 255 characters)")
    
    # Verify user exists
    user = db_session.query(User).filter_by(id=user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} does not exist")
    
    # Create the forum post
    post = ForumPost(
        user_id=user_id,
        title=title.strip(),
        content=content.strip()
    )
    
    try:
        db_session.add(post)
        db_session.commit()
        return post
    except Exception as e:
        db_session.rollback()
        # Log the specific database error
        import logging
        logging.error(f"Database error during forum post creation: {str(e)}")
        raise ValueError(f"Failed to create forum post: {str(e)}")


def create_reply(post_id: int, user_id: int, content: str) -> ForumReply:
    """
    Add a reply to an existing forum post.
    
    This function validates the input data and creates a new reply
    associated with the specified post and user. The reply is stored
    in the database with the current timestamp.
    
    Args:
        post_id: ID of the post being replied to
        user_id: ID of the user creating the reply
        content: Text content of the reply
    
    Returns:
        The newly created ForumReply object
    
    Raises:
        ValueError: If validation fails, post doesn't exist, or user doesn't exist
    
    Requirements: 8.4
    """
    # Validate content
    if not content or not isinstance(content, str):
        raise ValueError("Content is required and must be a string")
    
    if len(content.strip()) == 0:
        raise ValueError("Content cannot be empty")
    
    # Verify post exists
    post = db_session.query(ForumPost).filter_by(id=post_id).first()
    if not post:
        raise ValueError(f"Forum post with id {post_id} does not exist")
    
    # Verify user exists
    user = db_session.query(User).filter_by(id=user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} does not exist")
    
    # Create the reply
    reply = ForumReply(
        post_id=post_id,
        user_id=user_id,
        content=content.strip()
    )
    
    try:
        db_session.add(reply)
        db_session.commit()
        return reply
    except Exception as e:
        db_session.rollback()
        # Log the specific database error
        import logging
        logging.error(f"Database error during reply creation: {str(e)}")
        raise ValueError(f"Failed to create reply: {str(e)}")
