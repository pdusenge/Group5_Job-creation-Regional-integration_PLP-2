"""
Database connection and models for the Regional E-commerce Platform.
"""
import enum
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

from config import DB_URL, ECHO_SQL

# Create the SQLAlchemy engine
engine = create_engine(DB_URL, echo=ECHO_SQL)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Base class for all models
Base = declarative_base()
def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(engine)
    print("Database initialized successfully.")

def get_session():
    """Get a new database session."""
    return Session()

def close_session():
    """Close the current session."""
    Session.remove()
# Enums
class UserRole(enum.Enum):
    CUSTOMER = "customer"
    MERCHANT = "merchant"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Models
class User(Base):
    """User model for authentication and user information."""
    _tablename_ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="owner", uselist=False)
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

class Business(Base):
    """Business model for merchants."""
    _tablename_ = "businesses"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    contact_email = Column(String(100))
    
    # Relationships
    owner = relationship("User", back_populates="business")
    products = relationship("Product", back_populates="business", cascade="all, delete-orphan")


