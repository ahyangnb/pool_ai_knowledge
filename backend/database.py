"""
Database configuration and models
"""

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/pool_ai_knowledge?charset=utf8mb4"
)

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# ==================== Database Models ====================

class Post(Base):
    """Post/Article model"""
    __tablename__ = "posts"
    
    id = Column(String(255), primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(Text)  # JSON string or comma-separated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class APIKey(Base):
    """API Key configuration model"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key_type = Column(String(50), nullable=False)  # 'openai' or 'google'
    key_name = Column(String(100), nullable=False)  # Display name
    key_value = Column(Text, nullable=False)  # Encrypted or plain (should be encrypted in production)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))  # Admin user who created it
    description = Column(Text)  # Optional description


class AdminUser(Base):
    """Admin user model"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Should be hashed
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemConfig(Base):
    """System configuration model"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== Database Utilities ====================

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _run_sql_file(file_name: str):
    """Execute a SQL file against the database"""
    import re
    sql_path = os.path.join(os.path.dirname(__file__), "sql", file_name)
    if not os.path.exists(sql_path):
        print(f"Warning: SQL file not found: {sql_path}")
        return
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()
    # Strip comments (-- line comments and /* */ block comments)
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    from sqlalchemy import text
    with engine.connect() as conn:
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()


def init_db():
    """Initialize database: run schema.sql then seed.sql"""
    _run_sql_file("schema.sql")
    print("Database tables created successfully")
    _run_sql_file("seed.sql")
    print("Seed data initialized successfully")

