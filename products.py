"""
Product and business management for the Regional E-commerce Platform.
"""
from tabulate import tabulate

from database import get_session, Product, Business
from auth import get_current_user, merchant_required

def list_products():
    """
    List all active products.
    
    Returns:
        list: List of active Product objects
    """
    session = get_session()
    try:
        products = session.query(Product).filter(
            Product.is_active == True
        ).order_by(
            Product.category, Product.name
        ).all()
        
        if products:
            headers = ["ID", "Name", "Price", "Category", "Business"]
            data = []
            
            for p in products:
                # Get business name
                business_name = session.query(Business.name).filter(
                    Business.id == p.business_id
                ).scalar()
                
                data.append([
                    p.id, p.name, f"${p.price:.2f}", p.category, business_name
                ])
            
            print("\nAvailable Products:")
            print(tabulate(data, headers=headers, tablefmt="pretty"))
        else:
            print("\nNo products found.")
            
        return products
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []
    finally:
        session.close()

def search_products(query, category=None):
    """
    Search for products by name or description.
    
    Args:
        query (str): Search term
        category (str, optional): Filter by category. Defaults to None.
        
    Returns:
        list: List of matching Product objects
    """
    session = get_session()
    try:
        # Build the query
        search = f"%{query}%"
        db_query = session.query(Product).filter(
            Product.is_active == True,
            (Product.name.ilike(search) | Product.description.ilike(search))
        )
        
        # Add category filter if provided
        if category:
            db_query = db_query.filter(Product.category == category)
            
        # Execute query
        products = db_query.order_by(Product.name).all()
        
        if products:
            headers = ["ID", "Name", "Price", "Category", "Business"]
            data = []
            
            for p in products:
                # Get business name
                business_name = session.query(Business.name).filter(
                    Business.id == p.business_id
                ).scalar()
                
                data.append([
                    p.id, p.name, f"${p.price:.2f}", p.category, business_name
                ])
            
            print(f"\nSearch results for '{query}':")
            print(tabulate(data, headers=headers, tablefmt="pretty"))
        else:
            print(f"\nNo products found matching '{query}'.")
            
        return products
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []
    finally:
        session.close()

def get_product_details(product_id):
    """
    Get detailed information about a product.
    
    Args:
        product_id (int): ID of the product to view
        
    Returns:
        Product: Product object if found, None otherwise
    """
    session = get_session()
    try:
        product = session.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True
        ).first()
        
        if product:
            # Get business information
            business = session.query(Business).filter(
                Business.id == product.business_id
            ).first()
            
            print(f"\nProduct Details: {product.name}")
            print(f"Price: ${product.price:.2f}")
            print(f"Category: {product.category}")
            print(f"Business: {business.name}")
            print(f"Description: {product.description}")
            
            if product.stock_quantity > 0:
                print(f"In Stock: {product.stock_quantity} available")
            else:
                print("Out of Stock")
                
            # Create a copy to return
            product_copy = Product(
                id=product.id,
                business_id=product.business_id,
                name=product.name,
                description=product.description,
                price=product.price,
                stock_quantity=product.stock_quantity,
                category=product.category,
                is_active=product.is_active
            )
            
            return product_copy
        else:
            print("\nProduct not found.")
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    finally:
        session.close()

def get_categories():
    """
    Get a list of all product categories.
    
    Returns:
        list: List of category strings
    """
    session = get_session()
    try:
        categories = session.query(Product.category).distinct().all()
        return [c[0] for c in categories if c[0]]  # Filter out None values
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []
    finally:
        session.close()

@merchant_required
def list_merchant_products(business_id):
    """
    List all products for a merchant's business.
    
    Args:
        business_id (int): The business ID to list products for
        
    Returns:
        list: List of Product objects
    """
    current_user = get_current_user()
    if not current_user:
        print("User session not found. Please log in again.")
        return []
        
    session = get_session()
    try:
        # Verify business ownership
        business = session.query(Business).filter(
            Business.id == business_id,
            Business.owner_id == current_user.id
        ).first()
        
        if not business:
            print("Business not found or you don't have permission.")
            return []
            
        # Get products
        products = session.query(Product).filter(
            Product.business_id == business_id
        ).all()
        
        if products:
            headers = ["ID", "Name", "Price", "Stock", "Category", "Active"]
            data = [
                [p.id, p.name, f"${p.price:.2f}", p.stock_quantity, p.category, "Yes" if p.is_active else "No"]
                for p in products
            ]
            print("\nYour Products:")
            print(tabulate(data, headers=headers, tablefmt="pretty"))
        else:
            print("\nYou don't have any products listed yet.")
            
        return products
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []
    finally:
        session.close()



def add_product(business_id, name, description, price, stock_quantity, category):
    """
    Add a new product to the business.
    
    Args:
        business_id (int): Business ID
        name (str): Product name
        description (str): Product description
        price (float): Product price
        stock_quantity (int): Available stock quantity
        category (str): Product category
        
    Returns:
        tuple: (bool, Product|str) - Success status and Product object or error message
    """
    if not business_id:
        return False, "Missing business ID."
    
    current_user = get_current_user()
    if not current_user:
        return False, "User session not found. Please log in again."
        
    session = get_session()
    try:
        # Validate business ownership
        business = session.query(Business).filter(
            Business.id == business_id,
            Business.owner_id == current_user.id
        ).first()
        
        if not business:
            return False, "Business not found or you don't have permission."
            
        # Create product
        new_product = Product(
            business_id=business_id,
            name=name,
            description=description,
            price=float(price),
            stock_quantity=int(stock_quantity),
            category=category
        )
        
        session.add(new_product)
        session.commit()
        
        # Create a safe copy to return (without accessing attributes from the SQLAlchemy object)
        return True, f"Product '{name}' added successfully."
        
    except ValueError:
        session.rollback()
        return False, "Invalid price or stock quantity."
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()


@merchant_required
def update_product(product_id, name=None, description=None, price=None, 
                  stock_quantity=None, category=None, is_active=None):
    """
    Update product information.
    
    Args:
        product_id (int): ID of the product to update
        name (str, optional): New product name. Defaults to None.
        description (str, optional): New description. Defaults to None.
        price (float, optional): New price. Defaults to None.
        stock_quantity (int, optional): New stock quantity. Defaults to None.
        category (str, optional): New category. Defaults to None.
        is_active (bool, optional): Product availability. Defaults to None.
        
    Returns:
        tuple: (bool, Product|str) - Success status and Product object or error message
    """
    session = get_session()
    current_user = get_current_user()
    try:
        # Find the product and verify ownership
        product = session.query(Product).join(Business).filter(
            Product.id == product_id,
            Business.owner_id == current_user.id
        ).first()
        
        if not product:
            return False, "Product not found or doesn't belong to your business."
            
        # Update fields
        if name:
            product.name = name
        if description:
            product.description = description
        if price is not None:
            product.price = float(price)
        if stock_quantity is not None:
            product.stock_quantity = int(stock_quantity)
        if category:
            product.category = category
        if is_active is not None:
            product.is_active = bool(is_active)
            
        session.commit()
        
        # Create a copy to return
        product_copy = Product(
            id=product.id,
            business_id=product.business_id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category=product.category,
            is_active=product.is_active
        )
        
        return True, product_copy
        
    except ValueError:
        session.rollback()
        return False, "Invalid price or stock quantity."
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()
