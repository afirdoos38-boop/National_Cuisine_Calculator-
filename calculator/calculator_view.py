"""
calculator/calculator_view.py
Модуль калькулятора ингредиентов. Реализует логику пропорционального пересчета
продуктов в зависимости от количества порций и экспорт результатов в TXT.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog


class Calculator:
    def __init__(self, app):
        self.app = app
        self.current_selection = None  # текущий выбранный рецепт

    def show_calculator(self, pre_selected_recipe_id=None):
        """Калькулятор продуктов"""

        self.app.draw_header()
        self.app.create_scrollable_frame(padding=25)
        self.app.current_frame.help_tag = 'help_calc'

        ttk.Label(self.app.current_frame, text=self.app.get_text('menu_calc'),
                  style='Title.TLabel').pack(pady=10)

        # Выбор рецепта (Premium Grid Layout)
        select_frame = ttk.LabelFrame(self.app.current_frame, text=self.app.get_text('select_recipe_for_calc'), padding=15)
        select_frame.pack(fill='x', pady=10)
        
        select_frame.columnconfigure(0, weight=3)
        select_frame.columnconfigure(1, weight=1)

        # Левая часть: Список рецептов
        list_container = ttk.Frame(select_frame)
        list_container.grid(row=0, column=0, sticky='nsew', padx=5)
        
        ttk.Label(list_container, text=self.app.get_text('select_recipe'), font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=5)
        
        recipe_listbox = tk.Listbox(
            list_container,
            height=6,
            font=('Segoe UI', 10),
            selectbackground='#3498DB',
            selectforeground='white',
            borderwidth=1,
            relief='flat'
        )
        recipe_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=recipe_listbox.yview)
        recipe_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Правая часть: Порции
        portions_frame = ttk.Frame(select_frame)
        portions_frame.grid(row=0, column=1, sticky='n', padx=20)
        
        ttk.Label(portions_frame, text=self.app.get_text('portions_label'), font=('Segoe UI', 11, 'bold')).pack(pady=5)
        portions_entry = ttk.Entry(portions_frame, width=12, font=('Segoe UI', 12), justify='center')
        portions_entry.insert(0, "1") 
        portions_entry.pack(pady=5)

        # Таблица расчёта
        calc_frame = ttk.Frame(self.app.current_frame)
        calc_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns_keys = ['col_ingredient', 'col_quantity', 'col_unit', 'col_price_per_unit', 'col_total_cost']
        # Уменьшаем начальную высоту таблицы
        calc_tree = ttk.Treeview(calc_frame, columns=columns_keys, show='headings', height=6)

        s = getattr(self.app, 'ui_scale', 1.0)
        col_widths = [int(w * s) for w in [280, 110, 90, 140, 140]]
        for i, (key, width) in enumerate(zip(columns_keys, col_widths)):
            calc_tree.heading(key, text=self.app.get_text(key))
            # Все колонки теперь могут немного растягиваться для адаптивности
            calc_tree.column(key, width=width, anchor=tk.CENTER, stretch=True)

        v_scroll = ttk.Scrollbar(calc_frame, orient=tk.VERTICAL, command=calc_tree.yview)
        calc_tree.configure(yscrollcommand=v_scroll.set)

        calc_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')

        # Итоговая сумма
        total_frame = ttk.Frame(self.app.current_frame)
        total_frame.pack(fill='x', pady=10)

        total_label = ttk.Label(total_frame, text=self.app.get_text('total_cost_label').format(cost='0.00'),
                                font=('Arial', 12, 'bold'), foreground='green')
        total_label.pack()

        # Массив соответствия: индекс в Listbox -> ID рецепта
        recipe_ids = []

        # ========================= Внутренние функции ========================= #

        def on_recipe_select(event):
            """Сохраняем выбор рецепта"""
            selection = recipe_listbox.curselection()
            if selection:
                self.current_selection = selection[0]

        def load_recipes():
            """Загрузка списка рецептов и выделение нужного при необходимости"""
            nonlocal recipe_ids
            try:
                recipe_listbox.delete(0, tk.END)
                recipe_ids = []
                cursor = None
                try:
                    cursor = self.app.db_connection.cursor()
                    cursor.execute('''
                        SELECT 
                            r.id,
                            r.name,
                            COALESCE(c.name, 'Не указана') AS cuisine_name
                        FROM recipes r
                        LEFT JOIN cuisines c ON r.cuisine_id = c.id
                        ORDER BY r.name
                    ''')
                    recipes = cursor.fetchall()

                    selected_index = None
                    for i, (recipe_id, name, cuisine) in enumerate(recipes):
                        display_name = f"{name} ({cuisine})"
                        recipe_listbox.insert(tk.END, display_name)
                        recipe_ids.append(int(recipe_id))

                        # Если калькулятор открыт для конкретного рецепта
                        if pre_selected_recipe_id is not None and int(recipe_id) == pre_selected_recipe_id:
                            selected_index = i

                    if selected_index is not None:
                        recipe_listbox.selection_clear(0, tk.END)
                        recipe_listbox.selection_set(selected_index)
                        recipe_listbox.activate(selected_index)
                        recipe_listbox.see(selected_index)
                        recipe_listbox.focus_set()
                        self.current_selection = selected_index
                    elif self.current_selection is not None and self.current_selection < recipe_listbox.size():
                        recipe_listbox.selection_set(self.current_selection)
                        recipe_listbox.see(self.current_selection)

                finally:
                    if cursor:
                        try:
                            cursor.close()
                        except:
                            pass

            except Exception as e:
                messagebox.showerror(self.app.get_text('error'), f"{self.app.get_text('error_db')}: {e}")

        def restore_selection():
            """Восстановить выбор рецепта"""
            if self.current_selection is not None and self.current_selection < recipe_listbox.size():
                recipe_listbox.selection_set(self.current_selection)
                recipe_listbox.see(self.current_selection)

        def calculate_ingredients():
            """Расчёт стоимости ингредиентов"""
            restore_selection()

            if self.current_selection is None:
                messagebox.showwarning(self.app.get_text('warning'), self.app.get_text('select_recipe_for_calc'))
                return

            try:
                portions = int(portions_entry.get())
                if portions < 0:
                    messagebox.showerror(self.app.get_text('error'), self.app.get_text('portions_negative'))
                    return
            except ValueError:
                messagebox.showerror(self.app.get_text('error'), self.app.get_text('portions_invalid'))
                return

            for item in calc_tree.get_children():
                calc_tree.delete(item)

            cursor = None
            try:
                cursor = self.app.db_connection.cursor()

                # Берём настоящий ID рецепта по индексу в Listbox
                recipe_id = recipe_ids[self.current_selection]

                cursor.execute('''
                    SELECT ingredients, base_portions 
                    FROM recipes 
                    WHERE id = ?
                ''', (recipe_id,))

                result = cursor.fetchone()
                try:
                    cursor.fetchall()
                except Exception:
                    pass

                if not result:
                    messagebox.showerror(self.app.get_text('error'), self.app.get_text('recipe_not_found'))
                    return

                ingredients_text, base_portions = result

                if portions == 0:
                    total_label.config(text=self.app.get_text('total_cost_label').format(cost='0.00'))
                    return

                if base_portions == 0:
                    base_portions = 1

                coefficient = portions / base_portions
                total_cost = 0
                ingredients = ingredients_text.strip().split('\n') if ingredients_text else []

                for ingredient_line in ingredients:
                    if '|' in ingredient_line:
                        parts = ingredient_line.split('|')
                        if len(parts) >= 3:
                            name = parts[0].strip()
                            try:
                                base_quantity = float(parts[1].strip())
                                unit = parts[2].strip()

                                calculated_quantity = base_quantity * coefficient

                                sample_prices = {
                                    'говядина': 500, 'свинина': 400, 'курица': 300, 'рис': 100,
                                    'картофель': 50, 'морковь': 40, 'лук': 30, 'мука': 60,
                                    'яйца': 80, 'сметана': 120, 'сыр': 700, 'масло': 150,
                                    'бекон': 800, 'пармезан': 1200, 'сливки': 200, 'нори': 300,
                                    'крабовые': 400, 'авокадо': 200, 'огурец': 80, 'икра': 500,
                                    'томат': 120, 'перец': 90, 'чеснок': 200, 'грибы': 300,
                                    'лапша': 150, 'соус': 180, 'специи': 1000, 'зелень': 200
                                }

                                price_per_unit = 50
                                for key, price in sample_prices.items():
                                    if key in name.lower():
                                        price_per_unit = price
                                        break

                                if unit == 'шт':
                                    total_cost_ingredient = calculated_quantity * price_per_unit
                                else:
                                    total_cost_ingredient = (calculated_quantity / 1000) * price_per_unit

                                total_cost += total_cost_ingredient

                                calc_tree.insert('', tk.END, values=(
                                    name,
                                    f"{calculated_quantity:.2f}",
                                    unit,
                                    f"{price_per_unit} {self.app.get_text('currency')}/{'шт' if unit == 'шт' else 'кг'}",
                                    f"{total_cost_ingredient:.2f} {self.app.get_text('currency')}"
                                ))

                            except ValueError:
                                continue

                total_label.config(text=self.app.get_text('total_cost_label').format(cost=f"{total_cost:.2f}"))

            except Exception as e:
                messagebox.showerror(self.app.get_text('error'), f"{self.app.get_text('error_db')}: {e}")
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass

        def clear_calculation():
            """Очистить таблицу расчёта"""
            for item in calc_tree.get_children():
                calc_tree.delete(item)
            total_label.config(text=self.app.get_text('total_cost_label').format(cost='0.00'))
            restore_selection()

        def print_to_file():
            """Сохранение полного расчёта в файл"""
            restore_selection()

            if self.current_selection is None:
                messagebox.showwarning(self.app.get_text('warning'), self.app.get_text('select_recipe_for_print'))
                return

            selected_recipe = recipe_listbox.get(self.current_selection)
            portions = portions_entry.get()

            try:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[(self.app.get_text('text_files'), "*.txt")],
                    title=self.app.get_text('save_calculation_title')
                )
                if not file_path:
                    return

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"РЕЦЕПТ: {selected_recipe.split(' (')[0]}\n")
                    f.write(f"Количество порций: {portions}\n\n")
                    f.write("ИНГРЕДИЕНТЫ:\n")

                    for item in calc_tree.get_children():
                        values = calc_tree.item(item)['values']
                        f.write(f"- {values[0]} | {values[1]} {values[2]} | {values[3]} | {values[4]}\n")

                    f.write(f"\n{total_label.cget('text')}\n")

                messagebox.showinfo(self.app.get_text('done'), self.app.get_text('file_saved').format(path=file_path))

            except Exception as e:
                messagebox.showerror(self.app.get_text('error'), f"{self.app.get_text('error_db')}: {e}")

        # ==================================================================== #

        recipe_listbox.bind('<<ListboxSelect>>', on_recipe_select)
        portions_entry.bind('<FocusOut>', lambda e: restore_selection())

        # Кнопки
        buttons_frame = ttk.Frame(self.app.current_frame)
        buttons_frame.pack(pady=20, fill='x', side=tk.BOTTOM)

        ttk.Button(buttons_frame, text=self.app.get_text('calculate_btn'), command=calculate_ingredients,
                   style='Accent.TButton', width=22).pack(side='left', padx=5, expand=True)

        ttk.Button(buttons_frame, text=self.app.get_text('delete_btn'), command=clear_calculation,
                   width=20).pack(side='left', padx=5, expand=True)

        ttk.Button(buttons_frame, text=self.app.get_text('menu_catalog'), command=self.app.show_recipe_catalog,
                   width=20).pack(side='left', padx=5, expand=True)

        ttk.Button(buttons_frame, text=self.app.get_text('print'), command=print_to_file,
                   style='Secondary.TButton', width=20).pack(side='left', padx=5, expand=True)

        ttk.Button(buttons_frame, text=self.app.get_text('main_menu_btn'), command=self.app.show_main_menu,
                   width=22).pack(side='left', padx=5, expand=True)

        load_recipes()
        self.app.root.update()
        try:
            self.app.fit_window_to_content()
        except:
            pass

    def show_calculator_for_recipe(self, recipe_id):
        """Показать калькулятор для конкретного рецепта"""
        self.show_calculator(recipe_id)



