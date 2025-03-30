# Database settings
DB_USER = "root"
DB_PASSWORD = "mysql"  # Change to your MySQL password
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "regional_ecommerce"

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
ECHO_SQL = False  # Set to True for SQL debugging

# Security settings
PASSWORD_SALT_ROUNDS = 12  # For bcrypt password hashing

# Application settings
APP_NAME = "Regional E-commerce Platform"
APP_VERSION = "1.1.0"
TAX_RATE = 0.08