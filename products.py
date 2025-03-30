"""
Product and business management for the Regional E-commerce Platform.
"""
from tabulate import tabulate

from database import get_session, Product, Business
from auth import get_current_user, merchant_required

@merchant_required

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
