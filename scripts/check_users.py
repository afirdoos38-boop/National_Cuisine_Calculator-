import sqlite3

def check_users():
    db_path = 'database.db'
    print(f"--- فحص المستخدمين في {db_path} ---")
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # جلب قائمة المستخدمين
        cursor.execute("SELECT id, username, full_name, role, created_at FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("⚠️ لا يوجد مستخدمين مسجلين بعد.")
        else:
            print(f"✅ تم العثور على ({len(users)}) مستخدمين:")
            print("-" * 50)
            for user in users:
                print(f"ID: {user[0]} | اسم المستخدم: {user[1]} | الاسم الكامل: {user[2]} | الرتبة: {user[3]}")
            print("-" * 50)
            
        cursor.close()
        conn.close()
    except sqlite3.Error as e:
        print(f"❌ حدث خطأ في قاعدة البيانات: {e}")

if __name__ == "__main__":
    check_users()
