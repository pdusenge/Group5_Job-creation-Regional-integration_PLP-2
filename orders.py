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


@login_required
def update_cart_item(cart_item_id, quantity):
    """
    Update the quantity of a cart item.
    
    Args:
        cart_item_id (int): ID of the cart item to update
        quantity (int): New quantity
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    session = get_session()
    current_user = get_current_user()
    try:
        # Validate inputs
        try:
            quantity = int(quantity)
        except ValueError:
            return False, "Invalid quantity."
        
        if quantity <= 0:
            return remove_from_cart(cart_item_id)
            
        # Find the cart item
        cart_item = session.query(CartItem).filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == current_user.id
        ).first()
        
        if not cart_item:
            return False, "Cart item not found."
            
        # Check product stock
        product = session.query(Product).filter(
            Product.id == cart_item.product_id
        ).first()
        
        if not product:
            return False, "Product not found."
            
        if quantity > product.stock_quantity:
            return False, f"Not enough stock. Available: {product.stock_quantity}"
            
        # Update quantity
        cart_item.quantity = quantity
        session.commit()
        return True, "Cart updated successfully."
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()


@login_required
def remove_from_cart(cart_item_id):
    """
    Remove an item from the shopping cart.
    
    Args:
        cart_item_id (int): ID of the cart item to remove
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    session = get_session()
    try:
        # Find the cart item
        cart_item = session.query(CartItem).filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == get_current_user().id
        ).first()
        
        if not cart_item:
            return False, "Cart item not found."
            
        # Remove the item
        session.delete(cart_item)
        session.commit()
        return True, "Item removed from cart."
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()


@login_required
def clear_cart():
    """
    Remove all items from the shopping cart.
    
    Returns:
        tuple: (bool, str) - Success status and message
    """
    session = get_session()
    try:
        # Delete all cart items for the current user
        session.query(CartItem).filter(
            CartItem.user_id == get_current_user().id
        ).delete()
        
        session.commit()
        return True, "Cart cleared successfully."
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()


@login_required
def view_cart():
    """
    View the contents of the shopping cart.
    
    Returns:
        tuple: (list, float) - List of cart items and total cost
    """
    current_user = get_current_user()
    if not current_user:
        print("\nUser session not found. Please log in again.")
        return [], 0
        
    session = get_session()
    try:
        # Get all cart items for the current user
        cart_items = session.query(CartItem).filter(
            CartItem.user_id == current_user.id
        ).all()
        
        if not cart_items:
            print("\nYour cart is empty.")
            return [], 0
            
        headers = ["ID", "Product", "Price", "Quantity", "Subtotal"]
        data = []
        total = 0
        
        for item in cart_items:
            # Get product information
            product = session.query(Product).filter(
                Product.id == item.product_id
            ).first()
            
            if product:
                subtotal = product.price * item.quantity
                total += subtotal
                
                data.append([
                    item.id,
                    product.name,
                    f"${product.price:.2f}",
                    item.quantity,
                    f"${subtotal:.2f}"
                ])
        
        print("\nYour Shopping Cart:")
        print(tabulate(data, headers=headers, tablefmt="pretty"))
        
        # Calculate tax and total with tax
        tax = total * TAX_RATE
        total_with_tax = total + tax
        
        print(f"\nSubtotal: ${total:.2f}")
        print(f"Tax ({TAX_RATE*100:.0f}%): ${tax:.2f}")
        print(f"Total: ${total_with_tax:.2f}")
        
        return cart_items, total_with_tax
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return [], 0
    finally:
        session.close()


@login_required
def checkout(shipping_address):
    """
    Process checkout from the shopping cart.
    
    Args:
        shipping_address (str): Delivery address
        
    Returns:
        tuple: (bool, Order|str) - Success status and Order object or error message
    """
    current_user = get_current_user()
    if not current_user:
        return False, "User session not found. Please log in again."
        
    session = get_session()
    try:
        # Get all cart items for the current user
        cart_items = session.query(CartItem).filter(
            CartItem.user_id == current_user.id
        ).all()
        
        if not cart_items:
            return False, "Your cart is empty."
            
        # Calculate total amount and verify stock availability
        total_amount = 0
        order_items_data = []
        insufficient_stock = []
        
        for cart_item in cart_items:
            product = session.query(Product).filter(
                Product.id == cart_item.product_id
            ).first()
            
            if not product:
                continue
                
            # Check if product is still active
            if not product.is_active:
                insufficient_stock.append(
                    f"{product.name} is no longer available."
                )
                continue
                
            # Check stock availability
            if product.stock_quantity < cart_item.quantity:
                insufficient_stock.append(
                    f"{product.name} has only {product.stock_quantity} available."
                )
                continue
                
            # Calculate item price
            subtotal = product.price * cart_item.quantity
            total_amount += subtotal
            
            # Add to order items data for later creation
            order_items_data.append({
                "product_id": product.id,
                "quantity": cart_item.quantity,
                "price_at_time": product.price
            })
        
        # If any items have insufficient stock, abort order
        if insufficient_stock:
            error_message = "Cannot create order due to inventory issues:\n"
            error_message += "\n".join(insufficient_stock)
            return False, error_message
            
        # Add tax to total amount
        tax = total_amount * TAX_RATE
        total_amount += tax
        
        # Create the order
        new_order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            shipping_address=shipping_address
        )
        
        session.add(new_order)
        session.flush()  # Get the order ID before committing
        
        # Create order items
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                price_at_time=item_data["price_at_time"]
            )
            session.add(order_item)
            
            # Reduce product stock
            product = session.query(Product).filter(
                Product.id == item_data["product_id"]
            ).first()
            product.stock_quantity -= item_data["quantity"]
        
        # Clear the cart
        session.query(CartItem).filter(
            CartItem.user_id == current_user.id
        ).delete()
        
        # Commit all changes
        session.commit()
        
        print("\nOrder created successfully!")
        print(f"Order #: {new_order.id}")
        print(f"Total: ${new_order.total_amount:.2f}")
        print(f"Status: {new_order.status.value}")
        
        return True, new_order
        
    except Exception as e:
        session.rollback()
        return False, f"Error creating order: {str(e)}"
    finally:
        session.close()


@login_required
def list_orders():
    """
    List all orders for the current user.
    
    Returns:
        list: List of Order objects
    """
    current_user = get_current_user()
    if not current_user:
        print("\nUser session not found. Please log in again.")
        return []
        
    session = get_session()
    try:
        orders = session.query(Order).filter(
            Order.user_id == current_user.id
        ).order_by(
            Order.created_at.desc()
        ).all()
        
        if orders:
            headers = ["Order #", "Date", "Total", "Status"]
            data = [
                [
                    o.id,
                    o.created_at.strftime("%Y-%m-%d"),
                    f"${o.total_amount:.2f}",
                    o.status.value
                ]
                for o in orders
            ]
            
            print("\nYour Orders:")
            print(tabulate(data, headers=headers, tablefmt="pretty"))
        else:
            print("\nYou don't have any orders yet.")
            
        return orders
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []
    finally:
        session.close()


@login_required
def view_order_details(order_id):
    """
    View details of a specific order.
    
    Args:
        order_id (int): ID of the order to view
        
    Returns:
        Order: Order object if found, None otherwise
    """
    current_user = get_current_user()
    if not current_user:
        print("\nUser session not found. Please log in again.")
        return None
        
    session = get_session()
    try:
        order = session.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        ).first()
        
        if not order:
            print(f"\nOrder #{order_id} not found or doesn't belong to you.")
            return None
            
        print(f"\nOrder #{order.id} Details:")
        print(f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Status: {order.status.value}")
        print(f"Shipping Address: {order.shipping_address}")
        
        # Get order items
        items = session.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()
        
        headers = ["Product", "Quantity", "Price", "Subtotal"]
        data = []
        subtotal = 0
        
        for item in items:
            # Get product information
            product = session.query(Product).filter(
                Product.id == item.product_id
            ).first()
            
            if product:
                item_subtotal = item.price_at_time * item.quantity
                subtotal += item_subtotal
                
                data.append([
                    product.name,
                    item.quantity,
                    f"${item.price_at_time:.2f}",
                    f"${item_subtotal:.2f}"
                ])
        
        print("\nOrder Items:")
        print(tabulate(data, headers=headers, tablefmt="pretty"))
        
        # Calculate tax and total
        tax = subtotal * TAX_RATE
        
        print(f"\nSubtotal: ${subtotal:.2f}")
        print(f"Tax ({TAX_RATE*100:.0f}%): ${tax:.2f}")
        print(f"Total: ${order.total_amount:.2f}")
        
        # Show status explanation
        status_explanations = {
            OrderStatus.PENDING: "Your order is being processed. Payment is being verified.",
            OrderStatus.PAID: "Payment received. The merchant is preparing your items.",
            OrderStatus.SHIPPED: "Your order has been shipped and is on its way to you.",
            OrderStatus.DELIVERED: "Your order has been delivered successfully.",
            OrderStatus.CANCELLED: "This order has been cancelled."
        }
        
        print(f"\nStatus Information: {status_explanations.get(order.status, '')}")
        
        return order
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    finally:
        session.close()


@merchant_required
def update_order_status(order_id, new_status):
    """
    Update the status of an order. Only for merchants who have products in the order.
    
    Args:
        order_id (int): ID of the order to update
        new_status (OrderStatus): New status for the order
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    current_user = get_current_user()
    if not current_user:
        return False, "User session not found. Please log in again."
        
    session = get_session()
    try:
        # First verify that the merchant has products in this order
        # Get merchant's business
        business = session.query(Business).filter(
            Business.owner_id == current_user.id
        ).first()
        
        if not business:
            return False, "You don't have a registered business."
            
        # Get the merchant's product IDs
        merchant_product_ids = [p.id for p in session.query(Product.id).filter(
            Product.business_id == business.id
        ).all()]
        
        if not merchant_product_ids:
            return False, "You don't have any products listed."
            
        # Check if the order contains any of the merchant's products
        order_contains_merchant_products = session.query(OrderItem).filter(
            OrderItem.order_id == order_id,
            OrderItem.product_id.in_(merchant_product_ids)
        ).first() is not None
        
        if not order_contains_merchant_products:
            return False, "You cannot update this order because it doesn't contain any of your products."
            
        # Now we can update the order status
        order = session.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return False, f"Order #{order_id} not found."
            
        # Update the status
        old_status = order.status
        order.status = new_status
        session.commit()
        
        return True, f"Order status updated from {old_status.value} to {new_status.value}"
        
    except Exception as e:
        session.rollback()
        return False, f"Error updating order status: {str(e)}"
    finally:
        session.close()


@merchant_required
def view_merchant_order_details(order_id, business_id):
    """
    View details of a specific order for a merchant.
    
    Args:
        order_id (int): ID of the order to view
        business_id (int): ID of the merchant's business
        
    Returns:
        tuple: (Order, List) - Order object and list of OrderItems for merchant's products
    """
    current_user = get_current_user()
    if not current_user:
        print("\nUser session not found. Please log in again.")
        return None, []
        
    session = get_session()
    try:
        # Get all products from the business
        product_ids = [p.id for p in session.query(Product.id).filter(
            Product.business_id == business_id
        ).all()]
        
        if not product_ids:
            print("\nYou don't have any products listed.")
            return None, []
            
        # Get the order
        order = session.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            print(f"\nOrder #{order_id} not found.")
            return None, []
            
        # Get order items for the merchant's products only
        order_items = session.query(OrderItem).filter(
            OrderItem.order_id == order_id,
            OrderItem.product_id.in_(product_ids)
        ).all()
        
        if not order_items:
            print(f"\nOrder #{order_id} doesn't contain any of your products.")
            return None, []
            
        # Get customer information
        customer = session.query(User).filter(User.id == order.user_id).first()
        
        print(f"\nOrder #{order_id} Details:")
        print(f"Customer: {customer.username}")
        print(f"Status: {order.status.value}")
        print(f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"Shipping Address: {order.shipping_address}")
        
        headers = ["Product", "Quantity", "Price", "Subtotal"]
        data = []
        total = 0
        
        for item in order_items:
            # Get product information
            product = session.query(Product).filter(
                Product.id == item.product_id
            ).first()
            
            if product:
                subtotal = item.price_at_time * item.quantity
                total += subtotal
                
                data.append([
                    product.name,
                    item.quantity,
                    f"${item.price_at_time:.2f}",
                    f"${subtotal:.2f}"
                ])
        
        print("\nYour Products in This Order:")
        print(tabulate(data, headers=headers, tablefmt="pretty"))
        print(f"\nYour Total: ${total:.2f} (out of ${order.total_amount:.2f})")
        
        return order, order_items
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, []
    finally:
        session.close()

@merchant_required
def view_merchant_orders(business_id):
    """
    View all orders for the merchant's products.
    
    Args:
        business_id (int): Business ID to view orders for
        
    Returns:
        list: List of Order objects
    """
    current_user = get_current_user()
    if not current_user:
        print("\nUser session not found. Please log in again.")
        return []
        
    session = get_session()
    try:
        # Verify business ownership
        business = session.query(Business).filter(
            Business.id == business_id,
            Business.owner_id == current_user.id
        ).first()
        
        if not business:
            print("\nBusiness not found or you don't have permission.")
            return []
            
        # Get all products from the business
        product_ids = [p.id for p in session.query(Product.id).filter(
            Product.business_id == business_id
        ).all()]
        
        if not product_ids:
            print("\nYou don't have any products listed.")
            return []
            
        # Find orders containing those products
        orders = session.query(Order).join(OrderItem).filter(
            OrderItem.product_id.in_(product_ids)
        ).distinct().all()
        
        if orders:
            headers = ["Order #", "Customer", "Date", "Status"]
            data = []
            
            for order in orders:
                # Get username
                username = session.query(User.username).filter(
                    User.id == order.user_id
                ).scalar()
                
                data.append([
                    order.id,
                    username,
                    order.created_at.strftime("%Y-%m-%d"),
                    order.status.value
                ])
            
            print("\nOrders for Your Products:")
            print(tabulate(data, headers=headers, tablefmt="pretty"))
        else:
            print("\nNo orders found for your products.")
            
        return orders
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []
    finally:
        session.close()