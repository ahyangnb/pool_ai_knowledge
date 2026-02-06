"""
Database initialization script
Creates tables and default admin user.

Usage:
    python init_db.py          - Initialize database
    python init_db.py --reset  - Drop and recreate all tables (WARNING: destroys data)
"""

from database import init_db
import sys


if __name__ == "__main__":
    print("Initializing database...")
    try:
        init_db()
        print("\nDatabase initialization complete!")
        print("\nDefault admin account:")
        print("  Username: admin")
        print("  Password: admin123456")
        print("  WARNING: Change the default password in production!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

