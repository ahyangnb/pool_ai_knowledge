"""
Database initialization script
Creates tables and optionally creates a default admin user
"""

from database import init_db, SessionLocal, AdminUser, APIKey
from auth import get_password_hash
import sys

def create_default_admin():
    """Create default admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if admin:
            print("Default admin user already exists")
            return
        
        # Create default admin
        admin = AdminUser(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),  # Change this in production!
            is_super_admin=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("Default admin user created:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  WARNING: Change the default password in production!")
    except Exception as e:
        print(f"Error creating default admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    try:
        init_db()
        print("Database tables created successfully")
        
        # Create default admin
        create_default_admin()
        
        print("\nDatabase initialization complete!")
        print("\nNext steps:")
        print("1. Update the default admin password")
        print("2. Add API keys via admin panel: POST /api/admin/api-keys")
        print("3. Add posts via admin panel: POST /api/admin/posts")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

