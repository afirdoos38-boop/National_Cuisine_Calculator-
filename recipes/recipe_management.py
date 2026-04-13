"""
recipes/recipe_management.py
Центральный модуль управления рецептами. Реализует каталог, детальный просмотр,
поиск и фильтрацию, а также механизмы архивации (soft-delete) и автоматической
категоризации блюд.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from database.database import DatabaseManager

# Попытка импортировать Pillow для работы с изображениями
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


class RecipeManagement:
    def __init__(self, app):
        self.app = app
        self.db = DatabaseManager()

        # Для хранения текущего ImageTk.PhotoImage, чтобы GC не удалял изображение
        self._image_preview_ref = None

    def auto_categorize_recipe(self, recipe_name, description="", tags=""):
        """Автоматическая категоризация рецепта по названию"""
        name_lower = (recipe_name or "").lower()

        salad_terms = ['салат', 'salad']
        for term in salad_terms:
            if term in name_lower:
                return 'салат'

        dessert_terms = ['десерт', 'dessert', 'торт', 'пирог', 'кекс']
        for term in dessert_terms:
            if term in name_lower:
                return 'десерт'

        soup_terms = ['суп', 'soup', 'бульон']
        for term in soup_terms:
            if term in name_lower:
                return 'суп'

        appetizer_terms = ['закуска', 'appetizer', 'канапе', 'брускетта']
        for term in appetizer_terms:
            if term in name_lower:
                return 'закуска'

        drink_terms = ['напиток', 'drink', 'коктейль', 'сок', 'компот']
        for term in drink_terms:
            if term in name_lower:
                return 'напиток'

        main_dish_terms = ['блюдо', 'main', 'гарнир', 'мясо', 'курица', 'рыба', 'паста', 'рис']
        for term in main_dish_terms:
            if term in name_lower:
                return 'основное блюдо'

        return 'Без категории'

    # ------------------ КАТАЛОГ РЕЦЕПТОВ ------------------
    def show_recipe_catalog(self, initial_search=None):
        """Каталог рецептов (Requirement 6: сохранение состояния)"""
        self.app.update_nav_stack(self.show_recipe_catalog, 'menu_catalog', args=[initial_search])
        self.app.draw_header()
        self.app.create_scrollable_frame(padding=25)
        self.app.current_frame.help_tag = 'help_catalog'

        ttk.Label(self.app.current_frame, text=self.app.get_text('menu_catalog'),
                  style='Title.TLabel').pack(pady=10)

        # Поиск и фильтры
        # Поиск и фильтры (Premium Grid Layout)
        search_frame = ttk.LabelFrame(self.app.current_frame, text=self.app.get_text('filters_title'), padding=10)
        search_frame.pack(fill='x', pady=10)
        
        for i in range(4):
            search_frame.columnconfigure(i, weight=1)

        ttk.Label(search_frame, text=self.app.get_text('search_label')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        search_entry = ttk.Entry(search_frame)
        if initial_search:
            search_entry.insert(0, initial_search)
        search_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(search_frame, text=self.app.get_text('cuisine_label')).grid(row=0, column=2, sticky='w', padx=5, pady=5)
        cuisine_combo = ttk.Combobox(search_frame)
        cuisine_combo.grid(row=0, column=3, sticky='ew', padx=5, pady=5)

        ttk.Label(search_frame, text=self.app.get_text('difficulty_label')).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        difficulty_combo = ttk.Combobox(search_frame, values=['', self.app.get_text('diff_easy'), self.app.get_text('diff_medium'), self.app.get_text('diff_hard')])
        difficulty_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(search_frame, text=self.app.get_text('category_label')).grid(row=1, column=2, sticky='w', padx=5, pady=5)
        category_combo = ttk.Combobox(search_frame,
                                      values=['', self.app.get_text('cat_salad'), self.app.get_text('cat_soup'), self.app.get_text('cat_snack'), self.app.get_text('cat_main'), self.app.get_text('cat_dessert'), self.app.get_text('cat_drink')])
        category_combo.set('')
        category_combo.grid(row=1, column=3, sticky='ew', padx=5, pady=5)

        # Ряд 2: Кнопки действий (Centered)
        btn_container = ttk.Frame(search_frame)
        btn_container.grid(row=2, column=0, columnspan=4, pady=10)

        # Функции фильтрации должны быть определены далее, но кнопки можно объявить сейчас
        # (Они используют лямбды или будут привязаны позже)
        # На самом деле они определяются ниже по коду, поэтому используем command=apply_filters
        
        # Переместим определение функций фильтрации выше или используем существующие
        # В текущем файле они определены ниже. Тк это Tkinter, мы можем использовать 
        # отложенную привязку или просто передвинуть их.
        
        apply_btn = ttk.Button(btn_container, text=self.app.get_text('apply_filters'), style='Accent.TButton')
        apply_btn.pack(side='left', padx=10)
        
        reset_btn = ttk.Button(btn_container, text=self.app.get_text('reset_filters'))
        reset_btn.pack(side='left', padx=10)

        def apply_filters():
            load_recipes()

        def reset_filters():
            search_entry.delete(0, tk.END)
            cuisine_combo.set('')
            difficulty_combo.set('')
            category_combo.set('')
            load_recipes()

        apply_btn.configure(command=apply_filters)
        reset_btn.configure(command=reset_filters)

        # При поиске по Enter
        search_entry.bind('<Return>', lambda e: apply_filters())

        # Таблица рецептов
        tree_frame = ttk.Frame(self.app.current_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns_keys = ['col_id', 'col_name', 'col_cuisine', 'col_country', 'col_portions', 'col_time', 'col_difficulty', 'col_calories']
        columns = tuple(self.app.get_text(k) for k in columns_keys)
        # Уменьшаем высоту таблицы для лучшей читаемости на малых экранах
        tree = ttk.Treeview(tree_frame, columns=columns_keys, show='headings', height=12)

        col_widths = [50, 250, 120, 100, 80, 80, 100, 90]
        for i, (key, width) in enumerate(zip(columns_keys, col_widths)):
            tree.heading(key, text=self.app.get_text(key))
            # Название (вторая колонка) должно растягиваться максимально и быть по левому краю
            stretch = True if i == 1 else False 
            anchor = tk.W if i == 1 else tk.CENTER
            tree.column(key, width=width, anchor=anchor, stretch=stretch)

        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        def on_double_click(event):
            item_id = tree.identify_row(event.y)
            if not item_id:
                return
            item = tree.item(item_id)
            values = item.get('values') or []
            if values:
                recipe_id = values[0]
                self.show_recipe_details(recipe_id)

        tree.bind("<Double-1>", on_double_click)

        def load_cuisines():
            """
            Загружает уникальные названия кухонь в combobox.
            Убирает дубликаты на уровне запроса и дополнительно нормализует значения.
            """
            cursor = None
            try:
                cursor = self.app.db_connection.cursor()
                cursor.execute("SELECT DISTINCT TRIM(name) FROM cuisines ORDER BY TRIM(name)")
                rows = cursor.fetchall()
                cuisines = []
                seen = set()
                for r in rows:
                    if not r:
                        continue
                    name = (r[0] or "").strip()
                    key = name.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    cuisines.append(name)
                cuisine_combo['values'] = [''] + cuisines
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки кухонь: {e}")
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass

        def load_recipes():
            cursor = None
            try:
                for item in tree.get_children():
                    tree.delete(item)

                cursor = self.app.db_connection.cursor()
                query = '''
                    SELECT r.id, r.name, c.name, c.country,
                           r.base_portions, r.total_time, 
                           r.difficulty, r.calories,
                           r.tags
                    FROM recipes r 
                    JOIN cuisines c ON r.cuisine_id = c.id 
                    WHERE 1=1
                '''
                params = []

                search_text = search_entry.get().strip()
                if search_text:
                    query += " AND r.name LIKE ?"
                    params.append(f"%{search_text}%")

                cuisine = cuisine_combo.get().strip()
                if cuisine:
                    query += " AND c.name = ?"
                    params.append(cuisine)

                difficulty = difficulty_combo.get().strip()
                if difficulty:
                    query += " AND r.difficulty = ?"
                    params.append(difficulty)

                category = category_combo.get().strip()
                if category:
                    # теги вида "суп,говядина" — ищем вхождение категории
                    query += " AND IFNULL(r.tags, '') LIKE ?"
                    params.append(f"%{category}%")

                query += " ORDER BY r.name"
                cursor.execute(query, params)

                rows = cursor.fetchall()
                for row in rows:
                    (recipe_id, name, cuisine_name, country,
                     portions, time, difficulty_val, calories, tags) = row

                    base_name = name
                    # ⭐ персональные рецепты помечаем звездочкой
                    if tags == "персональный":
                        base_name = f"★ {base_name}"

                    display_name = base_name
                    if hasattr(self.app, 'calculator') and getattr(self.app, 'calculator', None) is not None:
                        calc = getattr(self.app, 'calculator')
                        if hasattr(calc, 'selected_recipes') and recipe_id in getattr(calc, 'selected_recipes', []):
                            display_name = f"← {base_name}"

                    tree.insert('', tk.END, values=(
                        recipe_id, display_name, cuisine_name, country,
                        portions, time, difficulty_val, calories
                    ))

                count = len(tree.get_children())
                result_label.config(text=self.app.get_text('recipes_found').format(n=count))

            except Exception as e:
                messagebox.showerror(self.app.get_text('error'), f"{self.app.get_text('error_db')}: {e}")
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass

        def show_recipe_details_btn():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                recipe_id = item['values'][0]
                self.show_recipe_details(recipe_id)
            else:
                messagebox.showwarning(self.app.get_text('warning'), self.app.get_text('select_recipe_warning'))

        def calculate_recipe():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                recipe_id = item['values'][0]
                self.app.show_calculator_for_recipe(recipe_id)
            else:
                messagebox.showwarning(self.app.get_text('warning'), self.app.get_text('select_recipe_for_calc_btn'))

        def edit_recipe():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                recipe_id = item['values'][0]
                self.edit_recipe(recipe_id)
            else:
                messagebox.showwarning(self.app.get_text('warning'), self.app.get_text('select_recipe_for_edit'))

        def delete_recipe():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                recipe_id = item['values'][0]
                recipe_name = item['values'][1]
                # Requirement 1: Confirmation before data loss
                if messagebox.askyesno(self.app.get_text('confirm_delete_title'), 
                                      f"{self.app.get_text('confirm_delete_msg')}\n\n{recipe_name}"):
                    if self.app.db_manager.delete_recipe(recipe_id):
                        load_recipes()
                        messagebox.showinfo(self.app.get_text('success'), self.app.get_text('recipe_deleted_success'))
                    else:
                        messagebox.showerror(self.app.get_text('error'), self.app.get_text('recipe_delete_error'))
            else:
                messagebox.showwarning(self.app.get_text('warning'), self.app.get_text('select_recipe_for_delete'))

        # Кнопки управления
        btn_frame = ttk.Frame(self.app.current_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text=self.app.get_text('search'), command=load_recipes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.app.get_text('view_details'), command=show_recipe_details_btn, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.app.get_text('calculate_btn'), command=calculate_recipe).pack(side='left', padx=5)

        if self.app.current_user['role'] in ['admin', 'chef']:
            ttk.Button(btn_frame, text=self.app.get_text('edit_btn'), command=edit_recipe).pack(side='left', padx=5)
            ttk.Button(btn_frame, text=self.app.get_text('delete_btn'), command=delete_recipe,
                       style='Delete.TButton').pack(side='left', padx=5)
        
        ttk.Button(self.app.current_frame, text=self.app.get_text('back_to_main'), 
                   command=self.app.show_main_menu, style='Secondary.TButton').pack(pady=10)

        ttk.Button(btn_frame, text=self.app.get_text('back'), command=self.app.show_main_menu).pack(side='left', padx=5)

        result_label = ttk.Label(self.app.current_frame, text=self.app.get_text('recipes_found').format(n=0))
        result_label.pack(pady=5)

        load_cuisines()
        load_recipes()

        try:
            self.app.fit_window_to_content()
        except:
            pass

    # ------------------ ДЕТАЛИ РЕЦЕПТА ------------------
    def show_recipe_details(self, recipe_id):
        """Просмотр карточки рецепта (Requirement 8 - Похоже на документ)"""
        # Сохраняем текущее состояние каталога (например, текст поиска) для возврата (Requirement 6)
        current_search = ""
        try:
            # Пытаемся найти поле ввода поиска в текущем фрейме перед очисткой
            for child in self.app.current_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    for sub in child.winfo_children():
                        if isinstance(sub, ttk.Entry):
                            current_search = sub.get()
                            break
        except: pass

        self.app.update_nav_stack(self.show_recipe_details, 'view_details', args=[recipe_id])
        self.app.draw_header()
        self.app.create_scrollable_frame(padding=25)
        self.app.current_frame.help_tag = 'help_details'

        cursor = None
        try:
            cursor = self.app.db_connection.cursor()
            cursor.execute('''
                SELECT r.name, r.description, r.ingredients, r.instructions, 
                       r.base_portions, r.preparation_time, r.cooking_time, 
                       r.total_time, r.difficulty, c.name, c.country, 
                       r.calories, r.proteins, r.fats, r.carbs, r.tags, r.image_path
                FROM recipes r 
                JOIN cuisines c ON r.cuisine_id = c.id 
                WHERE r.id = ?
            ''', (recipe_id,))
            recipe = cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки рецепта: {e}")
            self.show_recipe_catalog()
            return
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

        if not recipe:
            messagebox.showerror("Ошибка", "Рецепт не найден")
            self.show_recipe_catalog()
            return

        (name, description, ingredients, instructions, base_portions,
         prep_time, cook_time, total_time, difficulty, cuisine_name,
         country, calories, proteins, fats, carbs, tags, image_path) = recipe

        # добавляем звёздочку и пометку, если рецепт персональный
        title = name
        if tags == "персональный":
            title = f"★ {name}"

        ttk.Label(self.app.current_frame, text=title, style='Title.TLabel').pack(pady=10)

        if description:
            ttk.Label(self.app.current_frame, text=description,
                      style='Subtitle.TLabel', wraplength=600).pack(pady=5)

        if tags == "персональный":
            ttk.Label(self.app.current_frame, text="Тип: персональный рецепт",
                      font=('Arial', 9, 'italic'), foreground='blue').pack(pady=2)

        info_text = f"🌍 Кухня: {cuisine_name} ({country}) | 🍽️ Порции: {base_portions} | ⏱️ Время: {total_time} мин. | 📊 Сложность: {difficulty}"
        ttk.Label(self.app.current_frame, text=info_text, font=('Arial', 10)).pack(pady=5)

        nutrition_text = f"🔥 Калории: {calories} | 🥩 Белки: {proteins}г | 🥑 Жиры: {fats}г | 🍚 Углеводы: {carbs}г"
        ttk.Label(self.app.current_frame, text=nutrition_text,
                  font=('Arial', 9), foreground='green').pack(pady=2)

        # Показ изображения (если есть)
        if image_path:
            img_frame = ttk.Frame(self.app.current_frame)
            img_frame.pack(pady=8)
            if PIL_AVAILABLE and os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    max_w, max_h = 400, 300
                    img.thumbnail((max_w, max_h))
                    photo = ImageTk.PhotoImage(img)
                    lbl = ttk.Label(img_frame, image=photo)
                    lbl.image = photo  # удерживаем ссылку
                    lbl.pack()
                except Exception as e:
                    ttk.Label(img_frame, text=f"Ошибка загрузки изображения: {e}").pack()
            else:
                ttk.Label(img_frame, text=f"Изображение: {image_path}").pack()

        # Ингредиенты
        ttk.Label(self.app.current_frame, text="🛒 Ингредиенты:",
                  font=('Arial', 12, 'bold')).pack(anchor='w', pady=(15, 5))

        ingredients_frame = ttk.Frame(self.app.current_frame)
        ingredients_frame.pack(fill='x', pady=5)

        ingredients_text_widget = tk.Text(ingredients_frame, height=8, width=80, font=('Arial', 10))
        ingredients_text_widget.insert('1.0', ingredients or "")
        ingredients_text_widget.config(state='disabled')

        ingredients_scroll = ttk.Scrollbar(ingredients_frame, orient=tk.VERTICAL,
                                           command=ingredients_text_widget.yview)
        ingredients_text_widget.configure(yscrollcommand=ingredients_scroll.set)

        ingredients_text_widget.pack(side='left', fill='both', expand=True)
        ingredients_scroll.pack(side='right', fill='y')

        # Инструкции
        ttk.Label(self.app.current_frame, text="👨‍🍳 Приготовление:",
                  font=('Arial', 12, 'bold')).pack(anchor='w', pady=(15, 5))

        instructions_frame = ttk.Frame(self.app.current_frame)
        instructions_frame.pack(fill='x', pady=5)

        instructions_text_widget = tk.Text(instructions_frame, height=10, width=80, font=('Arial', 10))
        instructions_text_widget.insert('1.0', instructions or "")
        instructions_text_widget.config(state='disabled')

        instructions_scroll = ttk.Scrollbar(instructions_frame, orient=tk.VERTICAL,
                                            command=instructions_text_widget.yview)
        instructions_text_widget.configure(yscrollcommand=instructions_scroll.set)

        instructions_text_widget.pack(side='left', fill='both', expand=True)
        instructions_scroll.pack(side='right', fill='y')

        # Кнопки управления
        btn_frame = ttk.Frame(self.app.current_frame)
        btn_frame.pack(pady=15)

        def calculate_this_recipe():
            self.app.show_calculator_for_recipe(recipe_id)

        if self.app.current_user['role'] in ['admin', 'chef']:
            def edit_this_recipe():
                self.edit_recipe(recipe_id)
            ttk.Button(btn_frame, text="✏️ Редактировать", command=edit_this_recipe).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="🧮 Рассчитать продукты", command=calculate_this_recipe).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.app.get_text('back'), command=self.show_recipe_catalog).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🏠 Главная", command=self.app.show_main_menu).pack(side='left', padx=5)

    # ------------------ РЕДАКТИРОВАНИЕ РЕЦЕПТА (с поддержкой изображения) ------------------
    def edit_recipe(self, recipe_id):
        """Редактирование рецепта (с возможностью изменить изображение)"""
        self.app.draw_header()
        self.app.create_scrollable_frame(padding=25)
        ttk.Label(self.app.current_frame, text="✏️ Редактировать рецепт", style='Title.TLabel').pack(pady=10)

        cursor = None
        try:
            cursor = self.app.db_connection.cursor()
            cursor.execute('''
                SELECT r.name, r.description, r.ingredients, r.instructions, 
                       r.base_portions, r.difficulty, c.name, r.calories, 
                       r.proteins, r.fats, r.carbs, r.tags, r.image_path
                FROM recipes r 
                JOIN cuisines c ON r.cuisine_id = c.id 
                WHERE r.id = ?
            ''', (recipe_id,))
            recipe = cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки рецепта: {e}")
            self.show_recipe_catalog()
            return
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

        if not recipe:
            messagebox.showerror("Ошибка", "Рецепт не найден")
            self.show_recipe_catalog()
            return

        # Распакуем поля
        (name_val, desc_val, ingredients_val, instructions_val, portions_val, difficulty_val,
         cuisine_val, calories_val, proteins_val, fats_val, carbs_val, tags_val, image_path_val) = recipe

        form_frame = ttk.Frame(self.app.current_frame)
        form_frame.pack(fill='x', pady=10)

        ttk.Label(form_frame, text="Название рецепта:").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.insert(0, name_val)
        name_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky='w', pady=5)
        desc_entry = ttk.Entry(form_frame, width=40)
        desc_entry.insert(0, desc_val or "")
        desc_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Кухня:").grid(row=2, column=0, sticky='w', pady=5)
        cuisine_combo = ttk.Combobox(form_frame, width=37)
        cuisine_combo.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Категория:").grid(row=3, column=0, sticky='w', pady=5)
        category_combo = ttk.Combobox(form_frame, width=37)
        category_combo.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Ингредиенты:").grid(row=4, column=0, sticky='nw', pady=5)
        ingredients_text = tk.Text(form_frame, width=40, height=5)
        ingredients_text.insert('1.0', ingredients_val or "")
        ingredients_text.grid(row=4, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Инструкции:").grid(row=5, column=0, sticky='nw', pady=5)
        instructions_text = tk.Text(form_frame, width=40, height=5)
        instructions_text.insert('1.0', instructions_val or "")
        instructions_text.grid(row=5, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Порции:").grid(row=6, column=0, sticky='w', pady=5)
        portions_entry = ttk.Entry(form_frame, width=10)
        portions_entry.insert(0, str(portions_val))
        portions_entry.grid(row=6, column=1, pady=5, padx=5, sticky='w')

        ttk.Label(form_frame, text="Сложность:").grid(row=7, column=0, sticky='w', pady=5)
        difficulty_combo = ttk.Combobox(form_frame, values=['легко', 'средне', 'сложно'], width=10)
        difficulty_combo.set(difficulty_val)
        difficulty_combo.grid(row=7, column=1, pady=5, padx=5, sticky='w')

        # Блок изображения: кнопка выбора + превью + поле пути (скрытое)
        image_frame = ttk.Frame(form_frame)
        image_frame.grid(row=8, column=0, columnspan=2, pady=10, sticky='w')

        image_path_var = tk.StringVar(value=image_path_val or "")

        def choose_image():
            path = filedialog.askopenfilename(
                title="Выберите изображение",
                filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All files", "*.*")]
            )
            if path:
                image_path_var.set(path)
                show_image_preview(path)

        def show_image_preview(path):
            # превью в отдельном окне формы
            preview_holder = getattr(self, '_image_preview_holder', None)
            if preview_holder is None:
                preview_holder = ttk.Label(image_frame)
                preview_holder.grid(row=0, column=2, padx=10)
                self._image_preview_holder = preview_holder

            if PIL_AVAILABLE and os.path.exists(path):
                try:
                    img = Image.open(path)
                    img.thumbnail((200, 150))
                    photo = ImageTk.PhotoImage(img)
                    preview_holder.configure(image=photo)
                    preview_holder.image = photo
                    # сохранить ссылку чтобы не собрать GC
                    self._image_preview_ref = photo
                except Exception as e:
                    preview_holder.configure(text=f"Ошибка превью: {e}")
            else:
                preview_holder.configure(text=os.path.basename(path) if path else "Нет изображения")

        ttk.Label(image_frame, textvariable=image_path_var).grid(row=0, column=1, padx=5)

        # Загрузка списков кухонь и категорий
        def load_cuisines():
            cursor = None
            try:
                cursor = self.app.db_connection.cursor()
                cursor.execute("SELECT DISTINCT TRIM(name) FROM cuisines ORDER BY TRIM(name)")
                rows = cursor.fetchall()
                cuisines = []
                seen = set()
                for r in rows:
                    if not r:
                        continue
                    name = (r[0] or "").strip()
                    key = name.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    cuisines.append(name)
                cuisine_combo['values'] = cuisines
                if cuisines:
                    cuisine_combo.set(cuisine_val)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки кухонь: {e}")
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass

        def load_categories():
            categories = [
                'Без категории',
                'салат',
                'суп',
                'закуска',
                'основное блюдо',
                'десерт',
                'напиток'
            ]
            category_combo['values'] = categories
            current_cat = tags_val if tags_val else 'Без категории'
            category_combo.set(current_cat)

        def save_changes():
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            ingredients = ingredients_text.get("1.0", tk.END).strip()
            instructions = instructions_text.get("1.0", tk.END).strip()
            cuisine_name = cuisine_combo.get().strip()
            category = category_combo.get().strip()
            portions = portions_entry.get().strip()
            difficulty = difficulty_combo.get().strip()
            selected_image = image_path_var.get().strip()

            if not all([name, ingredients, instructions, cuisine_name, portions, difficulty]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return

            try:
                portions_int = int(portions)
            except ValueError:
                messagebox.showerror("Ошибка", "Порции должны быть числом")
                return

            cursor = None
            try:
                cursor = self.app.db_connection.cursor()

                # читаем все результаты и берём первый id
                cursor.execute("SELECT id FROM cuisines WHERE name = ?", (cuisine_name,))
                rows = cursor.fetchall()
                if not rows:
                    messagebox.showerror("Ошибка", "Выбранная кухня не найдена")
                    return
                cuisine_id = rows[0][0]

                final_category = (
                    category if category and category != 'Без категории'
                    else self.auto_categorize_recipe(name, description, "")
                )

                cursor.execute('''
                    UPDATE recipes 
                    SET name = ?, description = ?, ingredients = ?, instructions = ?, 
                        base_portions = ?, difficulty = ?, cuisine_id = ?, tags = ?, image_path = ?
                    WHERE id = ?
                ''', (name, description, ingredients, instructions, portions_int,
                      difficulty, cuisine_id, final_category, selected_image, recipe_id))

                self.app.db_connection.commit()

                messagebox.showinfo("Успех", "Рецепт успешно обновлен!")
                self.show_recipe_details(recipe_id)

            except Exception as e:
                try:
                    self.app.db_connection.rollback()
                except:
                    pass
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass

        # Кнопки
        btn_frame = ttk.Frame(self.app.current_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="💾 Сохранить", command=save_changes, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.app.get_text('back'), command=lambda: self.show_recipe_details(recipe_id), width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🏠 Главная", command=self.app.show_main_menu, width=15).pack(side='left', padx=5)

        load_cuisines()
        load_categories()
        if image_path_val:
            try:
                show_image_preview(image_path_val)
            except:
                pass

    # ------------------ ДОБАВЛЕНИЕ РЕЦЕПТА (с изображением) ------------------
    def add_recipe(self):
        """Добавление нового рецепта (с выбором изображения)"""
        self.app.draw_header()
        self.app.create_scrollable_frame(padding=25)

        ttk.Label(self.app.current_frame, text="➕ Добавить новый рецепт",
                  style='Title.TLabel').pack(pady=10)

        form_frame = ttk.Frame(self.app.current_frame)
        form_frame.pack(fill='x', pady=10)

        ttk.Label(form_frame, text="Название рецепта:").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky='w', pady=5)
        desc_entry = ttk.Entry(form_frame, width=40)
        desc_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Кухня:").grid(row=2, column=0, sticky='w', pady=5)
        cuisine_combo = ttk.Combobox(form_frame, width=37)
        cuisine_combo.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Категория:").grid(row=3, column=0, sticky='w', pady=5)
        category_combo = ttk.Combobox(form_frame, width=37)
        category_combo.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Ингредиенты (название|количество|ед.):").grid(row=4, column=0, sticky='nw', pady=5)
        ingredients_text = tk.Text(form_frame, width=40, height=5)
        ingredients_text.grid(row=4, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Инструкции:").grid(row=5, column=0, sticky='nw', pady=5)
        instructions_text = tk.Text(form_frame, width=40, height=5)
        instructions_text.grid(row=5, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Порции:").grid(row=6, column=0, sticky='w', pady=5)
        portions_entry = ttk.Entry(form_frame, width=10)
        portions_entry.insert(0, "1")
        portions_entry.grid(row=6, column=1, pady=5, padx=5, sticky='w')

        ttk.Label(form_frame, text="Сложность:").grid(row=7, column=0, sticky='w', pady=5)
        difficulty_combo = ttk.Combobox(form_frame, values=['легко', 'средне', 'сложно'], width=10)
        difficulty_combo.set('средне')
        difficulty_combo.grid(row=7, column=1, pady=5, padx=5, sticky='w')

        # (блок изображения при добавлении сейчас отключён — image_path = "" в save_recipe)

        def load_cuisines():
            cursor = None
            try:
                cursor = self.app.db_connection.cursor()
                cursor.execute("SELECT DISTINCT TRIM(name) FROM cuisines ORDER BY TRIM(name)")
                rows = cursor.fetchall()
                cuisines = []
                seen = set()
                for r in rows:
                    if not r:
                        continue
                    name = (r[0] or "").strip()
                    key = name.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    cuisines.append(name)
                cuisine_combo['values'] = cuisines
                if cuisines:
                    cuisine_combo.set(cuisines[0])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки кухонь: {e}")
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass

        def load_categories():
            categories = [
                'Без категории',
                'салат',
                'суп',
                'закуска',
                'основное блюдо',
                'десерт',
                'напиток'
            ]
            category_combo['values'] = categories
            category_combo.set('Без категории')

        def auto_detect_category(event=None):
            name = name_entry.get()
            if name:
                auto_category = self.auto_categorize_recipe(name)
                category_combo.set(auto_category)

        def save_recipe():
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            ingredients = ingredients_text.get("1.0", tk.END).strip()
            instructions = instructions_text.get("1.0", tk.END).strip()
            cuisine_name = cuisine_combo.get().strip()
            category = category_combo.get().strip()
            portions = portions_entry.get().strip()
            difficulty = difficulty_combo.get().strip()
            selected_image = ""  # image_path пустой

            if not all([name, ingredients, instructions, cuisine_name, portions, difficulty]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return

            try:
                portions_int = int(portions)
                if portions_int <= 0:
                    messagebox.showerror("Ошибка", "Количество порций должно быть больше 0")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Порции должны быть числом")
                return

            cursor = None
            try:
                cursor = self.app.db_connection.cursor()

                cursor.execute("SELECT id FROM cuisines WHERE name = ?", (cuisine_name,))
                rows = cursor.fetchall()
                if not rows:
                    messagebox.showerror("Ошибка", "Выбранная кухня не найдена")
                    return
                cuisine_id = rows[0][0]

                final_category = (
                    category if category and category != 'Без категории'
                    else self.auto_categorize_recipe(name, description, "")
                )

                recipe_data = (
                    name, description, ingredients, instructions, portions_int, difficulty,
                    cuisine_id, self.app.current_user['id'],
                    15, 30, 45, 300, None, None, None, final_category, selected_image
                )

                cursor.execute('''
                    INSERT INTO recipes 
                    (name, description, ingredients, instructions, base_portions, 
                     difficulty, cuisine_id, created_by, preparation_time, 
                     cooking_time, total_time, calories, proteins, fats, carbs, tags, image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', recipe_data)

                self.app.db_connection.commit()

                messagebox.showinfo("Успех", f"✅ Рецепт '{name}' успешно добавлен в базу данных!")
                self.app.show_main_menu()

            except Exception as e:
                try:
                    self.app.db_connection.rollback()
                except:
                    pass
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass

        btn_frame = ttk.Frame(self.app.current_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="💾 Сохранить", command=save_recipe, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.app.get_text('back'), command=self.app.show_main_menu, width=15).pack(side='left', padx=5)

        name_entry.bind('<KeyRelease>', auto_detect_category)

        load_cuisines()
        load_categories()

        try:
            self.app.fit_window_to_content()
        except:
            pass

    def manage_recipes(self):
        """Управление рецептами (для администраторов и шеф-поваров)"""
        self.show_recipe_catalog()





