"""
Database Initialization Script

This script initializes the database by creating all tables defined in the SQLAlchemy models.
Run this script to set up the database schema before starting the application.

Usage:
    python init_db.py
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import Base, DB_INSTANCE

# Import all models to ensure they are registered with SQLAlchemy
# This must be done before calling create_all()
# pylint: disable=unused-import
from app.models.card import Card, Deck, deck_cards


def create_tables():
    """Create all database tables defined in the models."""
    print("Starting database initialization...")
    print(f"Database URL: {settings.get_database_url}")

    try:
        # Create all tables
        Base.metadata.create_all(bind=DB_INSTANCE.engine)
        print("\nDatabase tables created successfully!")

        # List all created tables
        print("\nCreated tables:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")

    except Exception as e:
        print(f"\nError creating database tables: {e}")
        sys.exit(1)


def drop_tables():
    """Drop all database tables. Use with caution!"""
    print("WARNING: This will drop all existing tables!")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() == 'yes':
        try:
            Base.metadata.drop_all(bind=DB_INSTANCE.engine)
            print("\nAll tables dropped successfully!")
        except Exception as e:
            print(f"\nError dropping tables: {e}")
            sys.exit(1)
    else:
        print("Operation cancelled.")


def reset_database():
    """Drop all tables and recreate them. Use with caution!"""
    print("WARNING: This will drop all existing tables and recreate them!")
    print("All data will be lost!")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() == 'yes':
        try:
            print("\nDropping existing tables...")
            Base.metadata.drop_all(bind=DB_INSTANCE.engine)
            print("Tables dropped successfully!")

            print("\nCreating new tables...")
            Base.metadata.create_all(bind=DB_INSTANCE.engine)
            print("Tables created successfully!")

            print("\nDatabase reset complete!")
        except Exception as e:
            print(f"\nError resetting database: {e}")
            sys.exit(1)
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "create":
            create_tables()
        elif command == "drop":
            drop_tables()
        elif command == "reset":
            reset_database()
        else:
            print("Unknown command. Available commands: create, drop, reset")
            print("\nUsage:")
            print("  python init_db.py create  - Create all tables")
            print("  python init_db.py drop    - Drop all tables")
            print("  python init_db.py reset   - Drop and recreate all tables")
    else:
        # Default action is to create tables
        create_tables()
