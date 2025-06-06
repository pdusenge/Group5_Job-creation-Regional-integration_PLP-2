"""
Authentication and user management for the Regional E-commerce Platform.
"""
import bcrypt
from sqlalchemy.exc import IntegrityError
import sqlalchemy.orm

from config import PASSWORD_SALT_ROUNDS
from database import get_session, User, UserRole, Business

class UserSession:
    def __init__(self):
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
        
        # Set as current user
        set_current_user(user_copy)
        
        return True, user_copy
        
    except IntegrityError:
        session.rollback()
        return False, "Database error. Please try again."
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()


def login(username_or_email, password):
    """
    Log in a user.
    
    Args:
        username_or_email (str): Username or email for login
        password (str): User's password
        
    Returns:
        tuple: (bool, User|str) - Success status and User object or error message
    """
    session = get_session()
    try:
        # Find user by username or email
        user = session.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            return False, "User not found."
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Create a complete copy with all necessary attributes
            user_copy = User(
                id=user.id,
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                role=user.role,
                created_at=user.created_at
            )
            
            # Set the current user in the session
            set_current_user(user_copy)
            
            return True, user_copy
        else:
            return False, "Incorrect password."
            
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        session.close()


def get_user_by_id(user_id):
    """
    Get user by ID.
    
    Args:
        user_id (int): User ID to search for
        
    Returns:
        User: User object if found, None otherwise
    """
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        # Create a copy to return after session close
        user_copy = User(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            created_at=user.created_at
        )
        return user_copy
    finally:
        session.close()


def login_required(func):
    """
    Decorator to check if user is logged in.
    
    Args:
        func: The function to be decorated
        
    Returns:
        function: The decorated function
    """
    def wrapper(*args, **kwargs):
        current_user = get_current_user()
        if current_user is None or not hasattr(current_user, 'id'):
            print("\nYou must be logged in to access this feature.")
            return None
        return func(*args, **kwargs)
    return wrapper


def merchant_required(func):
    """
    Decorator to check if user is a merchant.
    
    Args:
        func: The function to be decorated
        
    Returns:
        function: The decorated function
    """
    def wrapper(*args, **kwargs):
        current_user = get_current_user()
        if current_user is None or not hasattr(current_user, 'role') or current_user.role != UserRole.MERCHANT:
            print("\nThis feature is only available to merchants.")
            return None
        return func(*args, **kwargs)
    return wrapper


def register_business(name, description, contact_email=None):
    """
    Register a new business for the current merchant user.
    
    Args:
        name (str): Business name
        description (str): Business description
        contact_email (str, optional): Contact email. Defaults to None.
        
    Returns:
        tuple: (bool, Business|str) - Success status and Business object or error message
    """
    current_user = get_current_user()
    if not current_user or current_user.role != UserRole.MERCHANT:
        return False, "Only merchants can register businesses."
        
    session = get_session()
    try:
        # Check if user already has a business
        existing_business = session.query(Business).filter(
            Business.owner_id == current_user.id
        ).first()
        
        if existing_business:
            return False, "You already have a registered business."
        
        # Create new business
        new_business = Business(
            owner_id=current_user.id,
            name=name,
            description=description,
            contact_email=contact_email or current_user.email
        )
        
        session.add(new_business)
        session.commit()
        
        # Create a copy to return
        business_copy = Business(
            id=new_business.id,
            owner_id=new_business.owner_id,
            name=new_business.name,
            description=new_business.description,
            contact_email=new_business.contact_email
        )
            
        return True, business_copy
        
    except IntegrityError:
        session.rollback()
        return False, "Database error. Please try again."
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()


def has_business(user_id):
    """
    Check if a user has a registered business.
    
    Args:
        user_id (int): User ID to check
        
    Returns:
        bool: True if user has a business, False otherwise
    """
    session = get_session()
    try:
        business = session.query(Business).filter(
            Business.owner_id == user_id
        ).first()
        return business is not None
    finally:
        session.close()


def get_business(user_id):
    """
    Get business information for a user.
    
    Args:
        user_id (int): User ID to get business for
        
    Returns:
        Business: Business object if found, None otherwise
    """
    session = get_session()
    try:
        business = session.query(Business).filter(
            Business.owner_id == user_id
        ).first()
        
        if not business:
            return None
            
        # Create a copy to return after session close
        business_copy = Business(
            id=business.id,
            owner_id=business.owner_id,
            name=business.name,
            description=business.description,
            contact_email=business.contact_email
        )
        return business_copy
    finally:
        session.close()