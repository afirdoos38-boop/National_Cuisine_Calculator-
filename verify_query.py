import sqlite3
import os

CUISINES_LIST = [
    'Русская кухня',
    'Украинская кухня',
    'Кавказская кухня',
    'Итальянская кухня',
    'Французская кухня',
    'Азиатская кухня',
    'Мексиканская кухня',
    'Индийская кухня',
    'Японская кухня',
    'Китайская кухня',
    'Тайская кухня',
    'Греческая кухня',
    'Испанская кухня',
    'Турецкая кухня',
    'Корейская кухня'
]

db_path = r'c:\DATA\DATA HOSSAM THE\Файлы КФУ\My projects\National-Cuisine-Calculator\database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

placeholders = ','.join(['?'] * len(CUISINES_LIST))
query = f'''
    SELECT
        TRIM(c.name) as cuisine_name,
        MAX(c.country) AS country,
        MAX(c.description) AS description,
        COUNT(r.id) AS recipe_count
    FROM cuisines c
    LEFT JOIN recipes r ON c.id = r.cuisine_id
    WHERE TRIM(c.name) IN ({placeholders})
    GROUP BY TRIM(c.name)
'''

print("Running query...")
cursor.execute(query, CUISINES_LIST)
rows = cursor.fetchall()

print(f"Found {len(rows)} cuisines.")
for row in rows:
    print(f"Name: {row[0]}, Country: {row[1]}, Recipes: {row[3]}")

conn.close()
if len(rows) == 15:
    print("\nSUCCESS: All 15 cuisines found!")
else:
    print(f"\nWARNING: Only {len(rows)} cuisines found out of 15.")
