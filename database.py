import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_connection():
    """Create a database connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database():
    """Create the database if it doesn't exist."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error creating database: {e}")

def create_tables():
    """Create the necessary tables if they don't exist."""
    create_database()
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    amount DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
        except Error as e:
            print(f"Error creating tables: {e}")

def add_transaction(amount, category, date, description=None):
    """Add a new transaction to the database."""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO transactions (amount, category, date, description)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (amount, category, date, description))
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error adding transaction: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

def get_monthly_expenses(year, month):
    """Get all transactions for a specific month and year."""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT * FROM transactions
                WHERE YEAR(date) = %s AND MONTH(date) = %s
                ORDER BY date DESC
            """
            cursor.execute(query, (year, month))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching monthly expenses: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

def get_expenses_by_category(year, month):
    """Get total expenses by category for a specific month and year."""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE YEAR(date) = %s AND MONTH(date) = %s
                GROUP BY category
            """
            cursor.execute(query, (year, month))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching expenses by category: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
