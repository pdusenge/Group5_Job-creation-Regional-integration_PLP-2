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
# Check if username or email already exists
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return False, "Username already taken."
            else:
                return False, "Email already registered."
        
        # Hash the password
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt(rounds=PASSWORD_SALT_ROUNDS)
        ).decode('utf-8')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        
        session.add(new_user)
        session.commit()
        
        # Create a fresh copy to return after session close
        user_copy = User(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            password_hash=new_user.password_hash,
            role=new_user.role,
            created_at=new_user.created_at
        )
        
