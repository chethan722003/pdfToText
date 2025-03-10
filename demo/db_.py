import psycopg2

# Database connection parameters
DB_URL = "postgresql://postgres:Jeevan@localhost:5433/flask_database"

try:
    # Establish connection
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    # Example: Creating a new table
    create_table_query = '''
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    
    cursor.execute(create_table_query)
    conn.commit()
    
    print("Table created successfully")

except Exception as e:
    print("Error:", e)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
