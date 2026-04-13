"""
cuisines/cuisines_view.py
Справочный модуль мировых национальных кухонь. Отображает список доступных
кухонь с описанием и количеством связанных рецептов.
"""
import tkinter as tk
from tkinter import ttk, messagebox

# Список 15 мировых кухонь, который используется и в статистике
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


class Cuisines:
    def __init__(self, app):
        self.app = app

    def show_cuisines(self):
        """Показать мировые кухни (15 выбранных кухонь)."""
        self.app.draw_header()
        self.app.create_scrollable_frame(padding=25)
        self.app.current_frame.help_tag = 'help_cuisines'

        ttk.Label(
            self.app.current_frame,
            text=self.app.get_text('menu_cuisines'),
            style='Title.TLabel'
        ).pack(pady=10)

        try:
            cursor = self.app.db_connection.cursor()

            cuisines_list = CUISINES_LIST
            placeholders = ','.join(['?'] * len(cuisines_list))

            # ВАЖНО: группируем по имени кухни, а не по id.
            # Так все рецепты для одинаковых названий суммируются вместе,
            # даже если в таблице cuisines несколько строк с одним и тем же name.
            cursor.execute(f'''
                SELECT
                    TRIM(c.name) as cuisine_name,
                    MAX(c.country) AS country,
                    MAX(c.description) AS description,
                    COUNT(r.id) AS recipe_count
                FROM cuisines c
                LEFT JOIN recipes r ON c.id = r.cuisine_id
                WHERE TRIM(c.name) IN ({placeholders})
                GROUP BY TRIM(c.name)
            ''', cuisines_list)

            # словарь: ключ = имя кухни, значение = (name, country, description, recipe_count)
            all_cuisines = {row[0]: row for row in cursor.fetchall()}

            # упорядочиваем в том же порядке, что и в CUISINES_LIST
            cuisines = [
                all_cuisines[name]
                for name in cuisines_list
                if name in all_cuisines
            ]

            cursor.close()

            # Создаем отдельный контейнер для сетки карточек, чтобы не было конфликта pack/grid
            cards_container = ttk.Frame(self.app.current_frame)
            cards_container.pack(fill='both', expand=True, padx=10, pady=10)

            # (Удалено ручное создание скролла, теперь используется create_scrollable_frame)
            scrollable_frame = cards_container
            canvas = self.app.main_scroll_container.canvas
            container = self.app.main_scroll_container

            card_frames = []
            for name, country, description, recipe_count in cuisines:
                card = ttk.LabelFrame(
                    scrollable_frame,
                    text=f"🍽️ {name} - {country}",
                    padding=10
                )

                ttk.Label(
                    card,
                    text=description or '',
                    wraplength=320
                ).pack(anchor='w', fill='x')

                ttk.Label(
                    card,
                    text=f"📋 Рецептов: {recipe_count}",
                    font=('Arial', 10),
                    foreground='green'
                ).pack(anchor='w', pady=4)

                def show_cuisine_recipes(cuisine_name=name):
                    self.show_recipes_by_cuisine(cuisine_name)

                ttk.Button(
                    card,
                    text=self.app.get_text('show_recipes_btn'),
                    command=show_cuisine_recipes,
                    width=20
                ).pack(anchor='e', pady=6)

                card_frames.append(card)

            def arrange_items(event=None):
                """Расположить карточки кухонь в несколько колонок при изменении ширины."""
                try:
                    canvas_width = canvas.winfo_width() or container.winfo_width() or 800
                    card_min_w = 340
                    cols = max(1, canvas_width // card_min_w)

                    for child in scrollable_frame.grid_slaves():
                        child.grid_forget()

                    for idx, card in enumerate(card_frames):
                        r = idx // cols
                        c = idx % cols
                        card.grid(
                            row=r,
                            column=c,
                            padx=10,
                            pady=10,
                            sticky='nsew'
                        )

                    for c in range(cols):
                        scrollable_frame.grid_columnconfigure(c, weight=1)

                    scrollable_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                except Exception:
                    pass

            canvas.bind("<Configure>", arrange_items)
            arrange_items()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки кухонь: {e}")

        ttk.Button(
            self.app.current_frame,
            text=self.app.get_text('back'),
            command=self.app.show_main_menu,
            style='Secondary.TButton'
        ).pack(pady=10)

        try:
            self.app.fit_window_to_content()
        except Exception:
            pass

    def show_recipes_by_cuisine(self, cuisine_name):
        """Показать рецепты по выбранной кухне."""
        self.app.draw_header()
        self.app.create_scrollable_frame(padding=25)

        ttk.Label(
            self.app.current_frame,
            text=f"📋 Рецепты {cuisine_name}",
            style='Title.TLabel'
        ).pack(pady=10)

        tree_frame = ttk.Frame(self.app.current_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ('ID', 'Название', 'Порции', 'Время', 'Сложность', 'Калории')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)

        col_widths = [50, 300, 80, 80, 100, 80]
        for col, width in zip(columns, col_widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor=tk.CENTER)

        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=v_scroll.set)

        tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')

        try:
            cursor = self.app.db_connection.cursor()
            cursor.execute('''
                SELECT r.id, r.name, r.base_portions, r.total_time,
                       r.difficulty, r.calories
                FROM recipes r 
                JOIN cuisines c ON r.cuisine_id = c.id
                WHERE c.name = ?
                ORDER BY r.name
            ''', (cuisine_name,))

            for row in cursor.fetchall():
                tree.insert('', tk.END, values=row)

            cursor.close()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки рецептов: {e}")

        def show_recipe():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                recipe_id = item['values'][0]
                # предполагаем, что в app есть метод show_recipe_details
                self.app.show_recipe_details(recipe_id)

        btn_frame = ttk.Frame(self.app.current_frame)
        btn_frame.pack(pady=10)

        ttk.Button(
            btn_frame,
            text=self.app.get_text('view_details'),
            command=show_recipe
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text=self.app.get_text('menu_cuisines'),
            command=self.show_cuisines
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text=self.app.get_text('main_menu_btn'),
            command=self.app.show_main_menu,
            style='Accent.TButton'
        ).pack(side='left', padx=5)

        try:
            self.app.fit_window_to_content()
        except Exception:
            pass


