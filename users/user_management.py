"""
users/user_management.py
Модуль управления пользователями. Доступен только пользователям с ролью 'admin'.
Позволяет просматривать, добавлять и удалять учетные записи из системы.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib

class UserManagement:
    def __init__(self, app):
        self.app = app

    def manage_users(self):
        """Управление пользователями (только для администратора)"""
        self.app.clear_window()
        self.app.root.geometry("800x600")

        self.app.current_frame = ttk.Frame(self.app.root, padding=20)
        self.app.current_frame.pack(fill=tk.BOTH, expand=True)
        self.app.current_frame.help_tag = 'help_users'

        ttk.Label(self.app.current_frame, text=self.app.get_text('user_mgmt_title'),
                  style='Title.TLabel').pack(pady=10)

        # Treeview с пользователями
        tree_frame = ttk.Frame(self.app.current_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns_keys = ['col_id', 'col_login', 'col_fullname', 'col_role', 'col_date']
        tree = ttk.Treeview(tree_frame, columns=columns_keys, show='headings', height=15)

        col_widths = [50, 120, 150, 100, 150]
        for key, width in zip(columns_keys, col_widths):
            tree.heading(key, text=self.app.get_text(key))
            tree.column(key, width=width, anchor=tk.CENTER)

        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=v_scroll.set)

        tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')

        def load_users():
            try:
                for item in tree.get_children():
                    tree.delete(item)

                cursor = self.app.db_connection.cursor()
                cursor.execute('''
                    SELECT id, username, full_name, role, created_at 
                    FROM users 
                    ORDER BY created_at DESC
                ''')

                for row in cursor.fetchall():
                    tree.insert('', tk.END, values=row)

                cursor.close()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки пользователей: {e}")

        def add_user():
            # Открываем диалог в отдельном окне с полями (лучше UX чем simpledialog)
            dlg = tk.Toplevel(self.app.root)
            dlg.title("Добавить пользователя")
            dlg.transient(self.app.root)
            dlg.grab_set()
            dlg.geometry("420x220")

            frm = ttk.Frame(dlg, padding=10)
            frm.pack(fill='both', expand=True)

            ttk.Label(frm, text="Логин:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
            username_var = tk.StringVar()
            username_entry = ttk.Entry(frm, textvariable=username_var, width=30)
            username_entry.grid(row=0, column=1, pady=5, padx=5)
            username_entry.focus()

            ttk.Label(frm, text="Пароль:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
            password_var = tk.StringVar()
            password_entry = ttk.Entry(frm, textvariable=password_var, show='*', width=30)
            password_entry.grid(row=1, column=1, pady=5, padx=5)

            ttk.Label(frm, text="Полное имя:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
            fullname_var = tk.StringVar()
            fullname_entry = ttk.Entry(frm, textvariable=fullname_var, width=30)
            fullname_entry.grid(row=2, column=1, pady=5, padx=5)

            ttk.Label(frm, text="Роль:").grid(row=3, column=0, sticky='w', pady=5, padx=5)
            role_var = tk.StringVar(value='user')
            role_combo = ttk.Combobox(frm, textvariable=role_var, values=['admin', 'chef', 'user'], state='readonly', width=28)
            role_combo.grid(row=3, column=1, pady=5, padx=5)

            def submit():
                username = username_var.get().strip()
                password = password_var.get()
                full_name = fullname_var.get().strip() or username
                role = role_var.get()

                if not username or not password:
                    messagebox.showerror("Ошибка", "Логин и пароль обязательны", parent=dlg)
                    return

                if role not in ['admin', 'chef', 'user']:
                    messagebox.showerror("Ошибка", "Роль должна быть: admin, chef или user", parent=dlg)
                    return

                cursor = None
                try:
                    cursor = self.app.db_connection.cursor()
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if cursor.fetchone():
                        messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует", parent=dlg)
                        return

                    hashed = self.app.db_manager.hash_password(password)
                    cursor.execute(
                        "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                        (username, hashed, full_name, role)
                    )
                    self.app.db_connection.commit()
                    messagebox.showinfo("Успех", "Пользователь добавлен", parent=dlg)
                    dlg.destroy()
                    load_users()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка добавления: {e}", parent=dlg)
                finally:
                    if cursor:
                        try:
                            cursor.close()
                        except:
                            pass

            def on_enter(event):
                submit()

            # Bind Enter для удобства
            username_entry.bind('<Return>', on_enter)
            password_entry.bind('<Return>', on_enter)
            fullname_entry.bind('<Return>', on_enter)
            role_combo.bind('<Return>', on_enter)

            btns = ttk.Frame(frm)
            btns.grid(row=4, column=0, columnspan=2, pady=10)

            ttk.Button(btns, text="Сохранить", command=submit, width=12).pack(side='left', padx=5)
            ttk.Button(btns, text="Отмена", command=dlg.destroy, width=12).pack(side='left', padx=5)

            # Сделать диалог модальным
            dlg.wait_window()

        def edit_user():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Внимание", "Выберите пользователя для редактирования")
                return

            item = tree.item(selection[0])
            user_id = item['values'][0]
            current_username = item['values'][1]
            current_fullname = item['values'][2]
            current_role = item['values'][3]

            dlg = tk.Toplevel(self.app.root)
            dlg.title("Редактировать пользователя")
            dlg.transient(self.app.root)
            dlg.grab_set()
            dlg.geometry("420x240")

            frm = ttk.Frame(dlg, padding=10)
            frm.pack(fill='both', expand=True)

            ttk.Label(frm, text="Логин:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
            username_var = tk.StringVar(value=current_username)
            username_entry = ttk.Entry(frm, textvariable=username_var, width=30)
            username_entry.grid(row=0, column=1, pady=5, padx=5)
            username_entry.focus()

            ttk.Label(frm, text="Новый пароль (оставьте пустым чтобы не менять):").grid(row=1, column=0, sticky='w', pady=5, padx=5)
            password_var = tk.StringVar()
            password_entry = ttk.Entry(frm, textvariable=password_var, show='*', width=30)
            password_entry.grid(row=1, column=1, pady=5, padx=5)

            ttk.Label(frm, text="Полное имя:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
            fullname_var = tk.StringVar(value=current_fullname)
            fullname_entry = ttk.Entry(frm, textvariable=fullname_var, width=30)
            fullname_entry.grid(row=2, column=1, pady=5, padx=5)

            ttk.Label(frm, text="Роль:").grid(row=3, column=0, sticky='w', pady=5, padx=5)
            role_var = tk.StringVar(value=current_role)
            role_combo = ttk.Combobox(frm, textvariable=role_var, values=['admin', 'chef', 'user'], state='readonly', width=28)
            role_combo.grid(row=3, column=1, pady=5, padx=5)

            def submit_edit():
                new_username = username_var.get().strip()
                new_password = password_var.get()
                new_fullname = fullname_var.get().strip() or new_username
                new_role = role_var.get()

                if not new_username:
                    messagebox.showerror("Ошибка", "Логин не может быть пустым", parent=dlg)
                    return

                if new_role not in ['admin', 'chef', 'user']:
                    messagebox.showerror("Ошибка", "Неверная роль", parent=dlg)
                    return

                # Предотвращаем понижение прав у самого себя
                if user_id == self.app.current_user['id'] and new_role != self.app.current_user['role']:
                    messagebox.showerror("Ошибка", "Нельзя изменить роль самого себя", parent=dlg)
                    return

                cursor = None
                try:
                    cursor = self.app.db_connection.cursor()
                    cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (new_username, user_id))
                    if cursor.fetchone():
                        messagebox.showerror("Ошибка", "Другой пользователь уже использует этот логин", parent=dlg)
                        return

                    # Формируем запрос обновления
                    if new_password:
                        hashed = self.app.db_manager.hash_password(new_password)
                        cursor.execute(
                            "UPDATE users SET username=?, password=?, full_name=?, role=? WHERE id=?",
                            (new_username, hashed, new_fullname, new_role, user_id)
                        )
                    else:
                        cursor.execute(
                            "UPDATE users SET username=?, full_name=?, role=? WHERE id=?",
                            (new_username, new_fullname, new_role, user_id)
                        )

                    self.app.db_connection.commit()
                    messagebox.showinfo("Успех", "Пользователь обновлен", parent=dlg)

                    # Если обновили текущего пользователя — обновим кэш
                    if user_id == self.app.current_user['id']:
                        self.app.current_user['username'] = new_username
                        self.app.current_user['full_name'] = new_fullname
                        self.app.current_user['role'] = new_role

                    dlg.destroy()
                    load_users()

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка обновления: {e}", parent=dlg)
                finally:
                    if cursor:
                        try:
                            cursor.close()
                        except:
                            pass

            def on_enter(event):
                submit_edit()

            username_entry.bind('<Return>', on_enter)
            password_entry.bind('<Return>', on_enter)
            fullname_entry.bind('<Return>', on_enter)
            role_combo.bind('<Return>', on_enter)

            btns = ttk.Frame(frm)
            btns.grid(row=4, column=0, columnspan=2, pady=10)

            ttk.Button(btns, text="Сохранить", command=submit_edit, width=12).pack(side='left', padx=5)
            ttk.Button(btns, text="Отмена", command=dlg.destroy, width=12).pack(side='left', padx=5)

            dlg.wait_window()

        def delete_user():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                user_id = item['values'][0]
                username = item['values'][1]

                if user_id == self.app.current_user['id']:
                    messagebox.showerror("Ошибка", "Нельзя удалить самого себя")
                    return

                # Requirement 1: Confirmation before data loss
                if messagebox.askyesno(self.app.get_text('confirm_delete_title'), 
                                      f"{self.app.get_text('confirm_delete_msg')}\n\n{username}"):
                    if self.app.db_manager.delete_user(user_id):
                        messagebox.showinfo("Успех", "Пользователь удален и перемещен в архив")
                        load_users()
                    else:
                        messagebox.showerror("Ошибка", "Не удалось удалить пользователя")
            else:
                messagebox.showwarning("Внимание", "Выберите пользователя")

        # Кнопки управления
        btn_frame = ttk.Frame(self.app.current_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text=self.app.get_text('menu_add_recipe'),
                   command=add_user, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.app.get_text('edit_btn'),
                   command=edit_user, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Удалить",
                   command=delete_user, style='Delete.TButton', width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.app.get_text('back'),
                   command=self.app.show_main_menu, width=15).pack(side='left', padx=5)

        load_users()

