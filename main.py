"""
Regional E-commerce Platform

Main entry point for the application.
"""
import os
import sys
from datetime import datetime

from config import APP_NAME, APP_VERSION
from database import get_session, init_db, UserRole, Business, OrderStatus
import auth
import products
import orders
import helper

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    """Pause execution until user presses Enter."""
    input("\nPress Enter to continue...")


def get_input(prompt, required=False, input_type=str):
    """
    Get validated input from the user.
    
    Args:
        prompt (str): Prompt message to display
        required (bool, optional): Whether input is required. Defaults to False.
        input_type (type, optional): Type to convert input to. Defaults to str.
        
    Returns:
        Any: The validated input converted to input_type, or None if not required and empty
    """
    while True:
        value = input(prompt)
        
        if not value:
            if required:
                print("This field is required.")
                continue
            return None
            
        try:
            return input_type(value)
        except ValueError:
            print(f"Invalid input. Expected {input_type._name_}.")


def get_int(prompt, required=False, min_value=None, max_value=None):
    """
    Get an integer input from the user.
    
    Args:
        prompt (str): Prompt message to display
        required (bool, optional): Whether input is required. Defaults to False.
        min_value (int, optional): Minimum allowed value. Defaults to None.
        max_value (int, optional): Maximum allowed value. Defaults to None.
        
    Returns:
        int: The validated integer input, or None if not required and empty
    """
    while True:
        value = input(prompt)
        
        if not value:
            if required:
                print("This field is required.")
                continue
            return None
            
        try:
            int_value = int(value)
            
            if min_value is not None and int_value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
                
            if max_value is not None and int_value > max_value:
                print(f"Value must be at most {max_value}.")
                continue
                
            return int_value
            
        except ValueError:
            print("Invalid input. Expected an integer.")


def get_float(prompt, required=False, min_value=None, max_value=None):
    """
    Get a float input from the user.
    
    Args:
        prompt (str): Prompt message to display
        required (bool, optional): Whether input is required. Defaults to False.
        min_value (float, optional): Minimum allowed value. Defaults to None.
        max_value (float, optional): Maximum allowed value. Defaults to None.
        
    Returns:
        float: The validated float input, or None if not required and empty
    """
    while True:
        value = input(prompt)
        
        if not value:
            if required:
                print("This field is required.")
                continue
            return None
            
        try:
            float_value = float(value)
            
            if min_value is not None and float_value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
                
            if max_value is not None and float_value > max_value:
                print(f"Value must be at most {max_value}.")
                continue
                
            return float_value
            
        except ValueError:
            print("Invalid input. Expected a number.")


def show_menu(title, options):
    """
    Display a menu with options and get user choice.
    
    Args:
        title (str): Menu title
        options (list): List of option strings
        
    Returns:
        int: Selected option index (0-based) or -1 to exit
    """
    print(f"\n--- {title} ---")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Back/Exit")
    
    max_option = len(options)
    choice = get_int("\nEnter your choice (0-{0}): ".format(max_option), required=True, min_value=0, max_value=max_option)
    return choice - 1 if choice > 0 else -1


def setup_database():
    """Set up the database and create necessary tables."""
    try:
        # Check if MySQL server is running
        from database import engine
        conn = engine.connect()
        conn.close()
        
        # Initialize database
        init_db()
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"Database setup failed: {str(e)}")
        print("\nMake sure MySQL is running and the database credentials in config.py are correct.")
        sys.exit(1)


def register_user_menu():
    """Register a new user."""
    clear_screen()
    print("\n=== Register New User ===")
    
    username = get_input("Username: ", required=True)
    email = get_input("Email: ", required=True)
    password = get_input("Password: ", required=True)
    confirm_password = get_input("Confirm Password: ", required=True)
    
    if password != confirm_password:
        print("\nPasswords do not match.")
        pause()
        return
        
    is_merchant = get_input("Register as a merchant? (yes/no): ").lower() == "yes"
    role = UserRole.MERCHANT if is_merchant else UserRole.CUSTOMER
    
    success, result = auth.register_user(username, email, password, role)
    
    if success:
        print("\nRegistration successful!")
        # User is already set in auth.register_user
        
        if is_merchant:
            print("\nAs a merchant, you should register your business.")
            register_business_menu()
    else:
        print(f"\nRegistration failed: {result}")
        
    pause()


def login_menu():
    """Log in a user."""
    clear_screen()
    print("\n=== Login ===")
    
    username_or_email = get_input("Username or Email: ", required=True)
    password = get_input("Password: ", required=True)
    
    success, result = auth.login(username_or_email, password)
    
    if success:
        # User is already set in auth.login
        print(f"\nWelcome back, {result.username}!")
    else:
        print(f"\nLogin failed: {result}")
        
    pause()


def logout():
    """Log out the current user."""
    auth.clear_current_user()
    print("\nYou have been logged out.")
    pause()


def browse_products_menu():
    """Browse products."""
    clear_screen()
    print("\n=== Browse Products ===")
    
    product_list = products.list_products()
    
    if not product_list:
        pause()
        return
        
    while True:
        options = ["View Product Details", "Add to Cart"]
        choice = show_menu("Options", options)
        
        if choice == -1:  # Back/Exit
            return  # Return to previous menu
            
        if choice == 0:  # View Product Details
            product_id = get_int("\nEnter Product ID: ", required=True, min_value=1)
            product = products.get_product_details(product_id)
            
            if product and auth.get_current_user():
                add_to_cart = get_input("\nAdd to cart? (yes/no): ").lower() == "yes"
                if add_to_cart:
                    quantity = get_int("Quantity: ", required=True, min_value=1)
                    success, result = orders.add_to_cart(product_id, quantity)
                    
                    if success:
                        print(f"\n{result}")
                    else:
                        print(f"\nFailed to add product: {result}")
            
            pause()
            
        elif choice == 1:  # Add to Cart
            if not auth.get_current_user():
                print("\nYou must be logged in to add items to your cart.")
                pause()
                continue
                
            product_id = get_int("\nEnter Product ID: ", required=True, min_value=1)
            quantity = get_int("Quantity: ", required=True, min_value=1)
            
            success, result = orders.add_to_cart(product_id, quantity)
            
            if success:
                print(f"\n{result}")
            else:
                print(f"\nFailed to add product: {result}")
                
            pause()


def search_products_menu():
    """Search for products."""
    clear_screen()
    print("\n=== Search Products ===")
    
    query = get_input("Enter search term: ", required=True)
    
    # Get available categories for filtering
    categories = products.get_categories()
    if categories:
        print("\nCategories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
            
        choice = get_int("\nFilter by category? (0 for none): ", min_value=0, max_value=len(categories))
        selected_category = categories[choice-1] if choice > 0 else None
    else:
        selected_category = None
        
    # Perform search
    product_list = products.search_products(query, selected_category)
    
    if not product_list:
        pause()
        return
        
    while True:
        options = ["View Product Details", "Add to Cart"]
        choice = show_menu("Options", options)
        
        if choice == -1:  # Back/Exit
            return  # Return to previous menu
            
        if choice == 0:  # View Product Details
            product_id = get_int("\nEnter Product ID: ", required=True, min_value=1)
            product = products.get_product_details(product_id)
            
            if product and auth.get_current_user():
                add_to_cart = get_input("\nAdd to cart? (yes/no): ").lower() == "yes"
                if add_to_cart:
                    quantity = get_int("Quantity: ", required=True, min_value=1)
                    success, result = orders.add_to_cart(product_id, quantity)
                    
                    if success:
                        print(f"\n{result}")
                    else:
                        print(f"\nFailed to add product: {result}")
            
            pause()
            
        elif choice == 1:  # Add to Cart
            if not auth.get_current_user():
                print("\nYou must be logged in to add items to your cart.")
                pause()
                continue
                
            product_id = get_int("\nEnter Product ID: ", required=True, min_value=1)
            quantity = get_int("Quantity: ", required=True, min_value=1)
            
            success, result = orders.add_to_cart(product_id, quantity)
            
            if success:
                print(f"\n{result}")
            else:
                print(f"\nFailed to add product: {result}")
                
            pause()


@auth.login_required
def cart_menu():
    """View and manage the shopping cart."""
    while True:
        clear_screen()
        print("\n=== Shopping Cart ===")
        
        cart_items, total = orders.view_cart()
        
        if not cart_items:
            pause()
            return
            
        options = ["Update Quantity", "Remove Item", "Clear Cart", "Checkout"]
        choice = show_menu("Options", options)
        
        if choice == -1:  # Back/Exit
            return  # Return to previous menu
            
        if choice == 0:  # Update Quantity
            cart_item_id = get_int("\nEnter Cart Item ID: ", required=True, min_value=1)
            quantity = get_int("New Quantity: ", required=True, min_value=0)
            
            success, result = orders.update_cart_item(cart_item_id, quantity)
            
            if success:
                print("\nCart updated successfully.")
            else:
                print(f"\nFailed to update cart: {result}")
                
            pause()
            
        elif choice == 1:  # Remove Item
            cart_item_id = get_int("\nEnter Cart Item ID: ", required=True, min_value=1)
            
            success, result = orders.remove_from_cart(cart_item_id)
            
            if success:
                print("\nItem removed from cart.")
            else:
                print(f"\nFailed to remove item: {result}")
                
            pause()
            
        elif choice == 2:  # Clear Cart
            confirm = get_input("\nAre you sure you want to clear your cart? (yes/no): ").lower() == "yes"
            
            if confirm:
                success, result = orders.clear_cart()
                
                if success:
                    print("\nCart cleared successfully.")
                else:
                    print(f"\nFailed to clear cart: {result}")
                    
                pause()
                return  # Return to main menu after clearing cart
                
        elif choice == 3:  # Checkout
            shipping_address = get_input("Enter shipping address: ", required=True)
            
            if shipping_address:
                success, result = orders.checkout(shipping_address)
                
                if success:
                    print("\nCheckout successful!")
                else:
                    print(f"\nCheckout failed: {result}")
                
                pause()
                return  # Return to main menu after checkout


@auth.login_required
def orders_menu():
    """View and manage orders."""
    clear_screen()
    print("\n=== My Orders ===")
    
    order_list = orders.list_orders()
    
    if not order_list:
        pause()
        return  # Return to main menu if no orders
        
    while True:
        order_id = get_int("\nEnter Order ID to view details (or 0 to go back): ", min_value=0)
        
        if order_id == 0:
            return  # Return to main menu when user chooses to go back
            
        order = orders.view_order_details(order_id)
        
        if not order:
            print("\nOrder not found. Press Enter to continue...")
            pause()
        else:
            pause()  # Pause after displaying order details


@auth.merchant_required
def register_business_menu():
    """Register a new business for a merchant."""
    clear_screen()
    print("\n=== Register Business ===")
    
    # Check if the user already has a business
    current_user = auth.get_current_user()
    if auth.has_business(current_user.id):
        print("\nYou already have a registered business.")
        pause()
        return
    
    name = get_input("Business Name: ", required=True)
    description = get_input("Description: ", required=True)
    contact_email = get_input("Contact Email: ")
    
    success, result = auth.register_business(name, description, contact_email)
    
    if success:
        print("\nBusiness registered successfully!")
    else:
        print(f"\nFailed to register business: {result}")
        
    pause()


@auth.merchant_required
def add_product_menu(business_id):
    """
    Add a new product.
    
    Args:
        business_id (int): The business ID to add the product to
    """
    if not business_id:
        print("\nError: No business ID provided.")
        pause()
        return
        
    clear_screen()
    print("\n=== Add New Product ===")
    print(f"Adding product for business ID: {business_id}")
    
    name = get_input("Product Name: ", required=True)
    description = get_input("Description: ", required=True)
    price = get_float("Price: ", required=True, min_value=0.01)
    stock_quantity = get_int("Stock Quantity: ", required=True, min_value=0)
    category = get_input("Category: ", required=True)
    
    success, result = products.add_product(business_id, name, description, price, stock_quantity, category)
    
    if success:
        print(f"\n{result}")
    else:
        print(f"\nFailed to add product: {result}")
        
    pause()


@auth.merchant_required
def update_product_menu(business_id):
    """
    Update an existing product.
    
    Args:
        business_id (int): The business ID to update products for
    """
    product_id = get_int("\nEnter Product ID to update: ", required=True, min_value=1)
    
    # Get current product details
    session = get_session()
    try:
        from database import Product
        product = session.query(Product).join(Business).filter(
            Product.id == product_id,
            Business.id == business_id,
            Business.owner_id == auth.get_current_user().id
        ).first()
        
        if not product:
            print("\nProduct not found or doesn't belong to your business.")
            pause()
            return
            
        clear_screen()
        print(f"\n=== Update Product: {product.name} ===")
        
        name = get_input(f"Name [{product.name}]: ")
        description = get_input(f"Description [{product.description}]: ")
        price = get_float(f"Price [{product.price}]: ", min_value=0.01)
        stock_quantity = get_int(f"Stock Quantity [{product.stock_quantity}]: ", min_value=0)
        category = get_input(f"Category [{product.category}]: ")
        
        success, result = products.update_product(
            product_id, name, description, price, stock_quantity, category
        )
        
        if success:
            print("\nProduct updated successfully!")
        else:
            print(f"\nFailed to update product: {result}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        session.close()
        pause()


@auth.merchant_required
def toggle_product_menu(business_id):
    """
    Toggle a product's availability.
    
    Args:
        business_id (int): The business ID to toggle products for
    """
    product_id = get_int("\nEnter Product ID to toggle availability: ", required=True, min_value=1)
    
    # Get current product details
    session = get_session()
    try:
        from database import Product
        product = session.query(Product).join(Business).filter(
            Product.id == product_id,
            Business.id == business_id,
            Business.owner_id == auth.get_current_user().id
        ).first()
        
        if not product:
            print("\nProduct not found or doesn't belong to your business.")
            pause()
            return
            
        # Toggle availability
        new_status = not product.is_active
        success, result = products.update_product(
            product_id, is_active=new_status
        )
        
        if success:
            status_str = "available" if new_status else "unavailable"
            print(f"\nProduct is now {status_str}.")
        else:
            print(f"\nFailed to update product: {result}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        session.close()
        pause()


@auth.merchant_required
def manage_products_menu(business_id=None):
    """
    Menu for managing products.
    
    Args:
        business_id (int, optional): The business ID to manage products for.
                                    If None, will check current_user.business.
    """
    while True:
        clear_screen()
        print("\n=== Manage Products ===")
        
        # Get business ID if not provided
        if business_id is None:
            business = auth.get_business(auth.get_current_user().id)
            if not business:
                print("\nYou must register a business first.")
                pause()
                return
            business_id = business.id
            
        # List products for this business
        products.list_merchant_products(business_id)
        
        options = ["Add New Product", "Update Product", "Toggle Product Availability"]
        choice = show_menu("Options", options)
        
        if choice == -1:  # Back/Exit
            return  # Return to merchant dashboard
            
        if choice == 0:  # Add New Product
            add_product_menu(business_id)
        elif choice == 1:  # Update Product
            update_product_menu(business_id)
        elif choice == 2:  # Toggle Product Availability
            toggle_product_menu(business_id)


@auth.merchant_required
def merchant_menu():
    """Merchant dashboard menu."""
    while True:
        clear_screen()
        print("\n=== Merchant Dashboard ===")
        
        # Check for business
        business = auth.get_business(auth.get_current_user().id)
        
        if not business:
            print("\nYou don't have a registered business yet.")
            options = ["Register Business"]
        else:
            print(f"\nBusiness: {business.name}")
            options = ["Manage Products", "Manage Orders"]
            
        choice = show_menu("Options", options)
        
        if choice == -1:  # Back/Exit
            return  # Return to main menu
            
        if not business and choice == 0:  # Register Business
            register_business_menu()
        elif business:
            if choice == 0:  # Manage Products
                manage_products_menu(business.id)
            elif choice == 1:  # Manage Orders
                view_merchant_orders_menu(business.id)


@auth.merchant_required
def view_merchant_orders_menu(business_id):
    """
    View and manage orders for a merchant's products.
    
    Args:
        business_id (int): The business ID to view orders for
    """
    clear_screen()
    print("\n=== Merchant Orders ===")
    
    # Display all orders that contain merchant's products
    merchant_orders = orders.view_merchant_orders(business_id)
    
    if not merchant_orders:
        pause()
        return
        
    while True:
        order_id = get_int("\nEnter Order ID to view details and manage (or 0 to go back): ", min_value=0)
        
        if order_id == 0:
            return  # Return to merchant dashboard
            
        # View specific order details and manage order
        order, order_items = orders.view_merchant_order_details(order_id, business_id)
        
        if order and order_items:
            # Display options to update order status
            print(f"\nCurrent Status: {order.status.value}")
            print("\nUpdate Order Status:")
            
            # Show all possible statuses
            status_options = [status.value for status in OrderStatus]
            for i, status in enumerate(status_options, 1):
                print(f"{i}. {status}")
                
            # Get new status choice
            choice = get_int("\nSelect new status (0 to cancel): ", min_value=0, max_value=len(status_options))
            
            if choice == 0:
                pass  # Do nothing, continue loop
            else:
                # Update order status
                new_status = OrderStatus(status_options[choice - 1])
                success, message = orders.update_order_status(order_id, new_status)
                
                if success:
                    print(f"\n✓ {message}")
                else:
                    print(f"\n✗ {message}")
                    
        pause()
    return


def main_menu():
    """Display the main menu."""
    while True:
        clear_screen()
        print(f"\n=== {APP_NAME} v{APP_VERSION} ===")
        print(f"Current Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Get current user
        current_user = auth.get_current_user()
        
        if current_user:
            # Get user information
            user, business, is_merchant = helper.get_user_info(current_user.id)
            
            if user:
                print(f"Logged in as: {user.username} ({user.role.value})")
                
                if is_merchant:
                    if business:
                        print(f"Business: {business.name}")
                    else:
                        print("You don't have a registered business yet.")
                        
                options = [
                    "Browse Products",
                    "Search Products",
                    "View Cart",
                    "View My Orders"
                ]
                
                if is_merchant:
                    options.append("Merchant Dashboard")
                    
                options.append("Log Out")
            else:
                # User not found - session may have expired
                print("Session error. Please log in again.")
                auth.clear_current_user()
                pause()
                continue
                
        else:
            options = [
                "Browse Products",
                "Search Products",
                "Register",
                "Login"
            ]
        
        choice = show_menu("Main Menu", options)
        
        if choice == -1:  # Exit application
            print("\nThank you for using the Regional E-commerce Platform !")
            break
            
        if current_user:
            if choice == 0:  # Browse Products
                browse_products_menu()
            elif choice == 1:  # Search Products
                search_products_menu()
            elif choice == 2:  # View Cart
                cart_menu()
            elif choice == 3:  # View My Orders
                orders_menu()
            elif is_merchant and choice == 4:  # Merchant Dashboard
                merchant_menu()
            elif choice == len(options) - 1:  # Log Out
                logout()
        else:
            if choice == 0:  # Browse Products
                browse_products_menu()
            elif choice == 1:  # Search Products
                search_products_menu()
            elif choice == 2:  # Register
                register_user_menu()
            elif choice == 3:  # Login
                login_menu()


if _name_ == "_main_":
    try:
        setup_database()
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting application...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
    finally:
        from database import close_session
        close_session()
