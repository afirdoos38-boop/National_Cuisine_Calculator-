import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class PersonalRecipes:
    def __init__(self, app):
        self.app = app

    def enable_copy_paste(self, widget):
        widget.bind("<Control-c>", lambda e: widget.event_generate("<<Copy>>"))
        widget.bind("<Control-v>", lambda e: widget.event_generate("<<Paste>>"))
        widget.bind("<Control-x>", lambda e: widget.event_generate("<<Cut>>"))

        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label=self.app.get_text('ctx_copy') if hasattr(self, 'app') else 'Копировать', command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Вставить", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_command(label="Вырезать", command=lambda: widget.event_generate("<<Cut>>"))
        widget.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def create_personal_recipe(self):
        """Создание персонального рецепта для пользователя"""
        self.app.create_scrollable_frame(padding=25)

        ttk.Label(
            self.app.current_frame,
            text="📝 Создание персонального рецепта",
            style='Title.TLabel'
        ).pack(pady=10)

        # ---------- Поля формы ----------
        form_frame = ttk.Frame(self.app.current_frame)
        form_frame.pack(fill='x', pady=10)

        ttk.Label(form_frame, text=self.app.get_text('recipe_name_label')).grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, pady=5, padx=5)
        self.enable_copy_paste(name_entry)

        ttk.Label(form_frame, text=self.app.get_text('description_label')).grid(row=1, column=0, sticky='w', pady=5)
        desc_entry = ttk.Entry(form_frame, width=40)
        desc_entry.grid(row=1, column=1, pady=5, padx=5)
        self.enable_copy_paste(desc_entry)

        ttk.Label(form_frame, text=self.app.get_text('cuisine_label')).grid(row=2, column=0, sticky='w', pady=5)
        cuisine_combo = ttk.Combobox(form_frame, width=37)
        cuisine_combo.grid(row=2, column=1, pady=5, padx=5, sticky='w')

        ttk.Label(
            form_frame,
            text=self.app.get_text('ingredients_label')
        ).grid(row=3, column=0, sticky='nw', pady=5)
        ingredients_text = tk.Text(form_frame, width=40, height=5)
        ingredients_text.grid(row=3, column=1, pady=5, padx=5)
        self.enable_copy_paste(ingredients_text)

        ttk.Label(form_frame, text=self.app.get_text('instructions_label')).grid(row=4, column=0, sticky='nw', pady=5)
        instructions_text = tk.Text(form_frame, width=40, height=5)
        instructions_text.grid(row=4, column=1, pady=5, padx=5)
        self.enable_copy_paste(instructions_text)

        ttk.Label(form_frame, text=self.app.get_text('portions_field_label')).grid(row=5, column=0, sticky='w', pady=5)
        portions_entry = ttk.Entry(form_frame, width=10)
        portions_entry.insert(0, "1")   # القيمة الافتراضية 1 بدل 4
        portions_entry.grid(row=5, column=1, pady=5, padx=5, sticky='w')
        self.enable_copy_paste(portions_entry)

        ttk.Label(form_frame, text=self.app.get_text('difficulty_label')).grid(row=6, column=0, sticky='w', pady=5)
        difficulty_combo = ttk.Combobox(form_frame, values=['легко', 'средне', 'сложно'], width=10)
        difficulty_combo.set('средне')
        difficulty_combo.grid(row=6, column=1, pady=5, padx=5, sticky='w')
        self.enable_copy_paste(difficulty_combo)

        # ---------- Загрузка кухонь (без повторов, формат "<что-то> кухня") ----------
        try:
            cursor = self.app.db_connection.cursor()
            cursor.execute("SELECT name FROM cuisines ORDER BY name")
            rows = cursor.fetchall()
            cursor.close()

            cuisines = []
            seen_roots = set()

            for row in rows:
                if not row or not row[0]:
                    continue

                full_name = row[0].strip()          # например: "Греческая кухня (Крит)"
                if not full_name:
                    continue

                # часть до скобок: "Греческая кухня (Крит)" -> "Греческая кухня"
                base = full_name.split('(')[0].strip()

                # убираем "кухня/кухни", получаем корень: "Греческая кухня" -> "Греческая"
                root = base.replace('кухня', '').replace('кухни', '').strip()
                if not root:
                    continue

                key = root.lower()
                if key in seen_roots:
                    # уже добавляли такой тип кухни
                    continue

                seen_roots.add(key)

                # отображаем всегда в виде "<root> кухня": "Греческая кухня"
                display_name = f"{root} кухня"
                cuisines.append(display_name)

            cuisine_combo['values'] = cuisines
            if cuisines:
                cuisine_combo.set(cuisines[0])

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки кухонь: {e}")

        # ---------- Сохранение рецепта ----------
        def save_personal_recipe():
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            cuisine_name = cuisine_combo.get().strip()
            ingredients = ingredients_text.get("1.0", tk.END).strip()
            instructions = instructions_text.get("1.0", tk.END).strip()
            portions = portions_entry.get().strip()
            difficulty = difficulty_combo.get().strip()

            if not all([name, ingredients, instructions, portions, difficulty, cuisine_name]):
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
                # 1. курсор
                cursor = self.app.db_connection.cursor()

                # 2. текущий пользователь
                current_user_id = self.app.current_user['id']

                # 3. Находим id кухни (в БД может быть "Греческая кухня (Крит)")
                cursor.execute(
                    "SELECT id FROM cuisines WHERE name LIKE ? ORDER BY id LIMIT 1",
                    (cuisine_name + '%',)
                )
                cuisine_result = cursor.fetchone()
                if not cuisine_result:
                    messagebox.showerror("Ошибка", "Выбранная кухня не найдена")
                    cursor.close()
                    return
                cuisine_id = cuisine_result[0]

                # 4. Данные рецепта (tags = 'персональный', image_path = '')
                personal_tag = "персональный"

                recipe_data = (
                    name,              # name
                    description,       # description
                    ingredients,       # ingredients
                    instructions,      # instructions
                    portions_int,      # base_portions
                    difficulty,        # difficulty
                    cuisine_id,        # cuisine_id
                    current_user_id,   # created_by
                    15,                # preparation_time
                    30,                # cooking_time
                    45,                # total_time
                    300,               # calories
                    None,              # proteins
                    None,              # fats
                    None,              # carbs
                    personal_tag,      # tags (персональный рецепт)
                    ""                 # image_path
                )

                cursor.execute('''
                    INSERT INTO recipes (
                        name, description, ingredients, instructions,
                        base_portions, difficulty, cuisine_id, created_by,
                        preparation_time, cooking_time, total_time, calories,
                        proteins, fats, carbs, tags, image_path
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', recipe_data)

                self.app.db_connection.commit()
                cursor.close()

                # 5. Сохраняем текстовый файл
                recipe_content = f"""
🍽️ {name}

📖 Описание:
{description}

🏮 Кухня: {cuisine_name}

🛒 Ингредиенты:
{ingredients}

👨‍🍳 Инструкции:
{instructions}

📊 Информация:
• Порции: {portions_int}
• Сложность: {difficulty}
• Создано: {self.app.current_user['full_name']}
• Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
                filename = f"рецепт_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(recipe_content)

                messagebox.showinfo(
                    "Успех",
                    f"✅ Рецепт '{name}' успешно добавлен в базу данных!\n"
                    f"📁 Также сохранен в файл: {filename}"
                )

                self.app.show_main_menu()

            except Exception as e:
                try:
                    self.app.db_connection.rollback()
                except:
                    pass
                messagebox.showerror("Ошибка", f"Ошибка сохранения рецепта: {str(e)}")
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass

        def show_recipe_preview():
            """Предварительный просмотр рецепта"""
            name = name_entry.get() or "Название рецепта"
            description = desc_entry.get() or "Описание"
            cuisine = cuisine_combo.get() or "Кухня"
            ingredients = ingredients_text.get("1.0", tk.END).strip() or "Ингредиенты"
            instructions = instructions_text.get("1.0", tk.END).strip() or "Инструкции"
            portions_val = portions_entry.get() or "0"
            difficulty_val = difficulty_combo.get() or "не указана"

            preview_content = f"""
🍽️ {name}

📖 Описание:
{description}

🏮 Кухня: {cuisine}

🛒 Ингредиенты:
{ingredients}

👨‍🍳 Инструкции:
{instructions}

📊 Информация:
• Порции: {portions_val}
• Сложность: {difficulty_val}
"""
            messagebox.showinfo("Предварительный просмотр", preview_content)

        # ---------- Кнопки ----------
        btn_frame = ttk.Frame(self.app.current_frame)
        btn_frame.pack(pady=20)

        ttk.Button(
            btn_frame, text=self.app.get_text('preview_btn'),
            command=show_recipe_preview, width=15
        ).pack(side='left', padx=5)
        ttk.Button(
            btn_frame, text="💾 Сохранить и печать",
            command=save_personal_recipe, width=15
        ).pack(side='left', padx=5)
        ttk.Button(
            btn_frame, text=self.app.get_text('back'),
            command=self.app.show_main_menu, width=15
        ).pack(side='left', padx=5)

    def show_recipe_print(self, recipe_content, recipe_name):
        """Показать рецепт для печати"""
        self.app.create_scrollable_frame(padding=25)

        ttk.Label(
            self.app.current_frame,
            text=f"🍽️ {recipe_name}",
            style='Title.TLabel'
        ).pack(pady=10)

        recipe_text = tk.Text(self.app.current_frame, wrap=tk.WORD, font=('Arial', 11))
        recipe_text.pack(fill=tk.BOTH, expand=True, pady=10)
        recipe_text.insert('1.0', recipe_content)
        recipe_text.config(state='disabled')
        self.enable_copy_paste(recipe_text)

        btn_frame = ttk.Frame(self.app.current_frame)
        btn_frame.pack(pady=10)

        def print_recipe():
            try:
                filename = f"рецепт_{recipe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(recipe_content)
                messagebox.showinfo("Сохранено", f"Рецепт сохранен в файл: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

        ttk.Button(
            btn_frame, text="🖨️ Сохранить для печати",
            command=print_recipe, width=15
        ).pack(side='left', padx=5)
        ttk.Button(
            btn_frame, text="📝 Создать новый рецепт",
            command=self.create_personal_recipe, width=15
        ).pack(side='left', padx=5)
        ttk.Button(
            btn_frame, text="🏠 Главная",
            command=self.app.show_main_menu, width=15
        ).pack(side='left', padx=5)
