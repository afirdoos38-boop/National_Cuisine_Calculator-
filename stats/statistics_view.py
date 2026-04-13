"""
stats/statistics_view.py
Модуль формирования статистических отчетов. Включает агрегацию данных по кухням,
видам блюд и калорийности, а также функции экспорта рецептов в текстовые файлы.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class Statistics:
    def __init__(self, app):
        self.app = app
        self.last_hovered_item = None

    # ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ "САЛАТОВ" ---------- #

    def _salad_like_terms(self):
        """Шаблоны для поиска салатов (рус/англ)."""
        return ['%салат%', '%salad%']

    def build_salad_clause(self, alias: str):
        """
        Возвращает (clause_sql, params) — условие для поиска салатов
        по полям tags и name таблицы alias.
        """
        terms = self._salad_like_terms()
        fields = [
            f"LOWER(COALESCE({alias}.tags, ''))",
            f"LOWER(COALESCE({alias}.name, ''))"
        ]
        parts = []
        params = []
        for field in fields:
            for term in terms:
                parts.append(f"{field} LIKE ?")
                params.append(term)
        clause = '(' + ' OR '.join(parts) + ')'
        return clause, params

    # ---------- ОСНОВНОЙ ЭКРАН СТАТИСТИКИ ---------- #

    def show_statistics(self):
        """Экран статистики администратора."""
        self.app.draw_header()
        self.app.create_scrollable_frame(padding=25)
        self.app.current_frame.help_tag = 'help_stats'

        # ----- Заголовок ----- #
        header_frame = ttk.Frame(self.app.current_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        ttk.Button(
            header_frame, text=self.app.get_text('main_menu_btn'),
            command=self.app.show_main_menu, width=15,
            style='Accent.TButton'
        ).pack(side='left', padx=5)
        ttk.Label(
            header_frame, text=self.app.get_text('menu_stats'),
            style='Title.TLabel'
        ).pack(side='left', padx=20)

        top_frame = ttk.Frame(self.app.current_frame)
        top_frame.pack(fill='x', pady=5)

        # ----- Левая часть – общие числа ----- #
        stats_frame = ttk.Frame(top_frame)
        stats_frame.pack(side='left', padx=5, fill='x', expand=True)

        try:
            cursor = self.app.db_connection.cursor()

            # Всего рецептов (15 кухонь, как в каталоге)
            cursor.execute("""
                SELECT COUNT(*)
                FROM recipes r
                JOIN cuisines c ON r.cuisine_id = c.id
                WHERE c.name IN (
                    'Русская кухня','Украинская кухня','Кавказская кухня','Итальянская кухня',
                    'Французская кухня','Азиатская кухня','Мексиканская кухня','Индийская кухня',
                    'Японская кухня','Китайская кухня','Тайская кухня','Греческая кухня',
                    'Испанская кухня','Турецкая кухня','Корейская кухня'
                )
            """)
            total_recipes = cursor.fetchone()[0]

            total_cuisines = 15  # фиксировано

            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            cursor.close()
        except Exception as e:
            messagebox.showerror(self.app.get_text('error'), f"{self.app.get_text('error_db')}: {e}")
            total_recipes = total_cuisines = total_users = 0

        ttk.Label(stats_frame, text=self.app.get_text('total_recipes_label').format(n=total_recipes)).pack(anchor='w')
        ttk.Label(stats_frame, text=self.app.get_text('total_cuisines_label').format(n=total_cuisines)).pack(anchor='w')
        ttk.Label(stats_frame, text=self.app.get_text('total_users_label').format(n=total_users)).pack(anchor='w')

        # ----- Правая часть – фильтры ----- #
        filter_frame = ttk.LabelFrame(top_frame, text=self.app.get_text('filters_title'), padding=8)
        filter_frame.pack(side='right', padx=5, fill='x')
        filter_frame.columnconfigure(1, weight=1)

        report_options = [self.app.get_text('report_by_cuisines'), self.app.get_text('report_by_types'), self.app.get_text('report_by_calories')]
        filter_mode_var = tk.StringVar(value=report_options[0])
        recipe_kind_var = tk.StringVar(value='all')

        ttk.Label(filter_frame, text=self.app.get_text('report_label')).grid(row=0, column=0, sticky='e', padx=4, pady=2)
        filter_mode_combo = ttk.Combobox(
            filter_frame, state='readonly', values=report_options,
            textvariable=filter_mode_var, width=25
        )
        filter_mode_combo.grid(row=0, column=1, sticky='we', padx=4, pady=2)

        cuisine_label = ttk.Label(filter_frame, text=self.app.get_text('cuisine_label'))
        cuisine_combo = ttk.Combobox(filter_frame, state='readonly', width=25)

        recipe_type_label = ttk.Label(filter_frame, text=self.app.get_text('stat_col_type'))
        recipe_type_combo = ttk.Combobox(filter_frame, state='readonly', width=25)

        cal_frame = ttk.Frame(filter_frame)
        ttk.Label(cal_frame, text=self.app.get_text('cal_from')).grid(row=0, column=0, padx=2)
        min_cal_entry = ttk.Entry(cal_frame, width=8)
        min_cal_entry.grid(row=0, column=1, padx=2)
        ttk.Label(cal_frame, text=self.app.get_text('cal_to')).grid(row=0, column=2, padx=2)
        max_cal_entry = ttk.Entry(cal_frame, width=8)
        max_cal_entry.grid(row=0, column=3, padx=2)

        ttk.Label(filter_frame, text=self.app.get_text('category_label')).grid(row=2, column=0, sticky='e', padx=4, pady=2)
        kind_frame = ttk.Frame(filter_frame)
        kind_frame.grid(row=2, column=1, sticky='w', padx=4, pady=2)

        ttk.Radiobutton(
            kind_frame, text=self.app.get_text('cat_all'), value='all', variable=recipe_kind_var,
            command=lambda: load_stats()
        ).pack(side='left', padx=(0, 4))
        ttk.Radiobutton(
            kind_frame, text=self.app.get_text('cat_dishes'), value='dish', variable=recipe_kind_var,
            command=lambda: load_stats()
        ).pack(side='left', padx=(0, 4))
        ttk.Radiobutton(
            kind_frame, text=self.app.get_text('cat_salads'), value='salad', variable=recipe_kind_var,
            command=lambda: load_stats()
        ).pack(side='left')

        # Кнопка печати
        buttons_under_filters = ttk.Frame(filter_frame)
        buttons_under_filters.grid(row=3, column=0, columnspan=2, sticky='e', pady=(6, 0))

        ttk.Button(
            buttons_under_filters, text=self.app.get_text('print_recipe_btn'),
            command=lambda: print_recipe(), width=22
        ).pack(side='left', padx=4)

        # ----- Таблицы ----- #
        table_frame = ttk.Frame(self.app.current_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        tree = ttk.Treeview(table_frame, show='headings', height=6)
        tree.column('#0', width=0, stretch=False)
        yscr = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=yscr.set)
        tree.pack(side='left', fill='both', expand=True)
        yscr.pack(side='right', fill='y')

        recipes_label = ttk.Label(
            self.app.current_frame,
            text=self.app.get_text('recipes_by_filter'),
            style='Subtitle.TLabel'
        )
        recipes_label.pack(pady=(6, 0))

        rec_frame = ttk.Frame(self.app.current_frame)
        rec_frame.pack(fill='both', expand=True, pady=(0, 10))

        rec_cols_keys = ['col_id', 'col_name', 'col_portions', 'col_time', 'col_difficulty', 'col_calories']
        rec_tree = ttk.Treeview(rec_frame, columns=rec_cols_keys, show='headings', height=6)
        for key, w in zip(rec_cols_keys, [60, 280, 80, 100, 120, 90]):
            rec_tree.heading(key, text=self.app.get_text(key))
            rec_tree.column(key, width=w, anchor=tk.CENTER, stretch=False)
        rec_tree.column('col_name', stretch=True, anchor=tk.W)

        rec_ysc = ttk.Scrollbar(rec_frame, orient='vertical', command=rec_tree.yview)
        rec_tree.configure(yscrollcommand=rec_ysc.set)
        rec_tree.pack(side='left', fill='both', expand=True)
        rec_ysc.pack(side='right', fill='y')

        # ---------- ВНУТРЕННИЕ ФУНКЦИИ ---------- #

        def dedupe_by_name(rows, name_index=1):
            """Удаляет повторы рецептов по названию (только в отображении)."""
            seen = set()
            result = []
            for r in rows:
                name = (r[name_index] or '').strip().lower()
                if name in seen:
                    continue
                seen.add(name)
                result.append(r)
            return result

        def configure_tree(columns):
            """Настройка колонок таблицы с защитой от ошибок индексации."""
            col_ids = [f'col{i}' for i in range(len(columns))]
            # Сначала сбрасываем отображаемые колонки, чтобы избежать ошибок индексации
            tree['displaycolumns'] = ()
            # Затем устанавливаем новые колонки
            tree['columns'] = col_ids
            tree['displaycolumns'] = col_ids
            
            for col_id, (heading, width, col_anchor) in zip(col_ids, columns):
                tree.heading(col_id, text=heading)
                tree.column(col_id, width=width, anchor=col_anchor, stretch=True)
            return col_ids

        def update_filter_visibility():
            cuisine_label.grid_remove()
            cuisine_combo.grid_remove()
            recipe_type_label.grid_remove()
            recipe_type_combo.grid_remove()
            cal_frame.grid_remove()

            mode = filter_mode_var.get()
            if mode == report_options[0]:
                cuisine_label.grid(row=1, column=0, sticky='e', padx=4, pady=2)
                cuisine_combo.grid(row=1, column=1, sticky='we', padx=4, pady=2)
            elif mode == report_options[1]:
                recipe_type_label.grid(row=1, column=0, sticky='e', padx=4, pady=2)
                recipe_type_combo.grid(row=1, column=1, sticky='we', padx=4, pady=2)
            else:
                cal_frame.grid(row=1, column=0, columnspan=2, sticky='we', padx=4, pady=2)

        def load_cuisine_list():
            names = [self.app.get_text('all_cuisines')]
            cursor = None
            try:
                cursor = self.app.db_connection.cursor()
                cursor.execute("""
                    SELECT DISTINCT TRIM(name) as cuisine_name 
                    FROM cuisines 
                    WHERE name IS NOT NULL 
                      AND TRIM(name) != ''
                    ORDER BY cuisine_name
                """)
                for row in cursor.fetchall():
                    cuisine_name = row[0]
                    if cuisine_name and (
                        'кухн' in cuisine_name.lower() or 'cuisine' in cuisine_name.lower()
                    ):
                        names.append(cuisine_name)
            except Exception as e:
                print(f"Error loading cuisines: {e}")
            finally:
                if cursor:
                    cursor.close()

            cuisine_combo['values'] = names
            cuisine_combo.set(names[0])

        def load_recipe_type_list():
            types = [self.app.get_text('all_types')]
            cursor = None
            try:
                cursor = self.app.db_connection.cursor()
                cursor.execute("""
                    SELECT DISTINCT TRIM(
                        CASE
                            WHEN tags IS NULL OR tags = '' THEN 'Без категории'
                            WHEN INSTR(tags, ',') > 0 THEN SUBSTR(tags, 1, INSTR(tags, ',') - 1)
                            ELSE tags
                        END
                    ) AS recipe_type
                    FROM recipes
                    ORDER BY recipe_type
                """)
                types.extend([row[0] for row in cursor.fetchall() if row[0]])
            except Exception:
                pass
            finally:
                if cursor:
                    cursor.close()
            recipe_type_combo['values'] = types
            recipe_type_combo.set(types[0])

        def open_calculator(recipe_id=None):
            try:
                if hasattr(self.app, "show_calculator") and callable(getattr(self.app, "show_calculator")):
                    self.app.show_calculator(recipe_id)
                    return
                calc_obj = getattr(self.app, "calculator", None)
                if calc_obj is not None and hasattr(calc_obj, "show_calculator"):
                    calc_obj.show_calculator(recipe_id)
                    return
                messagebox.showinfo(self.app.get_text('info'), self.app.get_text('calculator_unavailable'))
            except Exception as e:
                messagebox.showerror(self.app.get_text('error'), f"{self.app.get_text('error_db')}: {e}")

        def get_recipe_ingredients(recipe_id):
            """
            Читает ингредиенты из текстового поля recipes.ingredients.
            Возвращает список (name, quantity, unit).
            """
            try:
                cursor = self.app.db_connection.cursor()
                cursor.execute("""
                    SELECT ingredients, base_portions
                    FROM recipes
                    WHERE id = ?
                """, (recipe_id,))
                row = cursor.fetchone()
                cursor.close()

                if not row or not row[0]:
                    return []

                ingredients_text, base_portions = row

                lines = ingredients_text.strip().split('\n')
                result = []
                for line in lines:
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            name = parts[0].strip()
                            qty = parts[1].strip()
                            unit = parts[2].strip()
                            result.append((name, qty, unit))

                return result

            except Exception as e:
                print(f"Error getting ingredients: {e}")
                return []

        def export_recipe_to_text(recipe_id):
            """Сохранить выбранный рецепт в текстовый файл (аккуратно, с общей ценой в конце)."""
            try:
                cursor = self.app.db_connection.cursor()
                cursor.execute("""
                    SELECT r.name, r.description, r.base_portions, r.total_time, 
                           r.difficulty, r.calories, r.instructions, r.tags,
                           COALESCE(c.name, 'Не указана') AS cuisine_name
                    FROM recipes r
                    LEFT JOIN cuisines c ON r.cuisine_id = c.id
                    WHERE r.id = ?
                """, (recipe_id,))
                recipe = cursor.fetchone()
                cursor.close()

                if not recipe:
                    messagebox.showerror(self.app.get_text('error'), self.app.get_text('recipe_not_found'))
                    return

                ingredients = get_recipe_ingredients(recipe_id)

                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[(self.app.get_text('text_files'), "*.txt")],
                    title=self.app.get_text('save_recipe_to_file')
                )
                if not file_path:
                    return

                # Примерный справочник цен
                sample_prices = {
                    'говядина': 500, 'свинина': 400, 'курица': 300, 'рис': 100,
                    'картофель': 50, 'морковь': 40, 'лук': 30, 'мука': 60,
                    'яйца': 80, 'сметана': 120, 'сыр': 700, 'масло': 150,
                    'бекон': 800, 'пармезан': 1200, 'сливки': 200, 'нори': 300,
                    'крабовые': 400, 'авокадо': 200, 'огурец': 80, 'икра': 500,
                    'томат': 120, 'перец': 90, 'чеснок': 200, 'грибы': 300,
                    'лапша': 150, 'соус': 180, 'специи': 1000, 'зелень': 200
                }

                (name, description, base_portions, total_time,
                 difficulty, calories, instructions, tags, cuisine_name) = recipe

                total_cost = 0.0

                with open(file_path, "w", encoding="utf-8") as f:
                    # Заголовок
                    f.write(f"РЕЦЕПТ: {name}\n")
                    f.write(f"Кухня: {cuisine_name}\n")
                    f.write(f"Базовое количество порций: {base_portions}\n")
                    f.write(f"Общее время приготовления: {total_time} мин\n")
                    f.write(f"Сложность: {difficulty}\n")
                    f.write(f"Калории: {calories}\n")
                    if tags:
                        f.write(f"Теги: {tags}\n")
                    f.write("\n")

                    # Описание
                    if description:
                        f.write("ОПИСАНИЕ:\n")
                        f.write(description.strip() + "\n\n")

                    # Ингредиенты (بدون أسعار في السطور)
                    if ingredients:
                        f.write("ИНГРЕДИЕНТЫ:\n")
                        for ing_name, qty, unit in ingredients:
                            f.write(f"- {ing_name}: {qty} {unit}\n")

                            # حساب السعر الكلي فقط
                            try:
                                base_quantity = float(str(qty).replace(',', '.'))
                            except (TypeError, ValueError):
                                base_quantity = 0.0

                            price_per_unit = 50
                            lname = str(ing_name).lower()
                            for key, price in sample_prices.items():
                                if key in lname:
                                    price_per_unit = price
                                    break

                            if unit == 'шт':
                                cost = base_quantity * price_per_unit
                            else:
                                cost = (base_quantity / 1000.0) * price_per_unit

                            total_cost += cost

                        f.write("\n")

                    # سطر واحد في النهاية للسعر الكلي
                    if ingredients:
                        f.write(f"ОБЩАЯ СТОИМОСТЬ РЕЦЕПТА: {total_cost:.2f} руб\n\n")

                    # Инструкции
                    if instructions:
                        f.write("ИНСТРУКЦИИ ПО ПРИГОТОВЛЕНИЮ:\n")
                        f.write(instructions.strip() + "\n")

                messagebox.showinfo(self.app.get_text('done'), self.app.get_text('recipe_saved_to_file').format(path=file_path))

            except Exception as e:
                messagebox.showerror(self.app.get_text('error'), f"{self.app.get_text('error_db')}: {e}")

        def print_recipe():
            """Сохранить рецепт в файл и открыть калькулятор."""
            selected_item = rec_tree.selection()
            if not selected_item:
                messagebox.showinfo(self.app.get_text('info'), self.app.get_text('select_recipe_for_print'))
                return
            recipe_id = rec_tree.item(selected_item[0])['values'][0]

            export_recipe_to_text(recipe_id)
            open_calculator(recipe_id)

        def show_recipe_details(recipe_id, recipe_name):
            try:
                cursor = self.app.db_connection.cursor()
                cursor.execute("""
                    SELECT r.name, r.description, r.base_portions, r.total_time, 
                           r.difficulty, r.calories, r.instructions, r.tags,
                           c.name as cuisine_name
                    FROM recipes r
                    LEFT JOIN cuisines c ON r.cuisine_id = c.id
                    WHERE r.id = ?
                """, (recipe_id,))
                recipe_data = cursor.fetchone()
                ingredients = get_recipe_ingredients(recipe_id)
                cursor.close()

                if not recipe_data:
                    return

                details_window = tk.Toplevel(self.app.root)
                details_window.title(f"Детали рецепта: {recipe_data[0]}")
                details_window.geometry("700x800")
                details_window.transient(self.app.root)
                details_window.grab_set()

                main_frame = ttk.Frame(details_window, padding=15)
                main_frame.pack(fill=tk.BOTH, expand=True)

                title_label = ttk.Label(
                    main_frame, text=recipe_data[0],
                    font=('Arial', 16, 'bold')
                )
                title_label.pack(pady=(0, 10))

                if recipe_data[8]:
                    cuisine_label_loc = ttk.Label(
                        main_frame, text=f"Кухня: {recipe_data[8]}",
                        font=('Arial', 12)
                    )
                    cuisine_label_loc.pack(anchor='w', pady=(0, 5))

                info_frame = ttk.LabelFrame(main_frame, text="Основная информация", padding=10)
                info_frame.pack(fill='x', pady=10)

                info_grid = ttk.Frame(info_frame)
                info_grid.pack(fill='x')

                ttk.Label(info_grid, text=f"Порции: {recipe_data[2]}").grid(
                    row=0, column=0, sticky='w', padx=(0, 20)
                )
                ttk.Label(info_grid, text=f"Время: {recipe_data[3]} мин").grid(
                    row=0, column=1, sticky='w', padx=(0, 20)
                )
                ttk.Label(info_grid, text=f"Сложность: {recipe_data[4]}").grid(
                    row=0, column=2, sticky='w', padx=(0, 20)
                )
                ttk.Label(info_grid, text=f"Калории: {recipe_data[5]}").grid(
                    row=0, column=3, sticky='w'
                )

                if ingredients:
                    ingredients_frame = ttk.LabelFrame(main_frame, text="Ингредиенты", padding=10)
                    ingredients_frame.pack(fill='x', pady=10)

                    ing_tree = ttk.Treeview(
                        ingredients_frame,
                        columns=('Ингредиент', 'Количество', 'Единица'),
                        show='headings', height=6
                    )
                    ing_tree.heading('Ингредиент', text='Ингредиент')
                    ing_tree.heading('Количество', text='Количество')
                    ing_tree.heading('Единица', text='Единица')

                    ing_tree.column('Ингредиент', width=250, anchor=tk.W)
                    ing_tree.column('Количество', width=100, anchor=tk.CENTER)
                    ing_tree.column('Единица', width=100, anchor=tk.CENTER)

                    for ing in ingredients:
                        ing_tree.insert('', tk.END, values=ing)

                    ing_scroll = ttk.Scrollbar(
                        ingredients_frame, orient='vertical', command=ing_tree.yview
                    )
                    ing_tree.configure(yscrollcommand=ing_scroll.set)
                    ing_tree.pack(side='left', fill='both', expand=True)
                    ing_scroll.pack(side='right', fill='y')

                if recipe_data[1]:
                    desc_frame = ttk.LabelFrame(main_frame, text="Описание", padding=10)
                    desc_frame.pack(fill='x', pady=10)

                    desc_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, font=('Arial', 10))
                    desc_text.insert('1.0', recipe_data[1])
                    desc_text.config(state='disabled')
                    desc_scroll = ttk.Scrollbar(
                        desc_frame, orient='vertical', command=desc_text.yview
                    )
                    desc_text.configure(yscrollcommand=desc_scroll.set)
                    desc_text.pack(side='left', fill='both', expand=True)
                    desc_scroll.pack(side='right', fill='y')

                if recipe_data[6]:
                    instructions_frame = ttk.LabelFrame(
                        main_frame, text="Инструкции приготовления", padding=10
                    )
                    instructions_frame.pack(fill='both', expand=True, pady=10)

                    instructions_text = tk.Text(
                        instructions_frame, wrap=tk.WORD, font=('Arial', 10)
                    )
                    instructions_text.insert('1.0', recipe_data[6])
                    instructions_text.config(state='disabled')
                    instructions_scroll = ttk.Scrollbar(
                        instructions_frame, orient='vertical',
                        command=instructions_text.yview
                    )
                    instructions_text.configure(yscrollcommand=instructions_scroll.set)
                    instructions_text.pack(side='left', fill='both', expand=True)
                    instructions_scroll.pack(side='right', fill='y')

                close_btn = ttk.Button(
                    main_frame, text="Закрыть", command=details_window.destroy, width=15
                )
                close_btn.pack(pady=10)

            except Exception as e:
                print(f"Error showing recipe details: {e}")

        def open_recipe(event):
            selected_item = rec_tree.selection()
            if not selected_item:
                return

            recipe_id = rec_tree.item(selected_item[0])['values'][0]
            recipe_name = rec_tree.item(selected_item[0])['values'][1]
            try:
                if hasattr(self.app, "show_recipe") and callable(getattr(self.app, "show_recipe")):
                    self.app.show_recipe(recipe_id)
                    return
                if hasattr(self.app, "open_recipe_detail") and callable(getattr(self.app, "open_recipe_detail")):
                    self.app.open_recipe_detail(recipe_id)
                    return
                recipe_manager = getattr(self.app, "recipe_manager", None)
                if recipe_manager is not None:
                    if hasattr(recipe_manager, "show_recipe") and callable(getattr(recipe_manager, "show_recipe")):
                        recipe_manager.show_recipe(recipe_id)
                        return
                    elif hasattr(recipe_manager, "open_recipe") and callable(getattr(recipe_manager, "open_recipe")):
                        recipe_manager.open_recipe(recipe_id)
                        return
                show_recipe_details(recipe_id, recipe_name)
            except Exception:
                show_recipe_details(recipe_id, recipe_name)

        def load_recipes_for_cuisine(cuisine_name, kind='all'):
            """Нижняя таблица: рецепты выбранной кухни, без повторов."""
            cursor = None
            try:
                cursor = self.app.db_connection.cursor()
                query = """
                    SELECT r.id, r.name, r.base_portions, r.total_time, r.difficulty, r.calories
                    FROM recipes r
                    LEFT JOIN cuisines c ON r.cuisine_id = c.id
                    WHERE COALESCE(c.name, 'Не указана') = ?
                """
                params = [cuisine_name]

                if kind == 'salad':
                    clause, clause_params = self.build_salad_clause('r')
                    query += f" AND {clause}"
                    params.extend(clause_params)
                elif kind == 'dish':
                    clause, clause_params = self.build_salad_clause('r')
                    query += f" AND NOT {clause}"
                    params.extend(clause_params)

                query += " ORDER BY r.name"
                cursor.execute(query, tuple(params))

                rows = cursor.fetchall()
                rows = dedupe_by_name(rows, name_index=1)

                rec_tree.delete(*rec_tree.get_children())
                for row in rows:
                    rec_tree.insert('', tk.END, values=row)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки рецептов: {str(e)}")
            finally:
                if cursor:
                    cursor.close()

        def load_stats():
            """Верхняя таблица: агрегированная статистика / список рецептов."""
            mode = filter_mode_var.get()
            kind = recipe_kind_var.get()
            cursor = None
            try:
                cursor = self.app.db_connection.cursor()

                # ---------- По кухням ---------- #
                if mode == report_options[0]:
                    configure_tree([
                        ('Кухня', 200, tk.W),
                        ('Кол-во', 80, tk.CENTER),
                        ('Avg калории', 120, tk.CENTER),
                        ('Avg время (мин)', 140, tk.CENTER),
                    ])
                    query = """
                        SELECT 
                            COALESCE(c.name, 'Не указана') AS cuisine_name,
                            COUNT(r.id) AS cnt,
                            COALESCE(AVG(r.calories), 0) AS avg_cal,
                            COALESCE(AVG(r.total_time), 0) AS avg_time
                        FROM recipes r
                        LEFT JOIN cuisines c ON r.cuisine_id = c.id
                    """
                    conditions = []
                    params = []

                    if kind == 'salad':
                        clause, clause_params = self.build_salad_clause('r')
                        conditions.append(clause)
                        params.extend(clause_params)
                    elif kind == 'dish':
                        clause, clause_params = self.build_salad_clause('r')
                        conditions.append(f"NOT {clause}")
                        params.extend(clause_params)

                    cuisine_val = cuisine_combo.get()
                    if cuisine_val and cuisine_val != 'Все кухни':
                        conditions.append('COALESCE(c.name, "Не указана") = ?')
                        params.append(cuisine_val)

                    if conditions:
                        query += ' WHERE ' + ' AND '.join(conditions)
                    query += ' GROUP BY cuisine_name ORDER BY cnt DESC'

                # ---------- По видам рецептов ---------- #
                elif mode == report_options[1]:
                    configure_tree([
                        ('Вид рецепта', 220, tk.W),
                        ('Кол-во', 80, tk.CENTER),
                        ('Avg калории', 120, tk.CENTER),
                        ('Avg время (мин)', 140, tk.CENTER),
                    ])
                    type_expr = (
                        "TRIM(CASE WHEN r.tags IS NULL OR r.tags = '' THEN 'Без категории' "
                        "ELSE (CASE WHEN INSTR(tags, ',') > 0 THEN SUBSTR(tags, 1, INSTR(tags, ',') - 1) ELSE tags END) END)"
                    )
                    query = f"""
                        SELECT {type_expr} AS recipe_type,
                               COUNT(r.id) AS cnt,
                               COALESCE(AVG(r.calories), 0) AS avg_cal,
                               COALESCE(AVG(r.total_time), 0) AS avg_time
                        FROM recipes r
                        LEFT JOIN cuisines c ON r.cuisine_id = c.id
                    """
                    conditions = []
                    params = []

                    if kind == 'salad':
                        clause, clause_params = self.build_salad_clause('r')
                        conditions.append(clause)
                        params.extend(clause_params)
                    elif kind == 'dish':
                        clause, clause_params = self.build_salad_clause('r')
                        conditions.append(f"NOT {clause}")
                        params.extend(clause_params)

                    recipe_type_val = recipe_type_combo.get()
                    if recipe_type_val and recipe_type_val != 'Все виды':
                        conditions.append(f"{type_expr} = ?")
                        params.append(recipe_type_val)

                    if conditions:
                        query += ' WHERE ' + ' AND '.join(conditions)
                    query += ' GROUP BY recipe_type ORDER BY cnt DESC'

                # ---------- По калориям ---------- #
                else:
                    configure_tree([
                        ('ID', 70, tk.CENTER),
                        ('Название', 250, tk.W),
                        ('Кухня', 200, tk.W),
                        ('Калории', 100, tk.CENTER),
                        ('Время (мин)', 120, tk.CENTER),
                    ])
                    query = """
                        SELECT 
                            r.id,
                            r.name,
                            COALESCE(c.name, 'Не указана') AS cuisine_name,
                            COALESCE(r.calories, 0) AS calories,
                            COALESCE(r.total_time, 0) AS total_time
                        FROM recipes r
                        LEFT JOIN cuisines c ON r.cuisine_id = c.id
                    """
                    conditions = []
                    params = []

                    min_cal = min_cal_entry.get().strip()
                    max_cal = max_cal_entry.get().strip()

                    if min_cal:
                        try:
                            min_val = int(min_cal)
                            conditions.append('COALESCE(r.calories, 0) >= ?')
                            params.append(min_val)
                        except ValueError:
                            messagebox.showerror("Ошибка", "Минимальные калории должны быть числом")
                            return

                    if max_cal:
                        try:
                            max_val = int(max_cal)
                            conditions.append('COALESCE(r.calories, 0) <= ?')
                            params.append(max_val)
                        except ValueError:
                            messagebox.showerror("Ошибка", "Максимальные калории должны быть числом")
                            return

                    if kind == 'salad':
                        clause, clause_params = self.build_salad_clause('r')
                        conditions.append(clause)
                        params.extend(clause_params)
                    elif kind == 'dish':
                        clause, clause_params = self.build_salad_clause('r')
                        conditions.append(f"NOT {clause}")
                        params.extend(clause_params)

                    if conditions:
                        query += ' WHERE ' + ' AND '.join(conditions)
                    query += ' ORDER BY COALESCE(r.calories, 0) DESC, r.name'

                params = locals().get('params', [])
                if params:
                    cursor.execute(query, tuple(params))
                else:
                    cursor.execute(query)

                rows = cursor.fetchall()

                tree.delete(*tree.get_children())

                if mode == 'По калориям':
                    rows = dedupe_by_name(rows, name_index=1)
                    for rid, name, cuisine_name, calories, total_time in rows:
                        tree.insert('', tk.END, values=(
                            rid,
                            name,
                            cuisine_name,
                            calories if calories and calories > 0 else '-',
                            total_time if total_time and total_time > 0 else '-'
                        ))
                else:
                    for label, cnt, avg_cal, avg_time in rows:
                        tree.insert('', tk.END, values=(
                            label,
                            cnt,
                            f"{avg_cal:.0f}" if avg_cal and avg_cal > 0 else '-',
                            f"{avg_time:.0f}" if avg_time and avg_time > 0 else '-'
                        ))

                if mode == report_options[0]:
                    cuisine_val = cuisine_combo.get()
                    if cuisine_val and cuisine_val != 'Все кухни':
                        load_recipes_for_cuisine(cuisine_val, kind)
                    else:
                        rec_tree.delete(*rec_tree.get_children())
                else:
                    load_recipes_for_selected()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки статистики: {str(e)}")
            finally:
                if cursor:
                    cursor.close()

        def load_recipes_for_selected(event=None, item_id=None):
            """
            Нижняя таблица:
            - По кухням      -> рецепты выбранной кухни
            - По видам       -> рецепты выбранного вида
            - По калориям    -> все рецепты, подходящие под текущий фильтр
            VS - Вызывается также при наведении (hover).
            """
            rec_tree.delete(*rec_tree.get_children())

            mode = filter_mode_var.get()
            kind = recipe_kind_var.get()
            cursor = None
            try:
                cursor = self.app.db_connection.cursor()

                if mode == report_options[0] or mode == report_options[1]:
                    # Если передан item_id (от hover) - используем его, иначе из выделения
                    sel_item = item_id if item_id else (tree.selection()[0] if tree.selection() else None)
                    if not sel_item:
                        return
                    
                    # Получаем значение категории (кухня или вид)
                    category_val = tree.item(sel_item)['values'][0]
                    
                    if mode == report_options[0]: # По кухням
                        cuisine_name = category_val
                    query = """
                        SELECT r.id, r.name, r.base_portions, r.total_time,
                               r.difficulty, r.calories
                        FROM recipes r
                        LEFT JOIN cuisines c ON r.cuisine_id = c.id
                        WHERE COALESCE(c.name, 'Не указана') = ?
                    """
                    params = [cuisine_name]

                    if kind == 'salad':
                        clause, clause_params = self.build_salad_clause('r')
                        query += f" AND {clause}"
                        params.extend(clause_params)
                    elif kind == 'dish':
                        clause, clause_params = self.build_salad_clause('r')
                        query += f" AND NOT {clause}"
                        params.extend(clause_params)

                    query += " ORDER BY r.name"

                elif mode == report_options[1]:
                    recipe_type = category_val
                    type_expr = (
                        "TRIM(CASE WHEN r.tags IS NULL OR r.tags = '' "
                        "THEN 'Без категории' "
                        "ELSE (CASE WHEN INSTR(r.tags, ',') > 0 THEN SUBSTR(r.tags, 1, INSTR(r.tags, ',') - 1) ELSE r.tags END) END)"
                    )
                    query = f"""
                        SELECT r.id, r.name, r.base_portions, r.total_time,
                               r.difficulty, r.calories
                        FROM recipes r
                        LEFT JOIN cuisines c ON r.cuisine_id = c.id
                        WHERE {type_expr} = ?
                    """
                    params = [recipe_type]

                    if kind == 'salad':
                        clause, clause_params = self.build_salad_clause('r')
                        query += f" AND {clause}"
                        params.extend(clause_params)
                    elif kind == 'dish':
                        clause, clause_params = self.build_salad_clause('r')
                        query += f" AND NOT {clause}"
                        params.extend(clause_params)

                    query += " ORDER BY r.name"

                else:
                    query = """
                        SELECT r.id, r.name, r.base_portions, r.total_time,
                               r.difficulty, r.calories
                        FROM recipes r
                        LEFT JOIN cuisines c ON r.cuisine_id = c.id
                    """
                    conditions = []
                    params = []

                    min_cal = min_cal_entry.get().strip()
                    max_cal = max_cal_entry.get().strip()

                    if min_cal:
                        try:
                            min_val = int(min_cal)
                            conditions.append('COALESCE(r.calories, 0) >= ?')
                            params.append(min_val)
                        except ValueError:
                            return

                    if max_cal:
                        try:
                            max_val = int(max_cal)
                            conditions.append('COALESCE(r.calories, 0) <= ?')
                            params.append(max_val)
                        except ValueError:
                            return

                    if kind == 'salad':
                        clause, clause_params = self.build_salad_clause('r')
                        conditions.append(clause)
                        params.extend(clause_params)
                    elif kind == 'dish':
                        clause, clause_params = self.build_salad_clause('r')
                        conditions.append(f"NOT {clause}")
                        params.extend(clause_params)

                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
                    query += " ORDER BY COALESCE(r.calories, 0) DESC, r.name"

                if params:
                    cursor.execute(query, tuple(params))
                else:
                    cursor.execute(query)

                rows = cursor.fetchall()
                rows = dedupe_by_name(rows, name_index=1)

                for row in rows:
                    rec_tree.insert('', tk.END, values=row)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки рецептов: {str(e)}")
            finally:
                if cursor:
                    cursor.close()

        # ----- بانو معاينة التفاصيل (Quick Preview Table) -----
        preview_frame = ttk.LabelFrame(self.app.current_frame, text=self.app.get_text('quick_preview'), padding=10)
        preview_frame.pack(fill='x', pady=(5, 10))

        # جدول ملخص البيانات (Table format for Stats)
        columns = ('name_val', 'cuisine_val', 'cal_val', 'time_val')
        preview_tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=1)
        preview_tree.pack(fill='x', pady=(0, 5))

        # تهيئة الأعمدة
        header_map = {
            'name_val': 'col_name',
            'cuisine_val': 'col_cuisine',
            'cal_val': 'col_calories',
            'time_val': 'col_time'
        }
        for col, key in header_map.items():
            preview_tree.heading(col, text=self.app.get_text(key))
            preview_tree.column(col, anchor='center', stretch=True)

        # Description (Larger box below the table)
        prev_label_desc = ttk.Label(preview_frame, text=self.app.get_text('description_label'), font=('Segoe UI', 10, 'bold'))
        prev_label_desc.pack(anchor='w', pady=(5, 0))
        
        preview_desc_text = tk.Text(preview_frame, height=5, wrap=tk.WORD, bg='#FDFEFE', font=('Segoe UI', 10), relief='groove', borderwidth=1)
        preview_desc_text.pack(fill='x', expand=True, pady=5)
        preview_desc_text.config(state='disabled')

        def update_recipe_preview(recipe_id):
            """جلب تفاصيل الوجبة وتحديث الجدول والوصف."""
            try:
                cursor = self.app.db_connection.cursor()
                cursor.execute("""
                    SELECT r.name, r.description, r.calories, r.total_time, c.name 
                    FROM recipes r 
                    LEFT JOIN cuisines c ON r.cuisine_id = c.id 
                    WHERE r.id = ?
                """, (recipe_id,))
                row = cursor.fetchone()
                cursor.close()
                
                if row:
                    name, desc, cal, time, cuisine = row
                    
                    # تحديث الجدول
                    preview_tree.delete(*preview_tree.get_children())
                    preview_tree.insert('', tk.END, values=(
                        name, 
                        cuisine if cuisine else "-", 
                        f"{cal} {self.app.get_text('unit_kcal')}", 
                        f"{time} {self.app.get_text('unit_min')}"
                    ))
                    
                    # تحديث الوصف
                    preview_desc_text.config(state='normal')
                    preview_desc_text.delete('1.0', tk.END)
                    preview_desc_text.insert('1.0', desc if desc else "-")
                    preview_desc_text.config(state='disabled')
            except Exception:
                pass

        btns = ttk.Frame(self.app.current_frame)
        btns.pack(fill='x', pady=6)
        ttk.Button(
            btns, text=self.app.get_text('back_to_main'),
            command=self.app.show_main_menu, width=25,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        # ----- Привязки ----- #
        filter_mode_combo.bind("<<ComboboxSelected>>", lambda event: (update_filter_visibility(), load_stats()))
        cuisine_combo.bind("<<ComboboxSelected>>", lambda event: load_stats())
        recipe_type_combo.bind("<<ComboboxSelected>>", lambda event: load_stats())
        min_cal_entry.bind('<Return>', lambda event: load_stats())
        max_cal_entry.bind('<Return>', lambda event: load_stats())

        tree.bind("<<TreeviewSelect>>", load_recipes_for_selected)
        
        self.last_hovered_recipe = None
        
        def on_mouse_hover(event):
            """Обновление нижней таблицы при наведении على الجدول العلوي."""
            item = tree.identify_row(event.y)
            if item and item != self.last_hovered_item:
                self.last_hovered_item = item
                load_recipes_for_selected(item_id=item)

        def on_recipe_hover(event):
            """تحديث شريط التفاصيل عند تمرير الماوس فوق وجبة في الجدول السفلي."""
            item = rec_tree.identify_row(event.y)
            if item and item != self.last_hovered_recipe:
                self.last_hovered_recipe = item
                vals = rec_tree.item(item)['values']
                if vals:
                    update_recipe_preview(vals[0])
        
        tree.bind("<Motion>", on_mouse_hover)
        rec_tree.bind("<Motion>", on_recipe_hover)
        rec_tree.bind("<Double-1>", open_recipe)

        # ----- Стартовая загрузка ----- #
        load_cuisine_list()
        load_recipe_type_list()
        update_filter_visibility()
        load_stats()

    # ---------- КРАТКАЯ СИСТЕМНАЯ СТАТИСТИКА ДЛЯ ГЛАВНОГО ЭКРАНА ---------- #

    def get_system_stats(self):
        """Возвращает агрегированную системную статистику."""
        try:
            cursor = self.app.db_connection.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM recipes r
                JOIN cuisines c ON r.cuisine_id = c.id
                WHERE c.name IN (
                    'Русская кухня','Украинская кухня','Кавказская кухня','Итальянская кухня',
                    'Французская кухня','Азиатская кухня','Мексиканская кухня','Индийская кухня',
                    'Японская кухня','Китайская кухня','Тайская кухня','Греческая кухня',
                    'Испанская кухня','Турецкая кухня','Корейская кухня'
                )
            """)
            recipes_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]

            cuisines_count = 15
            cursor.close()

            return {
                'recipes': recipes_count,
                'users': users_count,
                'cuisines': cuisines_count
            }
        except Exception as e:
            print(f"Ошибка получения системной статистики: {e}")
            return {'recipes': 0, 'users': 0, 'cuisines': 15}











