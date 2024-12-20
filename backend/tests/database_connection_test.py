# test_db_connection.py

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from app.core.config import settings
from sqlalchemy import create_engine, text

def test_connection():
    # Create an engine instance using the database URL
    engine = create_engine(settings.get_database_url)

    # Connect to the database
    with engine.connect() as connection:
        # Use the text() function to make "SELECT 1" executable
        result = connection.execute(text("SELECT 1"))  # Test query

        # Print the result to verify the connection
        for row in result:
            print("Connection successful, query result:", row)


if __name__ == "__main__":
    test_connection()
