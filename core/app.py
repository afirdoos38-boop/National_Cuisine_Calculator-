"""
core/app.py
Главный контроллер приложения. Управляет навигацией, переключением языков,
стилями интерфейса и интеграцией модулей. Реализует навигационный стек (Breadcrumbs)
и глобальные горячие клавиши (F1, Esc).
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from sqlite3 import Error
import hashlib
from datetime import datetime

from recipes.recipe_management import RecipeManagement
from calculator.calculator_view import Calculator
from users.user_management import UserManagement
from recipes.personal_recipes import PersonalRecipes
from cuisines.cuisines_view import Cuisines
from stats.statistics_view import Statistics
from database.database import DatabaseManager
from core.translations import TRANSLATIONS


class NationalCuisineCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title(" Калькулятор продуктов для национальной кухни")
        # при старте открываем приложение в полноэкранном режиме (максимизированное окно)
        try:
            self.root.state('zoomed')
        except:
            # запасной вариант, если state('zoomed') не сработал
            try:
                self.root.attributes("-zoomed", True)
            except:
                pass

        self.current_user = None
        self.current_frame = None
        self.lang = 'ru'  # По умолчанию русский

        # Инициализация модулей
        self.recipe_mgmt = RecipeManagement(self)
        self.calculator = Calculator(self)
        self.user_mgmt = UserManagement(self)
        self.personal_recipes = PersonalRecipes(self)
        self.cuisines = Cuisines(self)
        self.statistics = Statistics(self)

        # Состояние навигации (Breadcrumbs)
        self.nav_stack = [] 

        # Стили
        self.setup_styles()

        # Подключение к базе данных
        self.db_manager = DatabaseManager(self)
        self.db_connection = self.db_manager.connect_to_database()
        
        # Настройка статус-бара (Requirement 7)
        self.status_bar = None
        
        if self.db_connection:
            self.db_manager.init_database()
            # Начинаем с рекламной заставки (Requirement 7)
            self.show_splash_screen()
        else:
            messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных SQLite")
            self.root.destroy()
            
        # Глобальные горячие клавиши (Requirement 5)
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<Escape>', lambda e: self.handle_escape())

    def setup_styles(self):
        """Настройка стилей с современным дизайном (Premium Look)"""
        style = ttk.Style()
        
        # Используем тему 'clam' для лучшей настройки
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        # Основные цвета палитры
        bg_main = "#ECF0F1"
        primary_color = "#2E86C1"
        accent_color = "#E67E22"
        text_color = "#1B2631"
        
        # Настройка фона для всех Frame
        style.configure('TFrame', background=bg_main)
        style.configure('TLabelframe', background=bg_main)
        style.configure('TLabelframe.Label', background=bg_main, foreground=primary_color, font=('Arial', 10, 'bold'))
        
        # Заголовки
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground=primary_color, background=bg_main)
        style.configure('Subtitle.TLabel', font=('Segoe UI', 14), foreground="#5D6D7E", background=bg_main)
        style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'), foreground=text_color, background="#D6EAF8")
        
        # Кнопки
        style.configure('TButton', font=('Segoe UI', 10), padding=6)
        
        # Акцентная кнопка (синяя)
        style.configure('Accent.TButton', font=('Segoe UI', 11, 'bold'), foreground="white", background=primary_color)
        style.map('Accent.TButton', background=[('active', '#21618C')])
        
        # Вторичная кнопка (оранжевая)
        style.configure('Secondary.TButton', font=('Segoe UI', 10, 'bold'), foreground="white", background=accent_color)
        style.map('Secondary.TButton', background=[('active', '#A04000')])
        
        # Кнопка удаления (красная)
        style.configure('Delete.TButton', font=('Segoe UI', 10, 'bold'), foreground="white", background='#C0392B')
        style.map('Delete.TButton', background=[('active', '#922B21')])
        
        # Поля ввода
        style.configure('TEntry', padding=5)
        
        # Настройка Treeview
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=25, background="#FFFFFF", fieldbackground="#FFFFFF")
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        # Настройка статус-бара
        style.configure('Status.TLabel', font=('Segoe UI', 9), background='#D5D8DC', foreground='#566573')
        
        # Настройка приложения
        self.root.configure(background=bg_main)

    def draw_status_bar(self):
        """Отрисовка строки подсказки горячих клавиш (Requirement 7)"""
        if self.status_bar:
            self.status_bar.destroy()
        
        self.status_bar = ttk.Frame(self.root, style='Status.TLabel')
        self.status_bar.pack(side='bottom', fill='x')
        
        hint_text = self.get_text('hotkey_hints')
        ttk.Label(self.status_bar, text=hint_text, style='Status.TLabel', padding=(10, 2)).pack(side='left')

    def show_splash_screen(self):
        """Рекламная заставка (Requirement 7)"""
        self.clear_window()
        
        splash_frame = ttk.Frame(self.root, padding=40)
        splash_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = splash_frame
        
        # Переключатель языка на заставке
        lang_frame = ttk.Frame(splash_frame)
        lang_frame.pack(anchor='ne')
        ttk.Button(lang_frame, text="RU", width=4, command=lambda: self.toggle_language('ru')).pack(side='left', padx=2)
        ttk.Button(lang_frame, text="AR", width=4, command=lambda: self.toggle_language('ar')).pack(side='left', padx=2)
        ttk.Button(lang_frame, text="EN", width=4, command=lambda: self.toggle_language('en')).pack(side='left', padx=2)
        
        # Стильный заголовок
        ttk.Label(splash_frame, text=self.get_text('app_title'), style='Title.TLabel').pack(pady=(50, 20))
        
        # Описание системы
        ttk.Label(splash_frame, text=self.get_text('splash_desc'), 
                  font=('Segoe UI', 12), justify='center', wraplength=500).pack(pady=10)
        
        # Информация об авторе
        author_frame = ttk.LabelFrame(splash_frame, text=self.get_text('splash_author_frame'), padding=20)
        author_frame.pack(pady=30)
        
        ttk.Label(author_frame, text=self.get_text('author_name'), font=('Segoe UI', 14, 'bold')).pack()
        ttk.Label(author_frame, text=self.get_text('author_group'), font=('Segoe UI', 11)).pack()
        
        # Кнопка входа
        ttk.Button(splash_frame, text=self.get_text('splash_start_btn'), style='Accent.TButton', 
                   command=self.show_login_screen, width=25).pack(pady=20)
        
        self.draw_status_bar()
        self.root.update()
        self.fit_window_to_content()

    def show_help(self):
        """Контекстно-зависимая помощь (Requirement 7, F1)"""
        # Определяем текст помощи на основе текущего состояния
        help_key = 'help_main'
        if not self.current_user:
            help_key = 'help_login'
        elif self.current_frame and hasattr(self.current_frame, 'help_tag'):
            help_key = self.current_frame.help_tag
            
        messagebox.showinfo("Справка (F1)", self.get_text(help_key))

    def handle_escape(self):
        """Обработка клавиши Esc (Requirement 5)"""
        if not self.current_user:
            return 
        
        # Если мы в главном меню - выход из аккаунта
        if len(self.nav_stack) <= 1:
            if messagebox.askyesno(self.get_text('exit_title'), self.get_text('exit_confirm')):
                self.show_login_screen()
        else:
            # Возврат на предыдущий уровень (Requirement 6)
            self.nav_stack.pop() # текущий
            prev = self.nav_stack.pop()
            func = prev[0]
            args = prev[2] if len(prev) > 2 else []
            kwargs = prev[3] if len(prev) > 3 else {}
            func(*args, **kwargs)

    def update_nav_stack(self, func, label_key, args=None, kwargs=None):
        """Обновление стека навигации для хлебных крошек (Requirement 6)"""
        args = args or []
        kwargs = kwargs or {}
        
        item = (func, label_key, args, kwargs)
        
        # Если функция уже есть в стеке (например, при переходе назад), ищем её позицию
        funcs_in_stack = [i[0] for i in self.nav_stack]
        if func in funcs_in_stack:
             new_stack = []
             for i in self.nav_stack:
                 new_stack.append(i)
                 if i[0] == func: break
             self.nav_stack = new_stack
             # Обновляем аргументы на актуальные (сохранение состояния)
             self.nav_stack[-1] = item
        else:
            self.nav_stack.append(item)


    def clear_window(self):
        """Очистка окна – безопасная версия"""
        # Очищаем хедер если он есть
        if hasattr(self, 'current_frame_header') and self.current_frame_header:
            try:
                self.current_frame_header.destroy()
            except:
                pass
            self.current_frame_header = None
            
        if self.current_frame:
            try:
                self.current_frame.destroy()
            except:
                pass
            self.current_frame = None

    def draw_header(self):
        """Отрисовка заголовка с информацией о пользователе и сменой языка."""
        if not self.current_user:
            return
            
        # Очищаем старый заголовок если он есть
        if hasattr(self, 'current_frame_header') and self.current_frame_header:
            try: self.current_frame_header.destroy()
            except: pass
            
        header_frame = ttk.Frame(self.root, style='Header.TLabel', padding=(15, 10))
        header_frame.pack(fill='x', side='top')
        self.current_frame_header = header_frame

        user_info = f"👤 {self.current_user['full_name']} | 🔑 {self.get_text('role_label')} {self.current_user['role'].upper()}"
        ttk.Label(header_frame, text=user_info, style='Header.TLabel').pack(side='left')
        
        # Переключатель языка
        lang_btn_frame = ttk.Frame(header_frame, style='Header.TLabel')
        lang_btn_frame.pack(side='right', padx=20)
        ttk.Button(lang_btn_frame, text="RU", width=4, command=lambda: self.toggle_language('ru')).pack(side='left', padx=2)
        ttk.Button(lang_btn_frame, text="AR", width=4, command=lambda: self.toggle_language('ar')).pack(side='left', padx=2)
        ttk.Button(lang_btn_frame, text="EN", width=4, command=lambda: self.toggle_language('en')).pack(side='left', padx=2)

        ttk.Button(header_frame, text=self.get_text('logout'), command=self.show_login_screen, width=20).pack(side='right')
        
        # Хлебные крошки (Navigation Path - Requirement 6)
        path_text = " > ".join([self.get_text(item[1]) for item in self.nav_stack])
        ttk.Label(header_frame, text=f"📍 {path_text}", style='Header.TLabel', font=('Segoe UI', 9, 'italic')).pack(side='left', padx=20)
        
        self.draw_status_bar()

    def fit_window_to_content(self, extra_w=80, extra_h=140, max_ratio=0.95):
        """
        Подогнать размер главного окна под содержимое current_frame.
        extra_w/extra_h — дополнительные отступы, max_ratio — максимальная доля экрана.
        """
        try:
            self.root.update_idletasks()
            if not self.current_frame:
                return

            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()

            req_w = self.current_frame.winfo_reqwidth() + extra_w
            req_h = self.current_frame.winfo_reqheight() + extra_h

            max_w = int(sw * max_ratio)
            max_h = int(sh * max_ratio)

            w = min(req_w, max_w)
            h = min(req_h, max_h)

            x = max((sw - w) // 2, 0)
            y = max((sh - h) // 2, 0)

            self.root.geometry(f"{w}x{h}+{x}+{y}")
            self.root.update_idletasks()
        except Exception:
            pass

    def get_text(self, key):
        """Возвращает переведенный текст для ключа."""
        if key in TRANSLATIONS:
            return TRANSLATIONS[key].get(self.lang, TRANSLATIONS[key]['ru'])
        return key

    def toggle_language(self, lang_code):
        """Смена языка и обновление текущего кадра с сохранением позиции."""
        self.lang = lang_code
        # Обновляем текущий экран БЕЗ перехода в главное меню
        if self.current_user and self.nav_stack:
            # Перерисовываем текущий экран с сохранением позиции
            current = self.nav_stack.pop()
            func = current[0]
            args = current[2] if len(current) > 2 else []
            kwargs = current[3] if len(current) > 3 else {}
            func(*args, **kwargs)
        elif self.current_user:
            self.show_main_menu()
        else:
            self.show_splash_screen()

    def show_login_screen(self):
        """Показать экран входа"""
        self.current_user = None
        self.nav_stack = []
        self.clear_window()

        self.current_frame = ttk.Frame(self.root, padding=30)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame.help_tag = 'help_login'

        # Переключатель языка на экране входа
        lang_frame = ttk.Frame(self.current_frame)
        lang_frame.pack(anchor='ne')
        ttk.Button(lang_frame, text="RU", width=4, command=lambda: self.toggle_language('ru')).pack(side='left', padx=2)
        ttk.Button(lang_frame, text="AR", width=4, command=lambda: self.toggle_language('ar')).pack(side='left', padx=2)
        ttk.Button(lang_frame, text="EN", width=4, command=lambda: self.toggle_language('en')).pack(side='left', padx=2)

        ttk.Label(self.current_frame, text=self.get_text('app_title'),
                  style='Title.TLabel').pack(pady=(20, 10))

        ttk.Label(self.current_frame, text=self.get_text('app_subtitle'),
                  style='Subtitle.TLabel').pack(pady=(0, 20))

        form_container = ttk.LabelFrame(self.current_frame, text=self.get_text('login_container'), padding=20)
        form_container.pack(pady=10)

        form_frame = ttk.Frame(form_container)
        form_frame.pack()

        ttk.Label(form_frame, text=self.get_text('login_label'), font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=10)
        login_entry = ttk.Entry(form_frame, width=30, font=('Segoe UI', 10))
        login_entry.grid(row=0, column=1, pady=10, padx=10)
        login_entry.focus()

        ttk.Label(form_frame, text=self.get_text('password_label'), font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=10)
        password_entry = ttk.Entry(form_frame, width=30, show="*", font=('Segoe UI', 10))
        password_entry.grid(row=1, column=1, pady=10, padx=10)

        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(pady=20)

        def login_action():
            username = login_entry.get()
            password = password_entry.get()
            self.login(username, password)

        ttk.Button(button_frame, text=self.get_text('login_btn'), style='Accent.TButton',
                   command=login_action, width=15).pack(side='left', padx=10)

        ttk.Button(button_frame, text=self.get_text('register_btn'), width=15,
                   command=self.show_register_screen).pack(side='left', padx=10)

        ttk.Button(button_frame, text=self.get_text('exit'), width=12,
                   command=self.root.destroy).pack(side='left', padx=10)

        ttk.Label(self.current_frame, text=self.get_text('login_welcome_info'), font=('Segoe UI', 9, 'italic'),
                  foreground='#7F8C8D', justify='center').pack(pady=10)

        ttk.Label(self.current_frame, text=self.get_text('login_welcome_info2'), font=('Arial', 9),
                  foreground='gray', justify='center').pack(pady=10)

        def on_enter(event):
            login_action()

        login_entry.bind('<Return>', on_enter)
        password_entry.bind('<Return>', on_enter)

        self.fit_window_to_content()

    def login(self, username, password):
        """Авторизация пользователя"""
        if not username or not password:
            messagebox.showerror(self.get_text('error'), self.get_text('error_login_empty'))
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT id, username, full_name, role FROM users WHERE username = ? AND password = ?",
                (username, self.db_manager.hash_password(password))
            )
            user = cursor.fetchone()
            cursor.close()

            if user:
                self.current_user = {
                    'id': user[0],
                    'username': user[1],
                    'full_name': user[2],
                    'role': user[3]
                }
                messagebox.showinfo(self.get_text('success'), self.get_text('success_login').format(name=user[2], role=user[3]))
                self.show_main_menu()
            else:
                messagebox.showerror(self.get_text('error'), self.get_text('error_login'))
        except Error as e:
            messagebox.showerror(self.get_text('error'), f"{self.get_text('error_db')}: {e}")

    def show_main_menu(self):
        """Главное меню مع تصميم جديد كلياً"""
        self.update_nav_stack(self.show_main_menu, 'main_menu_btn')
        self.clear_window()
        self.draw_header()

        # المحتوى الرئيسي
        main_container = ttk.Frame(self.root, padding=30)
        main_container.pack(fill=tk.BOTH, expand=True)
        self.current_frame = main_container
        self.current_frame.help_tag = 'help_main'

        ttk.Label(main_container,
                  text=self.get_text('menu_title'),
                  style='Title.TLabel',
                  justify='center').pack(pady=(0, 10))

        # عرض سريع للإحصائيات (Quick Stats Dashboard)
        try:
            stats = self.statistics.get_system_stats()
            stats_frame = ttk.Frame(main_container)
            stats_frame.pack(pady=15)
            
            stat_items = [
                (f"🍲 {stats['recipes']}", self.get_text('recipes_count')),
                (f"🌍 {stats['cuisines']}", self.get_text('cuisines_count')),
                (f"👥 {stats['users']}", self.get_text('users_count'))
            ]
            
            for val, label in stat_items:
                f = ttk.Frame(stats_frame, padding=10)
                f.pack(side='left', padx=15)
                ttk.Label(f, text=val, font=('Segoe UI', 16, 'bold'), foreground='#2E86C1').pack()
                ttk.Label(f, text=label, font=('Segoe UI', 9)).pack()
        except:
            pass

        menu_frame = ttk.Frame(main_container)
        menu_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # تحديد الوظائف حسب الصلاحيات مع أيقونات
        functions = [
            (self.get_text('menu_catalog'), self.get_text('menu_catalog_desc'), self.recipe_mgmt.show_recipe_catalog),
            (self.get_text('menu_cuisines'), self.get_text('menu_cuisines_desc'), self.cuisines.show_cuisines),
            (self.get_text('menu_stats'), self.get_text('menu_stats_desc'), self.statistics.show_statistics),
            (self.get_text('menu_calc'), self.get_text('menu_calc_desc'), self.calculator.show_calculator),
        ]

        # أزرار المستخدم العادي
        if self.current_user['role'] == 'user':
            functions.append((self.get_text('menu_create_recipe'), self.get_text('menu_create_recipe_desc'), self.personal_recipes.create_personal_recipe))

        # أزرار الإدارة والشيف
        if self.current_user['role'] in ['admin', 'chef']:
            functions.append((self.get_text('menu_add_recipe'), self.get_text('menu_add_recipe_desc'), self.recipe_mgmt.add_recipe))

        if self.current_user['role'] == 'admin':
            functions.append((self.get_text('menu_manage'), self.get_text('menu_manage_desc'), self.user_mgmt.manage_users))

        # إنشاء بطاقات الأزرار (Button Cards)
        for i, (text, desc, command) in enumerate(functions):
            row = i // 2
            col = i % 2
            
            btn_frame = ttk.LabelFrame(menu_frame, text="", padding=5)
            btn_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            menu_frame.columnconfigure(col, weight=1)
            
            ttk.Label(btn_frame, text=desc, font=('Segoe UI', 8), foreground='gray').pack(pady=(0, 5))
            btn = ttk.Button(btn_frame, text=text, command=command, width=30)
            if "Добавить" in text or "Создать" in text:
                btn.configure(style='Secondary.TButton')
            elif "Управление" in text:
                btn.configure(style='Accent.TButton')
            btn.pack(pady=5)

    # Функции, используемые в других модулях
    def show_recipe_catalog(self):
        """Каталог рецептов"""
        self.update_nav_stack(self.show_recipe_catalog, 'menu_catalog')
        self.recipe_mgmt.show_recipe_catalog()

    def show_calculator(self, recipe_id=None):
        """Калькулятор продуктов"""
        self.update_nav_stack(self.show_calculator, 'menu_calc')
        self.calculator.show_calculator(recipe_id)

    def show_calculator_for_recipe(self, recipe_id):
        """Показать калькулятор для конкретного рецепта"""
        self.calculator.show_calculator_for_recipe(recipe_id)

    def show_recipe_details(self, recipe_id):
        """Показать детали рецепта"""
        self.recipe_mgmt.show_recipe_details(recipe_id)

    def show_cuisines(self):
        """Показать мировые кухни"""
        self.cuisines.show_cuisines()

    def show_statistics(self):
        """Показать статистику"""
        self.statistics.show_statistics()

    def add_recipe(self):
        """Добавить новый рецепт"""
        self.recipe_mgmt.add_recipe()

    def manage_recipes(self):
        """Управление рецептами"""
        self.recipe_mgmt.manage_recipes()

    def manage_users(self):
        """Управление пользователями"""
        self.user_mgmt.manage_users()

    def create_personal_recipe(self):
        """Создать персональный рецепт"""
        self.personal_recipes.create_personal_recipe()

    def get_system_stats(self):
        """Получение статистики системы"""
        return self.statistics.get_system_stats()

    def show_register_screen(self):
        """Показать экран регистрации нового пользователя"""
        self.clear_window()

        self.current_frame = ttk.Frame(self.root, padding=20)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.current_frame, text=self.get_text('register_title'),
                  style='Title.TLabel').pack(pady=10)

        form = ttk.Frame(self.current_frame)
        form.pack(pady=10)

        ttk.Label(form, text=self.get_text('login_label'), font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        username_entry = ttk.Entry(form, width=30)
        username_entry.grid(row=0, column=1, pady=5, padx=5)
        username_entry.focus()

        ttk.Label(form, text=self.get_text('full_name_label'), font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        fullname_entry = ttk.Entry(form, width=30)
        fullname_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form, text=self.get_text('password_label'), font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        password_entry = ttk.Entry(form, width=30, show='*')
        password_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(form, text=self.get_text('confirm_password_label'), font=('Arial', 10)).grid(row=3, column=0, sticky='w', pady=5)
        password_confirm_entry = ttk.Entry(form, width=30, show='*')
        password_confirm_entry.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(self.current_frame, text=self.get_text('reg_note'), font=('Arial', 9),
                  foreground='gray', wraplength=460).pack(pady=10)

        def register_user():
            username = username_entry.get().strip()
            fullname = fullname_entry.get().strip() or username
            password = password_entry.get()
            password_conf = password_confirm_entry.get()

            if not username or not password or not password_conf:
                messagebox.showerror(self.get_text('error'), self.get_text('error_fill_fields'))
                return

            if password != password_conf:
                messagebox.showerror(self.get_text('error'), self.get_text('error_passwords_mismatch'))
                return

            cursor = None
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    messagebox.showerror(self.get_text('error'), self.get_text('error_user_exists'))
                    return

                hashed = self.db_manager.hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                    (username, hashed, fullname, 'user')
                )
                self.db_connection.commit()

                messagebox.showinfo(self.get_text('success'), self.get_text('reg_success'))
                self.show_login_screen()

            except Exception as e:
                messagebox.showerror(self.get_text('error'), f"{self.get_text('error_db')}: {e}")
            finally:
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass

        def on_enter_register(event):
            register_user()

        username_entry.bind('<Return>', on_enter_register)
        password_entry.bind('<Return>', on_enter_register)
        password_confirm_entry.bind('<Return>', on_enter_register)

        self.fit_window_to_content()

        btn_frame = ttk.Frame(self.current_frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text=self.get_text('register_action_btn'), command=register_user,
                   width=18).pack(side='left', padx=8)
        ttk.Button(btn_frame, text=self.get_text('back'), command=self.show_login_screen,
                   width=12).pack(side='left', padx=8)

        def go_home_or_login():
            if self.current_user:
                self.show_main_menu()
            else:
                self.show_login_screen()

        ttk.Button(btn_frame, text=self.get_text('main_menu_btn'), command=go_home_or_login,
                   width=12).pack(side='left', padx=8)




