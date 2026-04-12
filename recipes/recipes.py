import tkinter as tk
from tkinter import ttk, messagebox
from sqlite3 import Error
from datetime import datetime


class RecipeManager:
    def __init__(self, db_manager, app):
        self.db_manager = db_manager
        self.app = app

    # ================= Статистика =================
    def show_recipe_statistics(self):
        """Статистика системы с поддержкой старых рецептов без tags"""
        self.app.clear_window()
        self.app.root.geometry("1000x700")
        self.app.current_frame = ttk.Frame(self.app.root, padding=20)
        self.app.current_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.app.current_frame, text="📊 Статистика системы", style='Title.TLabel').pack(pady=10)
        stats_frame = ttk.Frame(self.app.current_frame)
        stats_frame.pack(fill='x', pady=10)

        try:
            cursor = self.db_manager.db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes")
            total_recipes = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM cuisines")
            total_cuisines = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            # Статистика по категориям с учетом старых рецептов
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN name LIKE '%салат%' OR tags LIKE '%салат%' OR tags IS NULL THEN 'Салаты'
                        WHEN name LIKE '%суп%' OR tags LIKE '%суп%' THEN 'Супы'
                        WHEN name LIKE '%десерт%' OR tags LIKE '%десерт%' THEN 'Десерты'
                        WHEN name LIKE '%напиток%' OR tags LIKE '%напиток%' THEN 'Напитки'
                        ELSE 'Основные блюда'
                    END as category,
                    COUNT(*) as count,
                    AVG(calories) as avg_calories,
                    AVG(total_time) as avg_time
                FROM recipes 
                GROUP BY category
                ORDER BY count DESC
            ''')
            category_stats = cursor.fetchall()
            cursor.close()

            stats_text = f"Всего рецептов: {total_recipes} | Всего кухонь: {total_cuisines} | Всего пользователей: {total_users}"
            ttk.Label(stats_frame, text=stats_text, font=('Arial', 12, 'bold')).pack(pady=5)

        except Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки статистики: {e}")
            return

        # ================== Фильтры ==================
        filter_frame = ttk.Frame(self.app.current_frame)
        filter_frame.pack(fill='x', pady=10)

        ttk.Label(filter_frame, text="Фильтры", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Label(filter_frame, text="Отчёт:").grid(row=1, column=0, sticky='w', pady=2)
        report_combo = ttk.Combobox(filter_frame, values=['По кухням', 'По категориям'], width=15)
        report_combo.set('По кухням')
        report_combo.grid(row=1, column=1, pady=2, padx=5, sticky='w')

        ttk.Label(filter_frame, text="Кухня:").grid(row=2, column=0, sticky='w', pady=2)
        cuisine_combo = ttk.Combobox(filter_frame, width=15)
        cuisine_combo.grid(row=2, column=1, pady=2, padx=5, sticky='w')

        ttk.Label(filter_frame, text="Категория:").grid(row=3, column=0, sticky='w', pady=2)
        category_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="Все", variable=category_var, value="all").grid(row=3, column=1, sticky='w', padx=5)
        ttk.Radiobutton(filter_frame, text="Блюда", variable=category_var, value="main").grid(row=3, column=2, sticky='w', padx=5)
        ttk.Radiobutton(filter_frame, text="Салаты", variable=category_var, value="salads").grid(row=3, column=3, sticky='w', padx=5)

        # Загрузка кухонь
        try:
            cursor = self.db_manager.db_connection.cursor()
            cursor.execute("SELECT name FROM cuisines ORDER BY name")
            cuisines = [row[0] for row in cursor.fetchall()]
            cuisine_combo['values'] = cuisines
            cursor.close()
        except Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки кухонь: {e}")

        # ================== Таблица статистики ==================
        table_frame = ttk.Frame(self.app.current_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        stats_tree = ttk.Treeview(table_frame, columns=('Категория', 'Кол-во', 'Ср. калории', 'Ср. время'),
                                  show='headings', height=8)
        stats_tree.heading('Категория', text='Категория')
        stats_tree.heading('Кол-во', text='Кол-во')
        stats_tree.heading('Ср. калории', text='Ср. калории')
        stats_tree.heading('Ср. время', text='Ср. время (мин)')
        stats_tree.column('Категория', width=150)
        stats_tree.column('Кол-во', width=80)
        stats_tree.column('Ср. калории', width=100)
        stats_tree.column('Ср. время', width=120)

        for category in category_stats:
            category_name = category[0]
            count = category[1]
            avg_calories = round(category[2] or 0)
            avg_time = round(category[3] or 0)
            stats_tree.insert('', tk.END, values=(category_name, count, avg_calories, avg_time))

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=stats_tree.yview)
        stats_tree.configure(yscrollcommand=scrollbar.set)
        stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ================== Список рецептов ==================
        ttk.Label(self.app.current_frame, text="📋 Список рецептов по выбранному фильтру",
                  font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        recipes_tree = ttk.Treeview(self.app.current_frame,
                                    columns=('ID', 'Название', 'Порции', 'Время', 'Сложность', 'Калории'),
                                    show='headings', height=6)
        for col in recipes_tree["columns"]:
            recipes_tree.heading(col, text=col)
            recipes_tree.column(col, width=100)
        recipes_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        self.load_categorized_recipes(recipes_tree, category_var.get())

        # ================== Кнопки ==================
        btn_frame = ttk.Frame(self.app.current_frame)
        btn_frame.pack(pady=10)

        def refresh_stats():
            self.load_categorized_recipes(recipes_tree, category_var.get())

        def apply_filters():
            selected_report = report_combo.get()
            selected_cuisine = cuisine_combo.get()
            selected_category = category_var.get()
            self.load_filtered_recipes(recipes_tree, selected_report, selected_cuisine, selected_category)

        ttk.Button(btn_frame, text="🔍 Применить", command=apply_filters).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=refresh_stats).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="↩️ Назад", command=self.app.show_main_menu).pack(side='left', padx=5)

    # ================== Загрузка рецептов по категории ==================
    def load_categorized_recipes(self, tree, category_filter):
        for item in tree.get_children():
            tree.delete(item)
        try:
            cursor = self.db_manager.db_connection.cursor()
            query = "SELECT id, name, base_portions, total_time, difficulty, calories FROM recipes WHERE 1=1"
            params = []

            if category_filter == "salads":
                query += " AND ((name LIKE ? OR tags LIKE ?) OR tags IS NULL)"
                params.extend(['%салат%', '%салат%'])
            elif category_filter == "main":
                query += " AND ((name NOT LIKE ? AND (tags NOT LIKE ? OR tags IS NULL)))"
                params.extend(['%салат%', '%салат%'])

            query += " ORDER BY name LIMIT 50"
            cursor.execute(query, params)
            for row in cursor.fetchall():
                tree.insert('', tk.END, values=row)
            cursor.close()
        except Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки рецептов: {e}")

    # ================== Загрузка рецептов с фильтром ==================
    def load_filtered_recipes(self, tree, report_type, cuisine, category):
        for item in tree.get_children():
            tree.delete(item)
        try:
            cursor = self.db_manager.db_connection.cursor()
            params = []
            if report_type == 'По кухням':
                query = '''
                SELECT r.id, r.name, r.base_portions, r.total_time, r.difficulty, r.calories
                FROM recipes r
                JOIN cuisines c ON r.cuisine_id = c.id
                WHERE 1=1
                '''
                if cuisine:
                    query += " AND c.name = ?"
                    params.append(cuisine)
            else:
                query = "SELECT id, name, base_portions, total_time, difficulty, calories FROM recipes WHERE 1=1"

            if category == "salads":
                query += " AND ((name LIKE ? OR tags LIKE ?) OR tags IS NULL)"
                params.extend(['%салат%', '%салат%'])
            elif category == "main":
                query += " AND ((name NOT LIKE ? AND (tags NOT LIKE ? OR tags IS NULL)))"
                params.extend(['%салат%', '%салат%'])

            query += " ORDER BY name"
            cursor.execute(query, params)
            for row in cursor.fetchall():
                tree.insert('', tk.END, values=row)
            cursor.close()
            messagebox.showinfo("Информация", f"Найдено рецептов: {len(tree.get_children())}")
        except Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки рецептов: {e}")

    # ================== Остальные методы (создание, просмотр, добавление) ==================
    # Методы create_personal_recipe, show_recipe_details и др. можно добавить здесь без изменений
