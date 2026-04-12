"""
database/database.py
Менеджер базы данных SQLite. Обрабатывает подключение, создание таблиц,
инициализацию демо-данных (сиды), а также операции архивации удаленных записей.
"""
import sqlite3
from sqlite3 import Error
import hashlib


class DatabaseManager:
    def __init__(self, app=None):
        self.app = app
        self.connection = None

    def connect_to_database(self):
        """Подключение к базе данных SQLite"""
        try:
            connection = sqlite3.connect('database.db')
            # SQLite по умолчанию не проверяет FOREIGN KEY, пока не включить:
            connection.execute("PRAGMA foreign_keys = ON")
            self.connection = connection
            return connection
        except Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return None

    def init_database(self):
        """Инициализация структуры базы данных"""
        try:
            cursor = self.connection.cursor()



            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    role TEXT DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cuisines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    country VARCHAR(100),
                    description TEXT,
                    image_url VARCHAR(255)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    ingredients TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    preparation_time INT,
                    cooking_time INT,
                    total_time INT,
                    base_portions INT DEFAULT 4,
                    difficulty TEXT DEFAULT 'средне',
                    cuisine_id INT,
                    calories INT,
                    proteins DECIMAL(5,2),
                    fats DECIMAL(5,2),
                    carbs DECIMAL(5,2),
                    tags TEXT,
                    image_path VARCHAR(255),
                    created_by INT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cuisine_id) REFERENCES cuisines(id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

            # قواعد قديمة: الجدول موجود بدون عمود مسار الصورة
            cursor.execute("PRAGMA table_info(recipes)")
            _recipe_cols = [row[1] for row in cursor.fetchall()]
            if _recipe_cols and 'image_path' not in _recipe_cols:
                cursor.execute(
                    "ALTER TABLE recipes ADD COLUMN image_path VARCHAR(255)"
                )

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ingredient_calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id INT,
                    ingredient_name VARCHAR(255),
                    quantity DECIMAL(10,2),
                    unit VARCHAR(50),
                    price_per_unit DECIMAL(10,2),
                    total_price DECIMAL(10,2),
                    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
                )
            ''')

            # --- الحذف الآمن (الأرشيف) ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS archived_recipes (
                    id INTEGER PRIMARY KEY,
                    original_id INTEGER,
                    name TEXT,
                    data TEXT,
                    archived_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS archived_users (
                    id INTEGER PRIMARY KEY,
                    original_id INTEGER,
                    username TEXT,
                    data TEXT,
                    archived_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')


            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    price_per_unit DECIMAL(10,2) NOT NULL,
                    unit VARCHAR(20) NOT NULL DEFAULT 'кг',
                    category VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')


            test_users = [
                ('admin', self.hash_password('123'), 'Администратор Системы', 'admin'),
                ('chef', self.hash_password('111'), 'Шеф-повар Петров', 'chef'),
                ('user', self.hash_password('000'), 'Обычный Пользователь', 'user')
            ]

            for user in test_users:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                        user
                    )
                except Error as e:
                    print(f"Ошибка добавления пользователя {user[0]}: {e}")

            # ✅ إضافة المطابخ إذا لم تكن موجودة
            cuisines = [
                ('Русская кухня', 'Россия', 'Традиционная кухня народов России', None),
                ('Украинская кухня', 'Украина', 'Богатая и разнообразная кухня Украины', None),
                ('Кавказская кухня', 'Кавказ', 'Кухня народов Кавказа', None),
                ('Итальянская кухня', 'Италия', 'Знаменитая средиземноморская кухня', None),
                ('Французская кухня', 'Франция', 'Изысканная европейская кухня', None),
                ('Азиатская кухня', 'Азия', 'Кухни стран Восточной Азии', None),
                ('Мексиканская кухня', 'Мексика', 'Острая и яркая кухня Мексики', None),
                ('Индийская кухня', 'Индия', 'Ароматная кухня с пряностями', None),
                ('Японская кухня', 'Япония', 'Традиционная японская кухня', None),
                ('Китайская кухня', 'Китай', 'Разнообразная китайская кухня', None),
                ('Тайская кухня', 'Таиланд', 'Острая и ароматная тайская кухня', None),
                ('Греческая кухня', 'Греция', 'Средиземноморская кухня Греции', None),
                ('Испанская кухня', 'Испания', 'Яркая испанская кухня', None),
                ('Турецкая кухня', 'Турция', 'Богатая турецкая кухня', None),
                ('Корейская кухня', 'Корея', 'Острая корейская кухня', None)
            ]

            for cuisine in cuisines:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO cuisines (name, country, description, image_url) VALUES (?, ?, ?, ?)",
                        cuisine
                    )
                except Error as e:
                    print(f"Ошибка добавления кухни {cuisine[0]}: {e}")

            # ✅ إضافة المكونات الأساسية إذا لم تكن موجودة
            base_ingredients = [
                ('говядина', 450.00, 'кг', 'мясо'),
                ('свинина', 380.00, 'кг', 'мясо'),
                ('курица', 280.00, 'кг', 'мясо'),
                ('индейка', 350.00, 'кг', 'мясо'),
                ('рис', 80.00, 'кг', 'крупы'),
                ('гречка', 120.00, 'кг', 'крупы'),
                ('макароны', 110.00, 'кг', 'крупы'),
                ('картофель', 45.00, 'кг', 'овощи'),
                ('морковь', 35.00, 'кг', 'овощи'),
                ('лук', 25.00, 'кг', 'овощи'),
                ('чеснок', 200.00, 'кг', 'овощи'),
                ('помидор', 120.00, 'кг', 'овощи'),
                ('огурец', 90.00, 'кг', 'овощи'),
                ('перец', 130.00, 'кг', 'овощи'),
                ('капуста', 30.00, 'кг', 'овощи'),
                ('мука', 55.00, 'кг', 'бакалея'),
                ('сахар', 70.00, 'кг', 'бакалея'),
                ('соль', 20.00, 'кг', 'бакалея'),
                ('масло сливочное', 180.00, 'кг', 'молочные'),
                ('яйцо', 12.00, 'шт', 'молочные'),
                ('молоко', 75.00, 'л', 'молочные'),
                ('сметана', 130.00, 'кг', 'молочные'),
                ('сыр', 650.00, 'кг', 'молочные'),
                ('творог', 200.00, 'кг', 'молочные'),
                ('масло растительное', 120.00, 'л', 'бакалея'),
                ('хлеб', 60.00, 'шт', 'хлеб')
            ]

            for ingredient in base_ingredients:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO ingredients (name, price_per_unit, unit, category) VALUES (?, ?, ?, ?)",
                        ingredient
                    )
                except Error as e:
                    print(f"Ошибка добавления ингредиента {ingredient[0]}: {e}")

            self.connection.commit()

            self.ensure_recipe_seeds(cursor)

            self.connection.commit()
            cursor.close()
            print("[database] init completed successfully")

        except Error as e:
            print(f"Ошибка инициализации БД: {e}")
            import traceback
            traceback.print_exc()

    def ensure_recipe_seeds(self, cursor):
        """Вставляет недостающие демо-рецепты по имени (для каждой кухни из справочника)."""
        try:
            from database.seed_recipes import RECIPE_SEEDS
        except ImportError:
            try:
                from seed_recipes import RECIPE_SEEDS
            except ImportError:
                print("ensure_recipe_seeds: seed_recipes module not found")
                return

        seeds = list(RECIPE_SEEDS)
        try:
            from database.seed_recipes_extended import MORE_RECIPE_SEEDS
            seeds.extend(MORE_RECIPE_SEEDS)
        except ImportError:
            try:
                from seed_recipes_extended import MORE_RECIPE_SEEDS
                seeds.extend(MORE_RECIPE_SEEDS)
            except ImportError:
                pass

        try:
            cursor.execute("SELECT id FROM users WHERE username = 'chef'")
            chef_row = cursor.fetchone()
            if not chef_row:
                cursor.execute("SELECT id FROM users WHERE username = 'admin'")
                chef_row = cursor.fetchone()
            if not chef_row:
                print("ensure_recipe_seeds: no chef/admin user")
                return
            chef_id = chef_row[0]

            cursor.execute("SELECT id, name FROM cuisines")
            cuisines_dict = {name: cid for cid, name in cursor.fetchall()}

            inserted = 0
            for r in seeds:
                cuisine_id = cuisines_dict.get(r["cuisine"])
                if cuisine_id is None:
                    continue
                cursor.execute(
                    "SELECT 1 FROM recipes WHERE name = ?",
                    (r["name"],),
                )
                if cursor.fetchone():
                    continue
                cursor.execute(
                    """
                    INSERT INTO recipes (
                        name, description, ingredients, instructions,
                        preparation_time, cooking_time, total_time,
                        base_portions, difficulty, cuisine_id,
                        calories, proteins, fats, carbs, tags, image_path, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        r["name"],
                        r["description"],
                        r["ingredients"],
                        r["instructions"],
                        r["preparation_time"],
                        r["cooking_time"],
                        r["total_time"],
                        r["base_portions"],
                        r["difficulty"],
                        cuisine_id,
                        r["calories"],
                        r["proteins"],
                        r["fats"],
                        r["carbs"],
                        r["tags"],
                        "",
                        chef_id,
                    ),
                )
                inserted += 1

            if inserted:
                print(f"ensure_recipe_seeds: inserted {inserted} recipe(s)")

        except Error as e:
            print(f"ensure_recipe_seeds error: {e}")

    # باقي الدوال تبقى كما هي بدون تغيير
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def execute_query(self, query, params=None):
        """Выполнение запроса к базе данных"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = None

            cursor.close()
            return result
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None

    def get_user_by_credentials(self, username, password_hash):
        """Получение пользователя по логину и хешу пароля"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id, username, full_name, role FROM users WHERE username = ? AND password = ?",
                (username, password_hash)
            )
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Ошибка получения пользователя: {e}")
            return None

    def get_all_cuisines(self):
        """Получение всех кухонь"""
        return self.execute_query("SELECT id, name, country, description FROM cuisines ORDER BY name")

    def get_all_recipes(self):
        """Получение всех рецептов"""
        return self.execute_query('''
            SELECT r.id, r.name, c.name, c.country, r.base_portions, r.total_time, r.difficulty, r.calories
            FROM recipes r 
            JOIN cuisines c ON r.cuisine_id = c.id
            ORDER BY r.name
        ''')

    def get_recipe_by_id(self, recipe_id):
        """Получение рецепта по ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT r.name, r.description, r.ingredients, r.instructions, r.base_portions, 
                       r.preparation_time, r.cooking_time, r.total_time, r.difficulty, 
                       c.name, c.country, r.calories, r.proteins, r.fats, r.carbs, r.tags
                FROM recipes r 
                JOIN cuisines c ON r.cuisine_id = c.id
                WHERE r.id = ?
            ''', (recipe_id,))
            recipe = cursor.fetchone()
            cursor.close()
            return recipe
        except Error as e:
            print(f"Ошибка получения рецепта: {e}")
            return None

    def add_recipe(self, recipe_data):
        """Добавление нового рецепта"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO recipes (name, description, ingredients, instructions, 
                                  base_portions, difficulty, cuisine_id, created_by,
                                  preparation_time, cooking_time, total_time, calories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', recipe_data)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Ошибка добавления рецепта: {e}")
            return False

    def delete_recipe(self, recipe_id):
        """Удаление рецепта с перемещением в архив"""
        try:
            cursor = self.connection.cursor()
            
            # 1. Получаем данные перед удалением для архива
            cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            recipe_row = cursor.fetchone()
            
            if recipe_row:
                # 2. Сохраняем в архив (упрощенно как JSON/текст или поля)
                cursor.execute(
                    "INSERT INTO archived_recipes (original_id, name, data) VALUES (?, ?, ?)",
                    (recipe_id, recipe_row[1], str(recipe_row))
                )
                
                # 3. Удаляем оригинал
                cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
                self.connection.commit()
            
            cursor.close()
            return True
        except Error as e:
            print(f"Ошибка удаления рецепта: {e}")
            return False

    def get_all_users(self):
        """Получение всех пользователей"""
        return self.execute_query('''
            SELECT id, username, full_name, role, created_at 
            FROM users 
            ORDER BY created_at DESC
        ''')

    def add_user(self, user_data):
        """Добавление нового пользователя"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                user_data
            )
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Ошибка добавления пользователя: {e}")
            return False

    def delete_user(self, user_id):
        """Удаление пользователя с перемещением в архив"""
        try:
            cursor = self.connection.cursor()
            
            # 1. Получаем данные
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
            
            if user_row:
                # 2. В архив
                cursor.execute(
                    "INSERT INTO archived_users (original_id, username, data) VALUES (?, ?, ?)",
                    (user_id, user_row[1], str(user_row))
                )
                
                # 3. Удаляем
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                self.connection.commit()
                
            cursor.close()
            return True
        except Error as e:
            print(f"Ошибка удаления пользователя: {e}")
            return False

    def close_connection(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()

    def get_system_stats(self):
        """Получение статистики системы"""
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM recipes")
            recipes_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM cuisines")
            cuisines_count = cursor.fetchone()[0]

            cursor.close()

            return {
                'recipes': recipes_count,
                'users': users_count,
                'cuisines': cuisines_count
            }
        except Error as e:
            print(f"Ошибка получения статистики: {e}")
            return {'recipes': 0, 'users': 0, 'cuisines': 0}

