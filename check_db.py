import sqlite3
import os

db_path = r'c:\DATA\DATA HOSSAM THE\Файлы КФУ\My projects\National-Cuisine-Calculator\database.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    if ('cuisines',) in tables:
        cursor.execute("SELECT * FROM cuisines LIMIT 20;")
        rows = cursor.fetchall()
        print(f"Cuisines rows: {rows}")
        
    conn.close()
