# RegioCart (Regional E-commerce Platform)

## Project Overview
**RegioCart** is a comprehensive Python-based e-commerce solution that connects merchants and customers across regional markets. Built to focus on simplicity and efficiency, this platform enables businesses to register, list products, manage inventory, and track orders through a complete fulfillment cycle. Customers can browse products, search by category, manage their shopping carts, and track order status in a seamless shopping experience.

---

## Mission Statement
RegioCart bridges the gap between small businesses and regional markets by providing an accessible, secure, and efficient e-commerce solution. By leveraging Python and MySQL, we empower merchants to expand their reach while offering customers a diverse marketplace with reliable service and transparent order tracking.

---

## Features & Functionality

### 1. User Management
- **Dual Role System**: Separate interfaces for customers and merchants
- **Secure Authentication**: Password hashing and session management
- **Profile Management**: User information storage and retrieval

### 2. Merchant Features
- **Business Registration**: Complete business profile creation
- **Product Management**: Add, update, and toggle availability of products
- **Inventory Control**: Track stock quantities and manage availability
- **Order Processing**: View incoming orders and update order statuses
- **Sales Reports**: View product performance in the marketplace

### 3. Customer Features
- **Product Browsing**: View all available products in an organized display
- **Search Functionality**: Find products by name, description, or category
- **Shopping Cart**: Add, remove, and update quantities of selected items
- **Order History**: View past orders and their current status
- **Status Tracking**: Monitor order progress from payment to delivery

### 4. Order Management
- **Complete Lifecycle**: From cart to final delivery
- **Status Updates**: Five-stage order tracking (Pending, Paid, Shipped, Delivered, Cancelled)
- **Merchant Order Management**: Update status and communicate with customers
- **Order Details**: View comprehensive order information, including shipping details

### 5. Security & Data Integrity
- **Password Protection**: Secure credential storage with bcrypt hashing
- **Session Management**: Reliable user authentication across sessions
- **Transaction Security**: Safe payment processing and order confirmation
- **Data Validation**: Input checking to prevent errors and database corruption

---

## Technical Specifications

- **Programming Language**: Python 3.x
- **Database**: MySQL with SQLAlchemy ORM
- **Interface**: Terminal/Command-line interface
- **Dependencies**:
  - SQLAlchemy (Database ORM)
  - bcrypt (Password encryption)
  - PyMySQL (MySQL driver)
  - tabulate (Data presentation)
- **Architecture**: Multi-file modular design with clear separation of concerns
- **Data Models**: User, Business, Product, CartItem, Order, OrderItem

---

## Project Setup & Installation

### Prerequisites
- Python 3.6 or higher
- MySQL Server 5.7 or higher
- pip package manager

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/pdusenge/Group5_Job-creation-Regional-integration_PLP-2.git
   cd Group5_Job-creation-Regional-integration_PLP-2
   ```

2. **Set Up Virtual Environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pnpm install pymysql sqlalchemy bcrypt tabulate
   ```

4. **Configure Database**
   - Create a MySQL database named `regional_ecommerce`
   - Update database credentials in `config.py` if needed:
     ```python
     DB_USER = "root"
     DB_PASSWORD = "mysql"  # Change to your MySQL password
     DB_HOST = "localhost"
     DB_PORT = "3306"
     DB_NAME = "regional_ecommerce"
     ```

5. **Run the Application**
   ```bash
   python main.py
   ```

---

## Project Structure

```
RegioCart/
├── main.py              # Main entry point and UI handling
├── auth.py              # Authentication and user management
├── database.py          # Database models and connection
├── products.py          # Product management functions
├── orders.py            # Order processing and cart management
├── db_helpers.py        # Database utility functions
├── config.py            # Configuration settings
└── README.md            # Project documentation
```

---

## Usage Guide

### For Customers
1. Register a new account or log in
2. Browse products or search for specific items
3. Add desired products to your cart
4. View and update your cart as needed
5. Proceed to checkout and provide shipping information
6. Track your order status through the "View My Orders" option

### For Merchants
1. Register a merchant account
2. Create your business profile with details
3. Add products to your inventory with descriptions and prices
4. Manage your product listings (update details, toggle availability)
5. View and process incoming orders
6. Update order statuses as you fulfill them

---

## Future Enhancements
- Web-based interface
- Payment gateway integration
- Product reviews and ratings
- Multiple sellers per order support
- Advanced reporting and analytics
- Mobile application
- Multi-regional shipping and tax calculation

---

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contributors
- [@pdusenge](https://github.com/pdusenge)
- [@uwe](https://github.com/uwenayoallain)
- [@stevenalu](https://github.com/stevenalu)
- [@Ester446](https://github.com/Esther446)
- [@NMordecai](https://github.com/NMordecai)
- [@IgihozoColombe](https://github.com/IgihozoColombe)
---
