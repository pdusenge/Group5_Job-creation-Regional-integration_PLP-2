"""
Authentication and user management for the Regional E-commerce Platform.
"""
import bcrypt
from sqlalchemy.exc import IntegrityError
import sqlalchemy.orm

from config import PASSWORD_SALT_ROUNDS
from database import get_session, User, UserRole, Business

class UserSession:
    def _init_(self):
        self.current_user = None

# Create a singleton instance
user_session = UserSession()

def get_current_user():
    """Get the current logged in user."""
    return user_session.current_user

def set_current_user(user):
    """Set the current logged in user."""
    user_session.current_user = user
    
def clear_current_user():
    """Clear the current user session."""
    user_session.current_user = None


def register_user(username, email, password, role=UserRole.CUSTOMER):
    """
    Register a new user.
    
    Args:
        username (str): User's username
        email (str): User's email
        password (str): User's password in plaintext
        role (UserRole, optional): User's role. Defaults to UserRole.CUSTOMER.
        
    Returns:
        tuple: (bool, User|str) - Success status and User object or error message
    """
    session = get_session()
    try:
