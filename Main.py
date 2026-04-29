import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Личные расходы")
        self.root.geometry("900x600")
        
        # Файл для хранения данных
        self.data_file = "expenses.json"
        self.expenses = []
        
        # Загрузка существующих данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        # Основной фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление расхода", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле для суммы
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Поле для категории
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                          values=["Еда", "Транспорт", "Развлечения", 
                                                 "Жильё", "Медицина", "Одежда", "Другое"], 
                                          width=15)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set("Еда")
        
        # Поле для даты
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_button.grid(row=0, column=6, padx=10, pady=5)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по категории
        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                 values=["Все", "Еда", "Транспорт", "Развлечения", 
                                                        "Жильё", "Медицина", "Одежда", "Другое"],
                                                 width=15)
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_category_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_var = tk.StringVar(value="Все")
        self.filter_date_combo = ttk.Combobox(filter_frame, textvariable=self.filter_date_var,
                                             values=["Все", "Сегодня", "Эта неделя", "Этот месяц", "Этот год"],
                                             width=15)
        self.filter_date_combo.grid(row=0, column=3, padx=5, pady=5)
        self.filter_date_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        # Кнопка сброса фильтров
        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).grid(row=0, column=4, padx=10, pady=5)
        
        # Фрейм для статистики
        stats_frame = ttk.LabelFrame(self.root, text="Статистика", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        # Выбор периода для подсчёта суммы
        ttk.Label(stats_frame, text="Период для подсчёта:").grid(row=0, column=0, padx=5, pady=5)
        
        # Начальная дата
        ttk.Label(stats_frame, text="с (ГГГГ-ММ-ДД):").grid(row=0, column=1, padx=5, pady=5)
        self.period_start = ttk.Entry(stats_frame, width=12)
        self.period_start.grid(row=0, column=2, padx=5, pady=5)
        self.period_start.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Конечная дата
        ttk.Label(stats_frame, text="по (ГГГГ-ММ-ДД):").grid(row=0, column=3, padx=5, pady=5)
        self.period_end = ttk.Entry(stats_frame, width=12)
        self.period_end.grid(row=0, column=4, padx=5, pady=5)
        self.period_end.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Кнопка подсчёта
        ttk.Button(stats_frame, text="Подсчитать сумму", command=self.calculate_sum).grid(row=0, column=5, padx=10, pady=5)
        
        # Метка для отображения суммы
        self.sum_label = ttk.Label(stats_frame, text="Общая сумма: 0 руб.", font=("Arial", 10, "bold"))
        self.sum_label.grid(row=0, column=6, padx=20, pady=5)
        
        # Таблица для отображения расходов
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание Treeview
        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Сумма", text="Сумма (руб.)")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        
        self.tree.column("ID", width=50)
        self.tree.column("Сумма", width=100)
        self.tree.column("Категория", width=120)
        self.tree.column("Дата", width=120)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="Удалить выбранную запись", command=self.delete_expense).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_from_json).pack(side="left", padx=5)
    
    def add_expense(self):
        """Добавление нового расхода"""
        # Проверка суммы
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму (число)!")
            return
        
        # Проверка категории
        category = self.category_var.get()
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию!")
            return
        
        # Проверка даты
        date = self.date_entry.get()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        # Создание записи
        expense_id = len(self.expenses) + 1
        expense = {
            "id": expense_id,
            "amount": amount,
            "category": category,
            "date": date
        }
        
        self.expenses.append(expense)
        self.save_data()
        self.refresh_table()
        self.amount_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Расход успешно добавлен!")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        # Получение ID выбранной записи
        item = self.tree.item(selected[0])
        expense_id = int(item['values'][0])
        
        # Удаление из списка
        self.expenses = [e for e in self.expenses if e['id'] != expense_id]
        
        # Перенумерация ID
        for i, expense in enumerate(self.expenses, 1):
            expense['id'] = i
        
        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Запись удалена!")
    
    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение фильтров
        category_filter = self.filter_category_var.get()
        date_filter = self.filter_date_var.get()
        
        # Фильтрация данных
        filtered_expenses = self.expenses.copy()
        
        # Фильтр по категории
        if category_filter != "Все":
            filtered_expenses = [e for e in filtered_expenses if e['category'] == category_filter]
        
        # Фильтр по дате
        if date_filter != "Все":
            current_date = datetime.now()
            filtered_expenses = [e for e in filtered_expenses if self.check_date_filter(e['date'], date_filter, current_date)]
        
        # Добавление в таблицу
        for expense in filtered_expenses:
            self.tree.insert("", "end", values=(expense['id'], f"{expense['amount']:.2f}", 
                                               expense['category'], expense['date']))
    
    def check_date_filter(self, expense_date, date_filter, current_date):
        """Проверка соответствия даты фильтру"""
        exp_date = datetime.strptime(expense_date, "%Y-%m-%d")
        
        if date_filter == "Сегодня":
            return exp_date.date() == current_date.date()
        elif date_filter == "Эта неделя":
            week_start = current_date - datetime.timedelta(days=current_date.weekday())
            week_end = week_start + datetime.timedelta(days=6)
            return week_start.date() <= exp_date.date() <= week_end.date()
        elif date_filter == "Этот месяц":
            return exp_date.year == current_date.year and exp_date.month == current_date.month
        elif date_filter == "Этот год":
            return exp_date.year == current_date.year
        
        return True
    
    def calculate_sum(self):
        """Подсчёт суммы расходов за выбранный период"""
        start_date = self.period_start.get()
        end_date = self.period_end.get()
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start > end:
                messagebox.showerror("Ошибка", "Начальная дата не может быть позже конечной!")
                return
            
            total = 0
            for expense in self.expenses:
                exp_date = datetime.strptime(expense['date'], "%Y-%m-%d")
                if start <= exp_date <= end:
                    total += expense['amount']
            
            self.sum_label.config(text=f"Общая сумма: {total:.2f} руб.")
            messagebox.showinfo("Результат", f"Сумма расходов за период {start_date} - {end_date}: {total:.2f} руб.")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
    
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_category_var.set("Все")
        self.filter_date_var.set("Все")
        self.refresh_table()
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
                self.expenses = []
        else:
            self.expenses = []
    
    def save_to_json(self):
        """Ручное сохранение в JSON"""
        self.save_data()
        messagebox.showinfo("Успех", f"Данные сохранены в файл {self.data_file}")
    
    def load_from_json(self):
        """Ручная загрузка из JSON"""
        self.load_data()
        self.refresh_table()
        messagebox.showinfo("Успех", f"Данные загружены из файла {self.data_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()