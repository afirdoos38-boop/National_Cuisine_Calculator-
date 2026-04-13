import sqlite3
import os

db_path = r'c:\DATA\DATA HOSSAM THE\Файлы КФУ\My projects\National-Cuisine-Calculator\database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM cuisines;")
rows = cursor.fetchall()
for row in rows:
    name = row[0]
    print(f"Name: {name!r}, Length: {len(name)}, Hex: {name.encode('utf-8').hex()}")

print("\nExpected 'Русская кухня':")
expected = 'Русская кухня'
print(f"Name: {expected!r}, Length: {len(expected)}, Hex: {expected.encode('utf-8').hex()}")
conn.close()
