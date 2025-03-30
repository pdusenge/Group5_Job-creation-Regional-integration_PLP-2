"""
Shopping cart and order processing for the Regional E-commerce Platform.
"""
from tabulate import tabulate

from config import TAX_RATE
from database import get_session, CartItem, Product, Order, OrderItem, OrderStatus, Business, User
from auth import login_required, merchant_required, get_current_user


@login_required
def add_to_cart(product_id, quantity=1):
    """
    Add a product to the shopping cart.
    
    Args:
        product_id (int): ID of the product to add
        quantity (int, optional): Quantity to add. Defaults to 1.
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    # First verify that we have a current user
    current_user = get_current_user()
    if not current_user or not hasattr(current_user, 'id') or not current_user.id:
        print(f"Debug - current_user: {current_user}")
        if current_user:
            print(f"Debug - has id: {hasattr(current_user, 'id')}")
            if hasattr(current_user, 'id'):
                print(f"Debug - id value: {current_user.id}")
        return False, "User session not found. Please log in again."
        
    session = get_session()
    try:
        # Validate inputs
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return False, "Quantity must be a positive number."
        except ValueError:
            return False, "Invalid quantity."
            
        # Check if product exists and is active
        product = session.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            return False, "Product not found or unavailable."
            
        # Check if there's enough stock
        if product.stock_quantity < quantity:
            return False, f"Not enough stock. Available: {product.stock_quantity}"
            
        # Check if product is already in cart
        cart_item = session.query(CartItem).filter(
            CartItem.user_id == current_user.id,
            CartItem.product_id == product_id
        ).first()
        
        if cart_item:
            # Update quantity if already in cart
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                return False, f"Cannot add more. Maximum available: {product.stock_quantity}"
                
            cart_item.quantity = new_quantity
            session.commit()
            return True, "Item quantity updated in cart."
        else:
            # Add new item to cart
            new_cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            
            session.add(new_cart_item)
            session.commit()
            return True, "Item added to cart."
            
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()