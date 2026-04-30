import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Управление прочитанными книгами")
        self.root.geometry("900x600")

        # Загрузка данных из JSON
        self.books = []
        self.load_data()

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_view()
        self.create_button_frame()

        # Обновление таблицы
        self.refresh_treeview()

    def create_input_frame(self):
        """Создание формы для ввода данных книги"""
        input_frame = tk.LabelFrame(self.root, text="Добавление новой книги", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поле: Название книги
        tk.Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_entry = tk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поле: Автор
        tk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.author_entry = tk.Entry(input_frame, width=30)
        self.author_entry.grid(row=1, column=1, padx=5, pady=5)

        # Поле: Жанр
        tk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.genre_entry = tk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=2, column=1, padx=5, pady=5)

        # Поле: Количество страниц
        tk.Label(input_frame, text="Количество страниц:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.pages_entry = tk.Entry(input_frame, width=30)
        self.pages_entry.grid(row=3, column=1, padx=5, pady=5)

        # Кнопка добавления
        self.add_button = tk.Button(input_frame, text="➕ Добавить книгу", command=self.add_book,
                                    bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

    def create_filter_frame(self):
        """Создание фильтров"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        tk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_genre_var = tk.StringVar(value="Все")
        self.filter_genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var,
                                               values=["Все"], state="readonly", width=20)
        self.filter_genre_combo.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по количеству страниц
        tk.Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_pages_var = tk.StringVar(value="0")
        self.filter_pages_entry = tk.Entry(filter_frame, textvariable=self.filter_pages_var, width=10)
        self.filter_pages_entry.grid(row=0, column=3, padx=5, pady=5)

        # Кнопка применения фильтра
        self.filter_button = tk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter,
                                       bg="#2196F3", fg="white")
        self.filter_button.grid(row=0, column=4, padx=10, pady=5)

        # Кнопка сброса фильтра
        self.reset_filter_button = tk.Button(filter_frame, text="🗑️ Сбросить фильтр", command=self.reset_filter,
                                             bg="#FF9800", fg="white")
        self.reset_filter_button.grid(row=0, column=5, padx=5, pady=5)

    def create_tree_view(self):
        """Создание таблицы для отображения книг"""
        # Фрейм для таблицы и скроллбара
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание скроллбаров
        scroll_y = tk.Scrollbar(tree_frame, orient="vertical")
        scroll_x = tk.Scrollbar(tree_frame, orient="horizontal")

        # Создание таблицы
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Название", "Автор", "Жанр", "Страниц"),
                                 show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название книги")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Страниц", text="Страниц")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Название", width=250)
        self.tree.column("Автор", width=200)
        self.tree.column("Жанр", width=150)
        self.tree.column("Страниц", width=100, anchor="center")

        # Настройка скроллбаров
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Размещение элементов
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        # Привязка двойного клика для удаления
        self.tree.bind("<Double-1>", self.delete_book)

    def create_button_frame(self):
        """Создание кнопок управления"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)

        self.save_button = tk.Button(button_frame, text="💾 Сохранить в JSON", command=self.save_data,
                                     bg="#9C27B0", fg="white", font=("Arial", 10, "bold"))
        self.save_button.pack(side="left", padx=5)

        self.load_button = tk.Button(button_frame, text="📂 Загрузить из JSON", command=self.load_data,
                                     bg="#607D8B", fg="white", font=("Arial", 10, "bold"))
        self.load_button.pack(side="left", padx=5)

        self.stats_button = tk.Button(button_frame, text="📊 Статистика", command=self.show_stats,
                                      bg="#FF5722", fg="white")
        self.stats_button.pack(side="left", padx=5)

        self.exit_button = tk.Button(button_frame, text="❌ Выход", command=self.root.quit,
                                     bg="#F44336", fg="white")
        self.exit_button.pack(side="right", padx=5)

    def add_book(self):
        """Добавление новой книги с проверкой ввода"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages = self.pages_entry.get().strip()

        # Проверка на пустые поля
        if not title or not author or not genre or not pages:
            messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля!")
            return

        # Проверка, что количество страниц - число
        try:
            pages = int(pages)
            if pages <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
            return

        # Создание ID для книги
        book_id = max([book["id"] for book in self.books] + [0]) + 1

        # Добавление книги
        book = {
            "id": book_id,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.books.append(book)

        # Очистка полей ввода
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

        # Обновление фильтра жанров
        self.update_genre_filter()

        # Обновление таблицы
        self.refresh_treeview()

        messagebox.showinfo("Успех", f"Книга \"{title}\" успешно добавлена!")

    def delete_book(self, event):
        """Удаление книги по двойному клику"""
        selected = self.tree.selection()
        if not selected:
            return

        # Получение ID книги
        item = self.tree.item(selected[0])
        book_id = int(item['values'][0])

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Удалить книгу \"{item['values'][1]}\"?"):
            self.books = [book for book in self.books if book["id"] != book_id]
            self.update_genre_filter()
            self.refresh_treeview()
            messagebox.showinfo("Успех", "Книга удалена!")

    def apply_filter(self):
        """Применение фильтров"""
        genre_filter = self.filter_genre_var.get()
        pages_filter = self.filter_pages_var.get().strip()

        # Проверка фильтра страниц
        try:
            pages_threshold = int(pages_filter) if pages_filter else 0
        except ValueError:
            messagebox.showerror("Ошибка", "Фильтр по страницам должен быть числом!")
            return

        # Применение фильтров
        filtered_books = self.books.copy()

        if genre_filter != "Все":
            filtered_books = [book for book in filtered_books if book["genre"] == genre_filter]

        if pages_threshold > 0:
            filtered_books = [book for book in filtered_books if book["pages"] > pages_threshold]

        self.display_books(filtered_books)

    def reset_filter(self):
        """Сброс всех фильтров"""
        self.filter_genre_var.set("Все")
        self.filter_pages_var.set("0")
        self.refresh_treeview()

    def refresh_treeview(self):
        """Обновление таблицы с учетом фильтров"""
        self.apply_filter()

    def display_books(self, books_to_display):
        """Отображение книг в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление книг
        for book in books_to_display:
            self.tree.insert("", "end", values=(
                book["id"],
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

    def update_genre_filter(self):
        """Обновление списка жанров в фильтре"""
        genres = list(set([book["genre"] for book in self.books]))
        genres.sort()
        genres.insert(0, "Все")
        self.filter_genre_combo['values'] = genres

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open("books.json", "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Данные успешно сохранены в books.json!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if not os.path.exists("books.json"):
            return

        try:
            with open("books.json", "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.update_genre_filter()
            self.refresh_treeview()
            messagebox.showinfo("Успех", f"Загружено {len(self.books)} книг!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def show_stats(self):
        """Отображение статистики"""
        if not self.books:
            messagebox.showinfo("Статистика", "Нет добавленных книг.")
            return

        total_books = len(self.books)
        total_pages = sum(book["pages"] for book in self.books)
        avg_pages = total_pages / total_books if total_books > 0 else 0

        # Статистика по жанрам
        genres_count = {}
        for book in self.books:
            genres_count[book["genre"]] = genres_count.get(book["genre"], 0) + 1

        most_popular_genre = max(genres_count, key=genres_count.get) if genres_count else "Нет"

        stats_text = f"""📊 Статистика книг:

📚 Всего книг: {total_books}
📖 Всего страниц: {total_pages}
📈 Среднее кол-во страниц: {avg_pages:.1f}
🎭 Самый популярный жанр: {most_popular_genre} ({genres_count.get(most_popular_genre, 0)} книг)

Жанры:
{chr(10).join([f"   • {genre}: {count} книг" for genre, count in genres_count.items()])}
"""

        messagebox.showinfo("Статистика", stats_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()