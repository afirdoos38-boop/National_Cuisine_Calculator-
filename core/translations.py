"""
core/translations.py
Словарь переводов UI элементов на три языка: Русский (ru), Арабский (ar), Английский (en).
Все строки пользовательского интерфейса извлечены из модулей и собраны здесь.
"""

TRANSLATIONS = {
    # ==================== Общие (General) ====================
    'app_title': {
        'ru': '🍽️ Калькулятор национальной кухни',
        'ar': '🍽️ حاسبة المطبخ العالمي',
        'en': '🍽️ National Cuisine Calculator'
    },
    'app_subtitle': {
        'ru': 'Расчёт продуктов и каталог рецептов мировых кухонь',
        'ar': 'حساب المكونات وكتالوج وصفات المطابخ العالمية',
        'en': 'Ingredient calculator and world cuisine recipe catalog'
    },
    'back': {
        'ru': '↩️ Назад',
        'ar': '↩️ رجوع',
        'en': '↩️ Back'
    },
    'exit': {
        'ru': '❌ Выход',
        'ar': '❌ خروج',
        'en': '❌ Exit'
    },
    'main_menu_btn': {
        'ru': '🏠 Главная',
        'ar': '🏠 الرئيسية',
        'en': '🏠 Home'
    },
    'logout': {
        'ru': '🚪 Выход из аккаунта',
        'ar': '🚪 تسجيل خروج',
        'en': '🚪 Log out'
    },
    'back_to_main': {
        'ru': '🏠 Назад в главное меню',
        'ar': '🏠 العودة للقائمة الرئيسية',
        'en': '🏠 Back to main menu'
    },

    # ==================== Экран входа (Login Screen) ====================
    'login_container': {
        'ru': ' 🔐 Вход в систему ',
        'ar': ' 🔐 تسجيل الدخول ',
        'en': ' 🔐 Sign In '
    },
    'login_label': {
        'ru': 'Логин:',
        'ar': 'اسم المستخدم:',
        'en': 'Username:'
    },
    'password_label': {
        'ru': 'Пароль:',
        'ar': 'كلمة المرور:',
        'en': 'Password:'
    },
    'login_btn': {
        'ru': '🚪 Войти',
        'ar': '🚪 دخول',
        'en': '🚪 Sign In'
    },
    'register_btn': {
        'ru': '📝 Регистрация',
        'ar': '📝 تسجيل جديد',
        'en': '📝 Register'
    },
    'login_welcome_info': {
        'ru': 'Добро пожаловать! Используйте свои данные для доступа.',
        'ar': 'أهلاً بك! يرجى استخدام بياناتك للدخول.',
        'en': 'Welcome! Please use your credentials to log in.'
    },
    'login_welcome_info2': {
        'ru': 'Добро пожаловать в систему расчёта продуктов для национальной кухни!',
        'ar': 'أهلاً بك في نظام حساب المكونات للمطبخ العالمي!',
        'en': 'Welcome to the National Cuisine Ingredient Calculator!'
    },

    # ==================== Экран регистрации (Register Screen) ====================
    'register_title': {
        'ru': '📝 Регистрация нового пользователя',
        'ar': '📝 تسجيل مستخدم جديد',
        'en': '📝 Register New User'
    },
    'full_name_label': {
        'ru': 'Полное имя:',
        'ar': 'الاسم الكامل:',
        'en': 'Full Name:'
    },
    'confirm_password_label': {
        'ru': 'Подтвердите пароль:',
        'ar': 'تأكيد كلمة المرور:',
        'en': 'Confirm Password:'
    },
    'register_action_btn': {
        'ru': 'Зарегистрироваться',
        'ar': 'تسجيل',
        'en': 'Register'
    },
    'reg_note': {
        'ru': 'Регистрация создаёт обычного пользователя с ролью \'user\'.\nЕсли нужен аккаунт с правами шефа или администратора — обратитесь к администратору.',
        'ar': 'التسجيل ينشئ حساب مستخدم عادي بصلاحية \'user\'.\nإذا احتجت صلاحية شيف أو مدير — تواصل مع المدير.',
        'en': 'Registration creates a regular user account with \'user\' role.\nFor chef or admin access, please contact the administrator.'
    },
    'reg_success': {
        'ru': 'Регистрация успешна. Теперь войдите в систему.',
        'ar': 'تم التسجيل بنجاح. الآن سجل الدخول.',
        'en': 'Registration successful. Please sign in now.'
    },

    # ==================== Заставка (Splash Screen) ====================
    'splash_author_frame': {
        'ru': ' Автор проекта ',
        'ar': ' مؤلف المشروع ',
        'en': ' Project Author '
    },
    'splash_start_btn': {
        'ru': 'Приступить к работе ➔',
        'ar': 'ابدأ العمل ➔',
        'en': 'Get Started ➔'
    },

    # ==================== Главное меню (Main Menu) ====================
    'menu_title': {
        'ru': '🍳 Главное меню системы',
        'ar': '🍳 القائمة الرئيسية للنظام',
        'en': '🍳 System Main Menu'
    },
    'role_label': {
        'ru': 'Роль:',
        'ar': 'الدور:',
        'en': 'Role:'
    },
    'recipes_count': {
        'ru': 'рецептов',
        'ar': 'وصفة',
        'en': 'recipes'
    },
    'cuisines_count': {
        'ru': 'кухонь',
        'ar': 'مطبخ عالمي',
        'en': 'cuisines'
    },
    'users_count': {
        'ru': 'пользователей',
        'ar': 'مستخدم',
        'en': 'users'
    },

    # ==================== Функции меню (Menu Functions) ====================
    'menu_catalog': {
        'ru': '📖 Каталог рецептов',
        'ar': '📖 كتالوج الوصفات',
        'en': '📖 Recipe Catalog'
    },
    'menu_catalog_desc': {
        'ru': '📖 Просмотр каталога рецептов',
        'ar': '📖 تصفح كتالوج الوصفات',
        'en': '📖 Browse the recipe catalog'
    },
    'menu_cuisines': {
        'ru': '🌍 Мировые кухни',
        'ar': '🌍 المطابخ العالمية',
        'en': '🌍 World Cuisines'
    },
    'menu_cuisines_desc': {
        'ru': '🌍 Исследуйте кухни со всех континентов',
        'ar': '🌍 استكشف المطابخ من كل القارات',
        'en': '🌍 Explore cuisines from all continents'
    },
    'menu_stats': {
        'ru': '📊 Статистика',
        'ar': '📊 الإحصائيات',
        'en': '📊 Statistics'
    },
    'menu_stats_desc': {
        'ru': '📊 Просмотр общих отчетов и статистики',
        'ar': '📊 عرض التقارير والإحصائيات العامة',
        'en': '📊 View reports and statistics'
    },
    'menu_calc': {
        'ru': '🧮 Калькулятор',
        'ar': '🧮 الحاسبة',
        'en': '🧮 Calculator'
    },
    'menu_calc_desc': {
        'ru': '🧮 Расчет ингредиентов для определенного количества людей',
        'ar': '🧮 حساب المكونات لعدد معين من الأشخاص',
        'en': '🧮 Calculate ingredients for a given number of people'
    },
    'menu_create_recipe': {
        'ru': '✍️ Создать рецепт',
        'ar': '✍️ إنشاء وصفة',
        'en': '✍️ Create Recipe'
    },
    'menu_create_recipe_desc': {
        'ru': '✍️ Создайте свой собственный рецепт',
        'ar': '✍️ إضافة وصفة جديدة خاصة بك',
        'en': '✍️ Create your own personal recipe'
    },
    'menu_add_recipe': {
        'ru': '➕ Добавить рецепт',
        'ar': '➕ إضافة وصفة',
        'en': '➕ Add Recipe'
    },
    'menu_add_recipe_desc': {
        'ru': '➕ Добавить новое блюдо в базу данных',
        'ar': '➕ إضافة وصفة جديدة لقاعدة البيانات',
        'en': '➕ Add a new dish to the database'
    },
    'menu_manage': {
        'ru': '👥 Управление',
        'ar': '👥 الإدارة',
        'en': '👥 User Management'
    },
    'menu_manage_desc': {
        'ru': '👥 Управление учетными записями пользователей',
        'ar': '👥 إدارة حسابات المستخدمين',
        'en': '👥 Manage user accounts'
    },

    # ==================== Кнопки управления (Action Buttons) ====================
    'search': {
        'ru': '🔍 Поиск',
        'ar': '🔍 بحث',
        'en': '🔍 Search'
    },
    'view_details': {
        'ru': '👁️ Просмотр',
        'ar': '👁️ عرض التفاصيل',
        'en': '👁️ View Details'
    },
    'calculate_btn': {
        'ru': '🧮 Рассчитать',
        'ar': '🧮 احسب الكميات',
        'en': '🧮 Calculate'
    },
    'edit_btn': {
        'ru': '✏️ Изменить',
        'ar': '✏️ تعديل',
        'en': '✏️ Edit'
    },
    'delete_btn': {
        'ru': '🗑️ Удалить',
        'ar': '🗑️ حذف',
        'en': '🗑️ Delete'
    },
    'save': {
        'ru': '💾 Сохранить',
        'ar': '💾 حفظ',
        'en': '💾 Save'
    },
    'print': {
        'ru': '🖨️ Печать',
        'ar': '🖨️ طباعة',
        'en': '🖨️ Print'
    },
    'apply_filters': {
        'ru': '✅ Применить',
        'ar': '✅ تطبيق الكل',
        'en': '✅ Apply Filters'
    },
    'reset_filters': {
        'ru': '🔄 Сбросить',
        'ar': '🔄 إعادة ضبط',
        'en': '🔄 Reset'
    },

    # ==================== Фильтры каталога (Catalog Filters) ====================
    'search_label': {
        'ru': 'Поиск:',
        'ar': 'بحث:',
        'en': 'Search:'
    },
    'cuisine_label': {
        'ru': 'Кухня:',
        'ar': 'المطبخ:',
        'en': 'Cuisine:'
    },
    'difficulty_label': {
        'ru': 'Сложность:',
        'ar': 'الصعوبة:',
        'en': 'Difficulty:'
    },
    'category_label': {
        'ru': 'Категория:',
        'ar': 'الفئة:',
        'en': 'Category:'
    },

    # ==================== Значения фильтров (Filter Values) ====================
    'diff_easy': {
        'ru': 'легко',
        'ar': 'سهل',
        'en': 'easy'
    },
    'diff_medium': {
        'ru': 'средне',
        'ar': 'متوسط',
        'en': 'medium'
    },
    'diff_hard': {
        'ru': 'сложно',
        'ar': 'صعب',
        'en': 'hard'
    },
    'cat_salad': {
        'ru': 'салат',
        'ar': 'سلطة',
        'en': 'salad'
    },
    'cat_soup': {
        'ru': 'суп',
        'ar': 'حساء',
        'en': 'soup'
    },
    'cat_snack': {
        'ru': 'закуска',
        'ar': 'مقبلات',
        'en': 'snack'
    },
    'cat_main': {
        'ru': 'основное блюдо',
        'ar': 'طبق رئيسي',
        'en': 'main course'
    },
    'cat_dessert': {
        'ru': 'десерт',
        'ar': 'حلوى',
        'en': 'dessert'
    },
    'cat_drink': {
        'ru': 'напиток',
        'ar': 'مشروب',
        'en': 'drink'
    },

    # ==================== Заголовки таблиц (Table Column Headers) ====================
    'col_id': {
        'ru': 'ID',
        'ar': 'م',
        'en': 'ID'
    },
    'col_name': {
        'ru': 'Название',
        'ar': 'الاسم',
        'en': 'Name'
    },
    'col_cuisine': {
        'ru': 'Кухня',
        'ar': 'المطبخ',
        'en': 'Cuisine'
    },
    'col_country': {
        'ru': 'Страна',
        'ar': 'البلد',
        'en': 'Country'
    },
    'col_portions': {
        'ru': 'Порции',
        'ar': 'الحصص',
        'en': 'Portions'
    },
    'col_time': {
        'ru': 'Время',
        'ar': 'الوقت',
        'en': 'Time'
    },
    'col_difficulty': {
        'ru': 'Сложность',
        'ar': 'الصعوبة',
        'en': 'Difficulty'
    },
    'col_calories': {
        'ru': 'Калории',
        'ar': 'السعرات',
        'en': 'Calories'
    },
    'col_ingredient': {
        'ru': 'Ингредиент',
        'ar': 'المكوّن',
        'en': 'Ingredient'
    },
    'col_quantity': {
        'ru': 'Количество',
        'ar': 'الكمية',
        'en': 'Quantity'
    },
    'col_unit': {
        'ru': 'Единица',
        'ar': 'الوحدة',
        'en': 'Unit'
    },
    'col_price_per_unit': {
        'ru': 'Цена за единицу',
        'ar': 'سعر الوحدة',
        'en': 'Price/Unit'
    },
    'col_total_cost': {
        'ru': 'Общая стоимость',
        'ar': 'التكلفة الإجمالية',
        'en': 'Total Cost'
    },

    # ==================== Калькулятор (Calculator) ====================
    'select_recipe': {
        'ru': 'Выберите рецепт:',
        'ar': 'اختر وصفة:',
        'en': 'Select a recipe:'
    },
    'portions_label': {
        'ru': 'Количество порций:',
        'ar': 'عدد الحصص:',
        'en': 'Number of portions:'
    },
    'total_cost_label': {
        'ru': 'Общая стоимость: {cost} руб.',
        'ar': 'التكلفة الإجمالية: {cost} روبل',
        'en': 'Total cost: {cost} RUB'
    },
    'currency': {
        'ru': 'руб',
        'ar': 'روبل',
        'en': 'RUB'
    },
    'unit_kcal': {
        'ru': 'ккал',
        'ar': 'سعرة',
        'en': 'kcal'
    },
    'unit_min': {
        'ru': 'мин',
        'ar': 'دقيقة',
        'en': 'min'
    },

    # ==================== Статистика (Statistics) ====================
    'total_recipes_label': {
        'ru': 'Всего рецептов: {n}',
        'ar': 'إجمالي الوصفات: {n}',
        'en': 'Total recipes: {n}'
    },
    'total_cuisines_label': {
        'ru': 'Всего кухонь: {n}',
        'ar': 'إجمالي المطابخ: {n}',
        'en': 'Total cuisines: {n}'
    },
    'total_users_label': {
        'ru': 'Всего пользователей: {n}',
        'ar': 'إجمالي المستخدمين: {n}',
        'en': 'Total users: {n}'
    },
    'quick_preview': {
        'ru': '📝 Быстрый просмотр деталей',
        'ar': '📝 معاينة سريعة لتفاصيل الوجبة',
        'en': '📝 Quick Recipe Details Preview'
    },
    'filters_title': {
        'ru': 'Фильтры',
        'ar': 'الفلاتر',
        'en': 'Filters'
    },
    'report_label': {
        'ru': 'Отчёт:',
        'ar': 'التقرير:',
        'en': 'Report:'
    },
    'report_by_cuisines': {
        'ru': 'По кухням',
        'ar': 'حسب المطابخ',
        'en': 'By Cuisines'
    },
    'report_by_types': {
        'ru': 'По видам рецептов',
        'ar': 'حسب أنواع الوصفات',
        'en': 'By Recipe Types'
    },
    'report_by_calories': {
        'ru': 'По калориям',
        'ar': 'حسب السعرات',
        'en': 'By Calories'
    },
    'all_cuisines': {
        'ru': 'Все кухни',
        'ar': 'كل المطابخ',
        'en': 'All Cuisines'
    },
    'all_types': {
        'ru': 'Все виды',
        'ar': 'كل الأنواع',
        'en': 'All Types'
    },
    'cat_all': {
        'ru': 'Все',
        'ar': 'الكل',
        'en': 'All'
    },
    'cat_dishes': {
        'ru': 'Блюда',
        'ar': 'أطباق',
        'en': 'Dishes'
    },
    'cat_salads': {
        'ru': 'Салаты',
        'ar': 'سلطات',
        'en': 'Salads'
    },
    'print_recipe_btn': {
        'ru': '🧮 🖨️ Печать рецепта',
        'ar': '🧮 🖨️ طباعة الوصفة',
        'en': '🧮 🖨️ Print Recipe'
    },
    'recipes_by_filter': {
        'ru': 'Список рецептов по выбранному фильтру',
        'ar': 'قائمة الوصفات حسب الفلتر المحدد',
        'en': 'Recipes by selected filter'
    },
    'cal_from': {
        'ru': 'Калории от:',
        'ar': 'السعرات من:',
        'en': 'Calories from:'
    },
    'cal_to': {
        'ru': 'до:',
        'ar': 'إلى:',
        'en': 'to:'
    },

    # ==================== Кухни (Cuisines) ====================
    'recipes_in_cuisine': {
        'ru': '📋 Рецептов: {n}',
        'ar': '📋 الوصفات: {n}',
        'en': '📋 Recipes: {n}'
    },
    'show_recipes_btn': {
        'ru': '📖 Показать рецепты',
        'ar': '📖 عرض الوصفات',
        'en': '📖 Show Recipes'
    },
    'recipes_of_cuisine': {
        'ru': '📋 Рецепты {name}',
        'ar': '📋 وصفات {name}',
        'en': '📋 Recipes of {name}'
    },

    # ==================== Управление пользователями (User Management) ====================
    'user_mgmt_title': {
        'ru': '👥 Управление пользователями',
        'ar': '👥 إدارة المستخدمين',
        'en': '👥 User Management'
    },
    'col_login': {
        'ru': 'Логин',
        'ar': 'المستخدم',
        'en': 'Login'
    },
    'col_fullname': {
        'ru': 'Имя',
        'ar': 'الاسم',
        'en': 'Name'
    },
    'col_role': {
        'ru': 'Роль',
        'ar': 'الدور',
        'en': 'Role'
    },
    'col_date': {
        'ru': 'Дата регистрации',
        'ar': 'تاريخ التسجيل',
        'en': 'Registration Date'
    },

    # ==================== Создание рецепта (Personal Recipe) ====================
    'personal_recipe_title': {
        'ru': '📝 Создание персонального рецепта',
        'ar': '📝 إنشاء وصفة شخصية',
        'en': '📝 Create Personal Recipe'
    },
    'recipe_name_label': {
        'ru': 'Название рецепта:',
        'ar': 'اسم الوصفة:',
        'en': 'Recipe name:'
    },
    'description_label': {
        'ru': 'Описание:',
        'ar': 'الوصف:',
        'en': 'Description:'
    },
    'ingredients_label': {
        'ru': 'Ингредиенты (название|количество|ед.):',
        'ar': 'المكونات (الاسم|الكمية|الوحدة):',
        'en': 'Ingredients (name|qty|unit):'
    },
    'instructions_label': {
        'ru': 'Инструкции:',
        'ar': 'التعليمات:',
        'en': 'Instructions:'
    },
    'portions_field_label': {
        'ru': 'Порции:',
        'ar': 'الحصص:',
        'en': 'Portions:'
    },
    'preview_btn': {
        'ru': 'Предпросмотр',
        'ar': 'معاينة',
        'en': 'Preview'
    },
    'save_and_print_btn': {
        'ru': '💾 Сохранить и печать',
        'ar': '💾 حفظ وطباعة',
        'en': '💾 Save & Print'
    },
    'save_for_print_btn': {
        'ru': '🖨️ Сохранить для печати',
        'ar': '🖨️ حفظ للطباعة',
        'en': '🖨️ Save for printing'
    },
    'create_new_recipe_btn': {
        'ru': '📝 Создать новый рецепт',
        'ar': '📝 إنشاء وصفة جديدة',
        'en': '📝 Create new recipe'
    },

    # ==================== Контекстное меню (Context Menu) ====================
    'ctx_copy': {
        'ru': 'Копировать',
        'ar': 'نسخ',
        'en': 'Copy'
    },
    'ctx_paste': {
        'ru': 'Вставить',
        'ar': 'لصق',
        'en': 'Paste'
    },
    'ctx_cut': {
        'ru': 'Вырезать',
        'ar': 'قص',
        'en': 'Cut'
    },

    # ==================== Результаты (Results) ====================
    'recipes_found': {
        'ru': 'Найдено рецептов: {n}',
        'ar': 'الوصفات الموجودة: {n}',
        'en': 'Recipes found: {n}'
    },

    # ==================== Сообщения (Messages) ====================
    'success_login': {
        'ru': 'Добро пожаловать, {name}!\nВаша роль: {role}',
        'ar': 'أهلاً بك {name}!\nدورك: {role}',
        'en': 'Welcome, {name}!\nYour role: {role}'
    },
    'success': {
        'ru': 'Успех',
        'ar': 'نجاح',
        'en': 'Success'
    },
    'error': {
        'ru': 'Ошибка',
        'ar': 'خطأ',
        'en': 'Error'
    },
    'warning': {
        'ru': 'Внимание',
        'ar': 'تنبيه',
        'en': 'Warning'
    },
    'info': {
        'ru': 'Информация',
        'ar': 'معلومات',
        'en': 'Information'
    },
    'error_db': {
        'ru': 'Ошибка базы данных',
        'ar': 'خطأ في قاعدة البيانات',
        'en': 'Database Error'
    },
    'error_login': {
        'ru': 'Неверный логин или пароль',
        'ar': 'اسم المستخدم أو كلمة المرور غير صحيحة',
        'en': 'Invalid username or password'
    },
    'error_fill_fields': {
        'ru': 'Заполните все обязательные поля',
        'ar': 'يرجى ملء جميع الحقول المطلوبة',
        'en': 'Please fill in all required fields'
    },
    'error_login_empty': {
        'ru': 'Введите логин и пароль',
        'ar': 'أدخل اسم المستخدم وكلمة المرور',
        'en': 'Enter username and password'
    },
    'error_passwords_mismatch': {
        'ru': 'Пароли не совпадают',
        'ar': 'كلمتا المرور غير متطابقتين',
        'en': 'Passwords do not match'
    },
    'error_user_exists': {
        'ru': 'Пользователь с таким логином уже существует',
        'ar': 'اسم المستخدم موجود بالفعل',
        'en': 'Username already exists'
    },
    'select_recipe_warning': {
        'ru': 'Выберите рецепт',
        'ar': 'اختر وصفة',
        'en': 'Select a recipe'
    },
    'select_recipe_for_calc': {
        'ru': 'Выберите рецепт из списка',
        'ar': 'اختر وصفة من القائمة',
        'en': 'Select a recipe from the list'
    },
    'portions_negative': {
        'ru': 'Количество порций не может быть отрицательным',
        'ar': 'عدد الحصص لا يمكن أن يكون سالباً',
        'en': 'Number of portions cannot be negative'
    },
    'portions_invalid': {
        'ru': 'Введите корректное число порций',
        'ar': 'أدخل عدد حصص صحيح',
        'en': 'Enter a valid number of portions'
    },
    'recipe_not_found': {
        'ru': 'Рецепт не найден',
        'ar': 'الوصفة غير موجودة',
        'en': 'Recipe not found'
    },
    'file_saved': {
        'ru': 'Расчёт успешно сохранён в {path}',
        'ar': 'تم حفظ الحساب بنجاح في {path}',
        'en': 'Calculation saved to {path}'
    },
    'done': {
        'ru': 'Готово',
        'ar': 'تم',
        'en': 'Done'
    },
    'save_calculation_title': {
        'ru': 'Сохранить расчёт',
        'ar': 'حفظ الحساب',
        'en': 'Save Calculation'
    },
    'text_files': {
        'ru': 'Текстовые файлы',
        'ar': 'ملفات نصية',
        'en': 'Text Files'
    },
    'select_recipe_for_print': {
        'ru': 'Выберите рецепт для печати',
        'ar': 'اختر وصفة للطباعة',
        'en': 'Select a recipe to print'
    },
    'recipe_deleted_success': {
        'ru': 'Рецепт удален и перемещен в архив',
        'ar': 'تم حذف الوصفة ونقلها للأرشيف',
        'en': 'Recipe deleted and moved to archive'
    },
    'recipe_delete_error': {
        'ru': 'Не удалось удалить рецепт',
        'ar': 'فشل حذف الوصفة',
        'en': 'Failed to delete recipe'
    },
    'select_recipe_for_edit': {
        'ru': 'Выберите рецепт для редактирования',
        'ar': 'اختر وصفة للتعديل',
        'en': 'Select a recipe to edit'
    },
    'select_recipe_for_delete': {
        'ru': 'Выберите рецепт для удаления',
        'ar': 'اختر وصفة للحذف',
        'en': 'Select a recipe to delete'
    },
    'select_recipe_for_calc_btn': {
        'ru': 'Выберите рецепт для расчета',
        'ar': 'اختر وصفة للحساب',
        'en': 'Select a recipe to calculate'
    },
    'exit_confirm': {
        'ru': 'Пожалуйста, подтвердите: вернуться на экран входа?',
        'ar': 'هل تريد العودة لشاشة الدخول؟',
        'en': 'Return to the login screen?'
    },
    'exit_title': {
        'ru': 'Выход',
        'ar': 'خروج',
        'en': 'Exit'
    },
    'recipe_saved_success': {
        'ru': "✅ Рецепт '{name}' успешно добавлен в базу данных!\n📁 Также сохранен в файл: {file}",
        'ar': "✅ تمت إضافة الوصفة '{name}' بنجاح!\n📁 تم حفظها أيضاً في ملف: {file}",
        'en': "✅ Recipe '{name}' added to the database!\n📁 Also saved to file: {file}"
    },
    'portions_must_be_positive': {
        'ru': 'Количество порций должно быть больше 0',
        'ar': 'عدد الحصص يجب أن يكون أكبر من 0',
        'en': 'Portions must be greater than 0'
    },
    'portions_must_be_number': {
        'ru': 'Порции должны быть числом',
        'ar': 'عدد الحصص يجب أن يكون رقماً',
        'en': 'Portions must be a number'
    },
    'cuisine_not_found': {
        'ru': 'Выбранная кухня не найдена',
        'ar': 'المطبخ المحدد غير موجود',
        'en': 'Selected cuisine not found'
    },
    'preview_title': {
        'ru': 'Предварительный просмотр',
        'ar': 'معاينة',
        'en': 'Preview'
    },
    'recipe_file_saved': {
        'ru': 'Рецепт сохранен в файл: {file}',
        'ar': 'تم حفظ الوصفة في ملف: {file}',
        'en': 'Recipe saved to file: {file}'
    },
    'saved_title': {
        'ru': 'Сохранено',
        'ar': 'تم الحفظ',
        'en': 'Saved'
    },
    'close_btn': {
        'ru': 'Закрыть',
        'ar': 'إغلاق',
        'en': 'Close'
    },

    # ==================== Детали рецепта (Recipe Details) ====================
    'cooking_label': {
        'ru': '👨‍🍳 Приготовление:',
        'ar': '👨‍🍳 طريقة التحضير:',
        'en': '👨‍🍳 Cooking Instructions:'
    },
    'edit_recipe_title': {
        'ru': '✏️ Редактировать рецепт',
        'ar': '✏️ تعديل الوصفة',
        'en': '✏️ Edit Recipe'
    },
    'calc_products_btn': {
        'ru': '🧮 Рассчитать продукты',
        'ar': '🧮 حساب المكونات',
        'en': '🧮 Calculate Ingredients'
    },

    # ==================== Помощь и Реклама (Help & Splash) ====================
    'author_name': {
        'ru': 'Аль-Фахдави Ф. Х.А.',
        'ar': 'الفحداوي ف. خ. أ.',
        'en': 'Al-Fahdawi F. Kh.A.'
    },
    'author_group': {
        'ru': 'Группа 841-М23',
        'ar': 'المجموعة 841-M23',
        'en': 'Group 841-M23'
    },
    'splash_desc': {
        'ru': 'Интеллектуальная система расчёта ингредиентов и каталогизации национальных блюд мира.',
        'ar': 'نظام ذكي لحساب المكونات وفهرسة الأطباق الوطنية العالمية.',
        'en': 'An intelligent system for ingredient calculation and cataloging of national dishes worldwide.'
    },
    'hotkey_hints': {
        'ru': 'F1: Помощь | Esc: Назад | Tab: Переход | Enter: Выполнить',
        'ar': 'F1: مساعدة | Esc: رجوع | Tab: تنقل | Enter: موافق',
        'en': 'F1: Help | Esc: Back | Tab: Navigate | Enter: Confirm'
    },

    # ==================== Контекстная помощь (Context Help) ====================
    'help_login': {
        'ru': 'Введите логин и пароль для входа. Если вы новый пользователь, нажмите "Регистрация".\nF1 - Помощь, Enter - Вход.',
        'ar': 'أدخل اسم المستخدم وكلمة المرور. إذا كنت جديداً، اضغط "تسجيل".\nF1 للمساعدة، Enter للدخول.',
        'en': 'Enter your username and password to log in. If you are new, click "Register".\nF1 - Help, Enter - Sign In.'
    },
    'help_main': {
        'ru': 'Это главное меню. Выберите нужный раздел для работы с базой данных.\nEsc - Выход из аккаунта.',
        'ar': 'هذه القائمة الرئيسية. اختر القسم المطلوب للعمل على البيانات.\nEsc لتسجيل الخروج.',
        'en': 'This is the main menu. Select a section to work with.\nEsc - Log out.'
    },
    'help_catalog': {
        'ru': 'Здесь вы можете просматривать рецепты. Используйте поиск для фильтрации.\nEsc - Назад в меню.',
        'ar': 'هنا يمكنك تصفح الوصفات. استخدم البحث للتصفية.\nEsc للعودة للقائمة.',
        'en': 'Here you can browse recipes. Use search to filter.\nEsc - Back to menu.'
    },
    'help_details': {
        'ru': 'Здесь вы видите подробную карточку блюда. Вы можете нажать "Рассчитать" для перехода в калькулятор.\nEsc - Вернуться к каталогу.',
        'ar': 'عرض تفاصيل الوصفة. يمكنك الضغط على "احسب" للانتقال للحاسبة.\nEsc للعودة للكتالوج.',
        'en': 'Viewing a recipe card. Click "Calculate" to go to the calculator.\nEsc - Back to catalog.'
    },
    'help_calc': {
        'ru': 'Калькулятор порций: введите количество людей и нажмите "Рассчитать". Результат можно сохранить в файл.\nEsc - Назад в меню.',
        'ar': 'حاسبة الكميات: أدخل عدد الأشخاص واضغط "احسب". يمكنك حفظ النتيجة لملف.\nEsc للعودة للقائمة.',
        'en': 'Portion calculator: enter the number of people and click "Calculate". You can save results to a file.\nEsc - Back to menu.'
    },
    'help_stats': {
        'ru': 'Раздел статистики: здесь отображаются графические отчеты по базе рецептов и пользователям.\nEsc - Назад в меню.',
        'ar': 'قسم الإحصائيات: يعرض تقارير بيانية عن قاعدة البيانات والمستخدمين.\nEsc للعودة للقائمة.',
        'en': 'Statistics: graphical reports on recipes and users.\nEsc - Back to menu.'
    },
    'help_cuisines': {
        'ru': 'Справочник мировых кухонь: выберите кухню для просмотра краткой справки и списка её блюд.\nEsc - Назад в меню.',
        'ar': 'دليل المطابخ العالمية: اختر المطبخ لعرض نبذة عنه وقائمة أكلاته.\nEsc للعودة للقائمة.',
        'en': 'World cuisines directory: select a cuisine to view its description and dishes.\nEsc - Back to menu.'
    },
    'help_users': {
        'ru': 'Управление пользователями: здесь вы можете добавлять и удалять пользователей.\nEsc - Назад в меню.',
        'ar': 'إدارة المستخدمين: يمكنك إضافة وحذف المستخدمين.\nEsc للعودة للقائمة.',
        'en': 'User management: add and remove users.\nEsc - Back to menu.'
    },

    # ==================== Подтверждения (Confirmations) ====================
    'confirm_delete_title': {
        'ru': 'Подтверждение удаления',
        'ar': 'تأكيد الحذف',
        'en': 'Confirm Deletion'
    },
    'confirm_delete_msg': {
        'ru': 'Пожалуйста, подтвердите: вы уверены, что хотите удалить эту запись? Она будет перемещена в архив.',
        'ar': 'من فضلك أكد: هل أنت متأكد من حذف هذا السجل؟ سيتم نقله للأرشيف.',
        'en': 'Please confirm: are you sure you want to delete this record? It will be moved to the archive.'
    },
    'success_save': {
        'ru': 'Данные успешно сохранены. Благодарим за использование системы!',
        'ar': 'تم حفظ البيانات بنجاح. شكراً لاستخدامك نظامنا!',
        'en': 'Data saved successfully. Thank you for using the system!'
    },

    # ==================== Статистика (Stats sub-headers) ====================
    'stat_col_cuisine': {
        'ru': 'Кухня',
        'ar': 'المطبخ',
        'en': 'Cuisine'
    },
    'stat_col_count': {
        'ru': 'Кол-во',
        'ar': 'العدد',
        'en': 'Count'
    },
    'stat_col_avg_cal': {
        'ru': 'Avg калории',
        'ar': 'متوسط السعرات',
        'en': 'Avg Calories'
    },
    'stat_col_avg_time': {
        'ru': 'Avg время (мин)',
        'ar': 'متوسط الوقت (دقيقة)',
        'en': 'Avg Time (min)'
    },
    'stat_col_type': {
        'ru': 'Вид рецепта',
        'ar': 'نوع الوصفة',
        'en': 'Recipe Type'
    },
    'stat_col_time_min': {
        'ru': 'Время (мин)',
        'ar': 'الوقت (دقيقة)',
        'en': 'Time (min)'
    },
    'cal_error_min': {
        'ru': 'Минимальные калории должны быть числом',
        'ar': 'الحد الأدنى للسعرات يجب أن يكون رقماً',
        'en': 'Minimum calories must be a number'
    },
    'cal_error_max': {
        'ru': 'Максимальные калории должны быть числом',
        'ar': 'الحد الأقصى للسعرات يجب أن يكون رقماً',
        'en': 'Maximum calories must be a number'
    },
    'recipe_saved_to_file': {
        'ru': 'Рецепт сохранён в файл:\n{path}',
        'ar': 'تم حفظ الوصفة في ملف:\n{path}',
        'en': 'Recipe saved to file:\n{path}'
    },
    'save_recipe_to_file': {
        'ru': 'Сохранить рецепт в файл',
        'ar': 'حفظ الوصفة في ملف',
        'en': 'Save recipe to file'
    },
    'calculator_unavailable': {
        'ru': 'Окно калькулятора недоступно.',
        'ar': 'نافذة الحاسبة غير متاحة.',
        'en': 'Calculator window is unavailable.'
    },
}
