"""
Database helper functions for the Regional E-commerce Platform.
"""
from database import get_session, User, Business, UserRole


def get_user_info(user_id):
    """
    Get basic information about a user.
    
    Args:
        user_id (int): User ID to lookup
        
    Returns:
        tuple: (user, business, is_merchant) - User object, Business object, and boolean
    """
    if not user_id:
        return None, None, False
        
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None, None, False
            
        # Get business information separately
        business = session.query(Business).filter(Business.owner_id == user_id).first()
        
        is_merchant = (user.role == UserRole.MERCHANT)
        
        # Create copies to use after session closes
        user_copy = None
        business_copy = None
        
        if user:
            user_copy = User(
                id=user.id,
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                role=user.role,
                created_at=user.created_at
            )
            
        if business:
            business_copy = Business(
                id=business.id,
                owner_id=business.owner_id,
                name=business.name,
                description=business.description,
                contact_email=business.contact_email
            )
        
        return user_copy, business_copy, is_merchant
    except Exception as e:
        print(f"Error retrieving user info: {e}")
        return None, None, False
    finally:
        session.close()


def get_business_info(business_id):
    """
    Get information about a business.
    
    Args:
        business_id (int): Business ID to lookup
        
    Returns:
        Business: Business object if found, None otherwise
    """
    if not business_id:
        return None
        
    session = get_session()
    try:
        business = session.query(Business).filter(Business.id == business_id).first()
        
        if not business:
            return None
            
        # Create a copy to use after session closes
        business_copy = Business(
            id=business.id,
            owner_id=business.owner_id,
            name=business.name,
            description=business.description,
            contact_email=business.contact_email
        )
        
        return business_copy
    except Exception as e:
        print(f"Error retrieving business info: {e}")
        return None
    finally:
        session.close()