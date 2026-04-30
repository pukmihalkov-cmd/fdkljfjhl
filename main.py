"""
Quote Generator — Генератор случайных цитат
Автор: Николай Сорокин
Описание: GUI-приложение для генерации случайных цитат с фильтрацией по автору и теме,
         сохранением истории и возможностью экспорта в JSON.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
import os
from datetime import datetime

# ---------- БАЗА ДАННЫХ ЦИТАТ ----------
QUOTES_DB = [
    {"text": "Будь изменением, которое хочешь увидеть в мире.", "author": "Махатма Ганди", "theme": "мотивация"},
    {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "theme": "жизнь"},
    {"text": "Не важно, как медленно ты идёшь, главное — не останавливаться.", "author": "Конфуций", "theme": "мотивация"},
    {"text": "Единственный способ делать великую работу — любить то, что ты делаешь.", "author": "Стив Джобс", "theme": "работа"},
    {"text": "Успех — это способность идти от неудачи к неудаче, не теряя энтузиазма.", "author": "Уинстон Черчилль", "theme": "успех"},
    {"text": "Будущее зависит от того, что ты делаешь сегодня.", "author": "Махатма Ганди", "theme": "мотивация"},
    {"text": "Лучший способ предсказать будущее — создать его.", "author": "Питер Друкер", "theme": "будущее"},
    {"text": "Знание — сила.", "author": "Фрэнсис Бэкон", "theme": "знание"},
    {"text": "Без труда не вытащишь и рыбку из пруда.", "author": "Народная", "theme": "мотивация"},
    {"text": "Всё гениальное — просто.", "author": "Леонардо да Винчи", "theme": "мудрость"},
    {"text": "Жизнь — как езда на велосипеде. Чтобы сохранить равновесие, нужно двигаться.", "author": "Альберт Эйнштейн", "theme": "жизнь"},
    {"text": "Никогда не поздно стать тем, кем ты мог бы быть.", "author": "Джордж Элиот", "theme": "мотивация"},
    {"text": "Мечтай так, будто жить вечно. Живи так, будто умрёшь сегодня.", "author": "Джеймс Дин", "theme": "жизнь"},
    {"text": "То, что нас не убивает, делает нас сильнее.", "author": "Фридрих Ницше", "theme": "сила"},
    {"text": "Делай, что можешь, с тем, что имеешь, там, где ты есть.", "author": "Теодор Рузвельт", "theme": "действие"},
    {"text": "Нет никаких границ. Нужно только мужество и страсть.", "author": "Ричард Брэнсон", "theme": "успех"},
    {"text": "Книги — корабли мысли.", "author": "Фрэнсис Бэкон", "theme": "знание"},
    {"text": "Сложнее всего начать действовать, остальное зависит от упорства.", "author": "Пабло Пикассо", "theme": "действие"},
    {"text": "Секрет успеха — начать.", "author": "Марк Твен", "theme": "успех"},
    {"text": "Важно не количество знаний, а качество их.", "author": "Лев Толстой", "theme": "знание"},
]

# Имена авторов (для фильтра)
AUTHORS = sorted(set(q["author"] for q in QUOTES_DB))
# Темы (для фильтра)
THEMES = sorted(set(q["theme"] for q in QUOTES_DB))


# ---------- ОСНОВНОЙ КЛАСС ПРИЛОЖЕНИЯ ----------
class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор цитат")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        # История сгенерированных цитат
        self.history = []
        self.filtered_history = []
        self.load_history()

        # Создание интерфейса
        self.create_widgets()

    # ---------- ЗАГРУЗКА/СОХРАНЕНИЕ ИСТОРИИ (JSON) ----------
    def load_history(self):
        """Загрузка истории из файла JSON"""
        history_file = "quotes_history.json"
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
        """Сохранение истории в файл JSON"""
        try:
            with open("quotes_history.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Ошибка сохранения истории: {e}")

    def update_history_display(self):
        """Обновление отображения истории (с учётом фильтрации)"""
        # Очистка таблицы
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        # Определяем, какие записи показывать
        display_list = self.filtered_history if self.filtered_history else self.history

        # Добавление записей
        for entry in display_list:
            self.history_tree.insert("", "end", values=(
                entry["timestamp"],
                entry["text"],
                entry["author"],
                entry["theme"]
            ))

        self.status_label.config(text=f"Показано {len(display_list)} из {len(self.history)} цитат")

    def add_to_history(self, quote):
        """Добавление цитаты в историю"""
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text": quote["text"],
            "author": quote["author"],
            "theme": quote["theme"]
        }
        self.history.insert(0, history_entry)  # Новая цитата сверху
        self.save_history()
        self.update_history_display()
        self.update_stats()

    def clear_history(self):
        """Очистка всей истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.filtered_history = []
            self.update_history_display()
            self.update_stats()
            self.status_label.config(text="История очищена")

    def update_stats(self):
        """Обновление статистики (всего цитат, уникальных авторов)"""
        if not self.history:
            self.stats_label.config(text="Статистика: нет данных")
            return

        total = len(self.history)
        unique_authors = len(set(q["author"] for q in self.history))
        self.stats_label.config(text=f"Статистика: всего цитат: {total} | разных авторов: {unique_authors}")

    # ---------- ФИЛЬТРАЦИЯ ----------
    def apply_filter(self):
        """Применение фильтра по автору и теме"""
        selected_author = self.filter_author_combo.get()
        selected_theme = self.filter_theme_combo.get()

        if selected_author == "Все" and selected_theme == "Все":
            # Показать всю историю
            self.filtered_history = []
            self.update_history_display()
            return

        # Фильтрация
        filtered = []
        for entry in self.history:
            author_match = (selected_author == "Все" or entry["author"] == selected_author)
            theme_match = (selected_theme == "Все" or entry["theme"] == selected_theme)
            if author_match and theme_match:
                filtered.append(entry)

        self.filtered_history = filtered
        self.update_history_display()

        if len(filtered) == 0:
            self.status_label.config(text="По вашему запросу ничего не найдено", foreground="orange")
        else:
            self.status_label.config(text=f"Найдено {len(filtered)} цитат", foreground="green")

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_author_combo.set("Все")
        self.filter_theme_combo.set("Все")
        self.filtered_history = []
        self.update_history_display()

    # ---------- ГЕНЕРАЦИЯ СЛУЧАЙНОЙ ЦИТАТЫ ----------
    def generate_quote(self):
        """Генерация случайной цитаты"""
        quote = random.choice(QUOTES_DB)
        self.display_quote(quote)
        self.add_to_history(quote)
        self.status_label.config(text="Новая цитата сгенерирована!", foreground="green")

    def display_quote(self, quote):
        """Отображение цитаты на экране"""
        self.quote_text_label.config(text=f"«{quote['text']}»")
        self.quote_author_label.config(text=f"— {quote['author']}")
        self.quote_theme_label.config(text=f"Тема: {quote['theme']}")

    # ---------- GUI (ИНТЕРФЕЙС) ----------
    def create_widgets(self):
        # Создание двух основных фреймов
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # ========== ЛЕВАЯ ЧАСТЬ ==========
        # Заголовок
        ttk.Label(left_frame, text="Генератор цитат", font=("Arial", 18, "bold")).pack(pady=10)

        # Карточка цитаты
        quote_frame = ttk.Frame(left_frame, relief=tk.RAISED, borderwidth=2)
        quote_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.quote_text_label = ttk.Label(quote_frame, text="Нажмите кнопку для генерации цитаты",
                                          font=("Arial", 14, "italic"), wraplength=350, justify=tk.CENTER)
        self.quote_text_label.pack(pady=30, padx=20)

        self.quote_author_label = ttk.Label(quote_frame, text="", font=("Arial", 12))
        self.quote_author_label.pack(pady=5)

        self.quote_theme_label = ttk.Label(quote_frame, text="", font=("Arial", 10), foreground="gray")
        self.quote_theme_label.pack(pady=5)

        # Кнопка генерации
        self.generate_btn = ttk.Button(left_frame, text="Сгенерировать цитату", command=self.generate_quote)
        self.generate_btn.pack(pady=20)

        # ========== ПРАВАЯ ЧАСТЬ ==========
        # Фильтры
        filter_frame = ttk.LabelFrame(right_frame, text="Фильтрация истории", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Автор:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filter_author_combo = ttk.Combobox(filter_frame, values=["Все"] + AUTHORS, state="readonly", width=20)
        self.filter_author_combo.set("Все")
        self.filter_author_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Тема:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.filter_theme_combo = ttk.Combobox(filter_frame, values=["Все"] + THEMES, state="readonly", width=20)
        self.filter_theme_combo.set("Все")
        self.filter_theme_combo.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Применить фильтр", command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сбросить", command=self.reset_filter).pack(side=tk.LEFT, padx=5)

        # Таблица истории
        history_frame = ttk.LabelFrame(right_frame, text="История цитат", padding="5")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("Время", "Цитата", "Автор", "Тема")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=15)
        self.history_tree.heading("Время", text="Время")
        self.history_tree.heading("Цитата", text="Цитата")
        self.history_tree.heading("Автор", text="Автор")
        self.history_tree.heading("Тема", text="Тема")

        self.history_tree.column("Время", width=130)
        self.history_tree.column("Цитата", width=300)
        self.history_tree.column("Автор", width=120)
        self.history_tree.column("Тема", width=100)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления историей
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Button(control_frame, text="Очистить историю", command=self.clear_history).pack(side=tk.LEFT, padx=5)

        # Статусная строка
        self.status_label = ttk.Label(right_frame, text="Готово", foreground="gray")
        self.status_label.pack(fill=tk.X, pady=5)

        # Статистика
        self.stats_label = ttk.Label(right_frame, text="Статистика: нет данных", font=("Arial", 9))
        self.stats_label.pack(fill=tk.X, pady=2)

        # Обновление статистики
        self.update_history_display()
        self.update_stats()


# ---------- ЗАПУСК ПРИЛОЖЕНИЯ ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()
