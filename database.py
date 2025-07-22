import sqlite3

# This is the name of our database file.
# It will be created in the main project folder.
DATABASE_NAME = "finance.db"

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    # This allows us to access columns by name (like a dictionary).
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the database tables if they don't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # We use """ to write multi-line SQL statements for readability.
    
    # --- Create users table for PIN security ---
    # pin_hash will store a securely hashed version of the PIN, not the PIN itself.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        pin_hash TEXT NOT NULL
    )
    """)

    # --- Create categories table ---
    # Users will create their own categories here. budget is the monthly limit.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        budget REAL DEFAULT 0,
        is_recurring INTEGER NOT NULL DEFAULT 0 -- Add this line back
    )
    """)

    # --- Create transactions table ---
    # This is the heart of our app, storing every financial event.
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_date TEXT NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
        need_want TEXT CHECK(need_want IN ('need', 'want')),
        category_id INTEGER,
        payment_method TEXT, -- Add this new column
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL NOT NULL DEFAULT 0,
        image_filename TEXT,
        need_want TEXT,
        is_completed INTEGER DEFAULT 0,
        priority INTEGER DEFAULT 1,          -- Add this line
        show_on_dashboard INTEGER DEFAULT 0  -- Add this line (0=no, 1=yes)
    )
    """)

    print("Database tables created successfully.")
    conn.commit()
    conn.close()