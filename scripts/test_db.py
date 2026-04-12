import sqlite3
import os

db_path = 'database.db'

print(f"1. جاري محاولة الاتصال بـ SQLite (ملف: {db_path})...")
try:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    print("✅ تم الاتصال أو إنشاء الملف بنجاح.")

    # لنرى الجداول الموجودة
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if tables:
        print("✅ قاعدة البيانات تحتوي على الجداول التالية:")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("⚠️ قاعدة البيانات فارغة. قم بتشغيل main.py ليتم بناء الجداول تلقائياً.")

    cursor.close()
    conn.close()

except sqlite3.Error as e:
    print("❌ حدث خطأ في التعامل مع SQLite:")
    print(e)
