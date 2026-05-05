import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

# --- НАСТРОЙКИ ---
DATA_FILE = "weather.json"  # Файл будет создан в той же папке, что и скрипт

# --- ЗАГРУЗКА ДАННЫХ ---
def load_data():
    """Загружает записи из JSON-файла. Если файла нет, возвращает пустой список."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_data(data):
    """Сохраняет список записей в JSON-файл с обработкой ошибок."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл:\n{str(e)}")

# --- ОСНОВНОЕ ОКНО ---
root = tk.Tk()
root.title("Дневник погоды")
root.geometry("750x600")

# Список для хранения данных в памяти программы
data = load_data()

# --- ФУНКЦИИ ЛОГИКИ ---
def add_record():
    """Добавляет новую запись после полной проверки всех полей."""
    date = entry_date.get().strip()
    temp = entry_temp.get().strip()
    desc = entry_desc.get().strip()
    precip = var_precip.get() == 1

    # Проверка на пустые обязательные поля
    if not date:
        messagebox.showerror("Ошибка", "Поле 'Дата' не может быть пустым.")
        return
    if not temp:
        messagebox.showerror("Ошибка", "Поле 'Температура' не может быть пустым.")
        return
    if not desc:
        messagebox.showerror("Ошибка", "Поле 'Описание' не может быть пустым.")
        return

    # Валидация даты (ГГГГ-ММ-ДД)
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Ошибка", "Неверный формат даты.\nИспользуйте формат: ГГГГ-ММ-ДД (например, 2024-05-07).")
        return

    # Валидация температуры (должно быть числом)
    try:
        temp_float = float(temp)
    except ValueError:
        messagebox.showerror("Ошибка", "Температура должна быть числом.\nИспользуйте точку для дробных значений (например, 15.5).")
        return

    # Если все проверки пройдены - создаем запись
    record = {
        "date": date,
        "temp": temp_float,
        "desc": desc,
        "precip": precip
    }

    data.append(record)
    save_data(data)
    update_listbox() # Обновляем полный список
    clear_entries()

def clear_entries():
    """Очищает поля ввода после добавления записи."""
    entry_date.delete(0, tk.END)
    entry_temp.delete(0, tk.END)
    entry_desc.delete(0, tk.END)
    var_precip.set(0)

def update_listbox(records=None, filter_func=None):
    """
    Обновляет список записей в окне.
    Всегда работает с исходным списком данных 'data', если не передан другой.
    """
    listbox.delete(0, tk.END)
    
    # Если список не передан извне, берем глобальный 'data'
    if records is None:
        records = data
    
    # Применяем фильтр, если он указан
    if filter_func:
        records_to_show = [r for r in records if filter_func(r)]
    else:
        records_to_show = records

    if not records_to_show:
        listbox.insert(tk.END, "Записей нет или они не соответствуют фильтру.")
        return

    for r in records_to_show:
        precip_str = "Осадки" if r["precip"] else "Без осадков"
        listbox.insert(tk.END, f"{r['date']} | {r['temp']}°C | {r['desc']} | {precip_str}")

def filter_by_date():
    """Фильтрует записи по конкретной дате."""
    target_date = entry_filter_date.get().strip()
    
    if not target_date:
        messagebox.showerror("Ошибка", "Введите дату для поиска.")
        return

    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Ошибка", "Неверный формат даты для поиска.\nИспользуйте: ГГГГ-ММ-ДД")
        return

    # Передаем полный список 'data' и функцию-фильтр
    update_listbox(records=data, filter_func=lambda r: r["date"] == target_date)

def filter_by_temp():
    """Фильтрует записи по температуре (выше заданной)."""
    threshold_text = entry_filter_temp.get().strip()
    
    if not threshold_text:
        messagebox.showerror("Ошибка", "Введите температуру для поиска.")
        return

    try:
        threshold = float(threshold_text)
    except ValueError:
        messagebox.showerror("Ошибка", "Порог температуры должен быть числом.")
        return
    
    # Передаем полный список 'data' и функцию-фильтр
    update_listbox(records=data, filter_func=lambda r: r["temp"] > threshold)

# --- СОЗДАНИЕ ВИДЖЕТОВ (ИНТЕРФЕЙС) ---

# Блок 1: Ввод данных
tk.Label(root, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_date = tk.Entry(root, width=20)
entry_date.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Температура:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_temp = tk.Entry(root, width=20)
entry_temp.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Описание:", font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_desc = tk.Entry(root, width=30)
entry_desc.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Осадки:", font=("Arial", 10)).grid(row=3, column=0, padx=5, pady=5, sticky="e")
var_precip = tk.IntVar()
tk.Checkbutton(root, variable=var_precip).grid(row=3, column=1, padx=5, pady=5)

tk.Button(root, text="Добавить запись", bg="#4CAF50", fg="white", command=add_record).grid(row=4, columnspan=2, pady=10)

# Блок 2: Фильтрация
tk.Label(root, text="Фильтр по дате:", font=("Arial", 10)).grid(row=5, column=0, padx=5, pady=5, sticky="e")
entry_filter_date = tk.Entry(root, width=20)
entry_filter_date.grid(row=5, column=1, padx=5, pady=5)
tk.Button(root, text="Найти", command=filter_by_date).grid(row=5, column=2, padx=2)

tk.Label(root, text="Фильтр по температуре >:", font=("Arial", 10)).grid(row=6, column=0, padx=5, pady=5, sticky="e")
entry_filter_temp = tk.Entry(root, width=10)
entry_filter_temp.grid(row=6, column=1, padx=5, pady=5, sticky="w")
tk.Button(root, text="Найти", command=filter_by_temp).grid(row=6, column=2, padx=2)

# Блок 3: Список записей
listbox = tk.Listbox(root, width=70, height=18)
listbox.grid(row=7, columnspan=3, padx=10, pady=(0, 10))
update_listbox() # Загружаем данные при старте окна

root.mainloop()