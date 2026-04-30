import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# ---------- Класс конвертера валют ----------
class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("750x550")
        self.root.resizable(False, False)

        # API настройки (бесплатный API exchangerate-api.com)
        self.api_url = "https://api.exchangerate-api.com/v4/latest/"

        # Данные валют и курсов
        self.currencies = []
        self.exchange_rates = {}
        self.history = []

        # Загрузка истории из файла
        self.load_history()

        # Создание интерфейса
        self.create_widgets()

        # Загрузка доступных валют
        self.fetch_currencies()

    # ---------- Внешнее API ----------
    def fetch_currencies(self):
        """Получение списка доступных валют и курсов"""
        try:
            response = requests.get(self.api_url + "USD", timeout=10)
            response.raise_for_status()
            data = response.json()
            self.exchange_rates = data["rates"]
            self.currencies = sorted(self.exchange_rates.keys())

            # Обновление выпадающих списков
            self.from_currency_combo['values'] = self.currencies
            self.to_currency_combo['values'] = self.currencies

            # Установка значений по умолчанию
            if "USD" in self.currencies:
                self.from_currency_combo.set("USD")
            if "EUR" in self.currencies:
                self.to_currency_combo.set("EUR")

            self.status_label.config(text="Курсы валют успешно загружены", foreground="green")
        except requests.exceptions.RequestException as e:
            self.status_label.config(text=f"Ошибка API: {e}", foreground="red")
            messagebox.showerror("Ошибка", f"Не удалось загрузить курсы валют.\n{e}")

    def convert_currency(self):
        """Конвертация суммы из одной валюты в другую"""
        # Проверка корректности ввода суммы
        amount_str = self.amount_entry.get().strip()
        if not amount_str:
            messagebox.showwarning("Внимание", "Введите сумму для конвертации")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Внимание", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showwarning("Внимание", "Сумма должна быть числом")
            return

        from_currency = self.from_currency_combo.get()
        to_currency = self.to_currency_combo.get()

        if not from_currency or not to_currency:
            messagebox.showwarning("Внимание", "Выберите валюты")
            return

        # Проверка наличия курсов
        if not self.exchange_rates:
            messagebox.showwarning("Внимание", "Курсы валют не загружены")
            self.fetch_currencies()
            return

        try:
            # Конвертация через USD как базовую валюту
            if from_currency == "USD":
                rate_from = 1
            else:
                rate_from = self.exchange_rates.get(from_currency, 0)

            if to_currency == "USD":
                rate_to = 1
            else:
                rate_to = self.exchange_rates.get(to_currency, 0)

            if rate_from == 0 or rate_to == 0:
                messagebox.showerror("Ошибка", "Курс для выбранной валюты не найден")
                return

            # Итоговая сумма
            usd_amount = amount / rate_from
            converted_amount = usd_amount * rate_to

            # Форматирование результата
            result_text = f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}"
            self.result_label.config(text=result_text)

            # Добавление в историю
            history_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "from_currency": from_currency,
                "to_currency": to_currency,
                "amount": amount,
                "converted_amount": round(converted_amount, 2),
                "rate": round(rate_to / rate_from, 4)
            }
            self.history.insert(0, history_entry)  # Новые записи сверху
            self.update_history_table()
            self.save_history()

            self.status_label.config(text="Конвертация выполнена", foreground="green")
        except Exception as e:
            self.status_label.config(text=f"Ошибка конвертации: {e}", foreground="red")
            messagebox.showerror("Ошибка", f"Ошибка при конвертации:\n{e}")

    # ---------- История (JSON) ----------
    def load_history(self):
        """Загрузка истории из JSON файла"""
        history_file = "conversion_history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.history = []
                print(f"Ошибка загрузки истории: {e}")
        else:
            self.history = []

    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open("conversion_history.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Ошибка сохранения истории: {e}")

    def update_history_table(self):
        """Обновление таблицы истории"""
        # Очистка таблицы
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        # Добавление записей
        for entry in self.history:
            self.history_tree.insert("", "end", values=(
                entry["timestamp"],
                f"{entry['amount']} {entry['from_currency']}",
                f"{entry['converted_amount']} {entry['to_currency']}",
                entry["rate"]
            ))

    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю конвертаций?"):
            self.history = []
            self.update_history_table()
            self.save_history()
            self.status_label.config(text="История очищена", foreground="blue")

    # ---------- GUI ----------
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Блок ввода ---
        ttk.Label(main_frame, text="Конвертер валют", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

        # Сумма
        ttk.Label(main_frame, text="Сумма:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.amount_entry = ttk.Entry(main_frame, width=15, font=("Arial", 12))
        self.amount_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.amount_entry.insert(0, "1.00")

        # Из валюты
        ttk.Label(main_frame, text="Из валюты:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.from_currency_combo = ttk.Combobox(main_frame, width=10, values=[], state="readonly")
        self.from_currency_combo.grid(row=2, column=1, sticky=tk.W, pady=5)

        # В валюту
        ttk.Label(main_frame, text="В валюту:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.to_currency_combo = ttk.Combobox(main_frame, width=10, values=[], state="readonly")
        self.to_currency_combo.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Кнопка конвертации
        self.convert_btn = ttk.Button(main_frame, text="Конвертировать", command=self.convert_currency)
        self.convert_btn.grid(row=4, column=0, columnspan=2, pady=15)

        # Результат
        self.result_label = ttk.Label(main_frame, text="", font=("Arial", 12, "bold"), foreground="blue")
        self.result_label.grid(row=5, column=0, columnspan=2, pady=5)

        # Статус
        self.status_label = ttk.Label(main_frame, text="Готово", foreground="gray")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)

        # --- Блок истории ---
        history_frame = ttk.LabelFrame(self.root, text="История конвертаций", padding="5")
        history_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        # Таблица истории
        columns = ("Время", "От", "Результат", "Курс")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=20)
        self.history_tree.heading("Время", text="Время")
        self.history_tree.heading("От", text="От")
        self.history_tree.heading("Результат", text="Результат")
        self.history_tree.heading("Курс", text="Курс")
        self.history_tree.column("Время", width=140)
        self.history_tree.column("От", width=100)
        self.history_tree.column("Результат", width=120)
        self.history_tree.column("Курс", width=80)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Кнопка очистки истории
        clear_btn = ttk.Button(history_frame, text="Очистить историю", command=self.clear_history)
        clear_btn.grid(row=1, column=0, pady=10)

        # Заполнение таблицы
        self.update_history_table()


# ---------- Запуск приложения ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()