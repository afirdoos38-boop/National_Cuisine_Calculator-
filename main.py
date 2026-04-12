"""
main.py
Точка входа в приложение National Cuisine Calculator.
Инициализирует главное окно Tkinter и запускает основной цикл программы.
Автор: Аль-Фахдави Ф. Х.А. (Группа 841-М23)
"""
import tkinter as tk
import sys
import os

# Add root folder to sys.path if not there
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import NationalCuisineCalculator

def main():
    root = tk.Tk()                      # ← отступ
    app = NationalCuisineCalculator(root)  # ← отступ
    root.mainloop()                    # ← отступ

if __name__ == "__main__":
    main()
