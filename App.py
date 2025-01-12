import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import asyncio
from checker import GrammarChecker
from utils import get_error_description

class GrammarCheckerApp:
    """
    Графический интерфейс для проверки грамматических и орфографических ошибок.
    """

    def __init__(self, root: tk.Tk, loop: asyncio.AbstractEventLoop) -> None:
        """
        Инициализирует графический интерфейс.

        Аргументы:
            root (tk.Tk): Корневое окно приложения.
            loop (asyncio.AbstractEventLoop): Цикл событий asyncio.
        """
        self.root = root
        self.loop = loop
        self.root.title("Проверка грамматики и орфографии")
        self.root.geometry("600x400")

        # Меню
        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Открыть файл", command=self.open_file)
        self.file_menu.add_command(label="Сохранить результаты", command=self.save_results)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

        # Поле для ввода текста
        self.input_label = tk.Label(root, text="Введите текст для проверки:")
        self.input_label.pack(pady=5)

        self.input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=10)
        self.input_text.pack(pady=5)

        # Кнопка для проверки текста
        self.check_button = tk.Button(root, text="Проверить текст", command=self.start_check_text)
        self.check_button.pack(pady=10)

        # Поле для вывода результатов
        self.output_label = tk.Label(root, text="Результаты проверки:")
        self.output_label.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=10, state="disabled")
        self.output_text.pack(pady=5)

        # Кнопка для выхода из приложения
        self.exit_button = tk.Button(root, text="Выход", command=self.exit_app)
        self.exit_button.pack(pady=10)

    def open_file(self) -> None:
        """
        Открывает текстовый файл и загружает его содержимое в поле ввода.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, file.read())

    def save_results(self) -> None:
        """
        Сохраняет результаты проверки в файл.
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.output_text.get("1.0", tk.END))

    def start_check_text(self) -> None:
        """
        Запускает асинхронную проверку текста.
        """
        # Получаем текст из поля ввода
        text = self.input_text.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Ошибка", "Введите текст для проверки.")
            return

        # Отключаем кнопку проверки на время выполнения
        self.check_button.config(state="disabled")
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Проверка текста...")
        self.output_text.config(state="disabled")

        # Запускаем асинхронную проверку
        asyncio.run_coroutine_threadsafe(self.check_text_async(text), self.loop)

    async def check_text_async(self, text: str) -> None:
        """
        Асинхронно проверяет текст и выводит результаты.
        """
        # Проверяем текст
        checker = GrammarChecker(text)
        await checker.check_text()  # Используем await для асинхронного вызова
        errors = checker.get_errors()

        # Выводим результаты
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)

        if not errors:
            self.output_text.insert(tk.END, "Ошибок не найдено.")
        else:
            self.output_text.insert(tk.END, f"Найдено {len(errors)} ошибок:\n\n")
            for error in errors:
                self.output_text.insert(tk.END, f"  - Ошибка: '{error['word']}' (позиция: {error['pos']})\n")
                self.output_text.insert(tk.END, f"    Возможные исправления: {', '.join(error['s'])}\n")
                self.output_text.insert(tk.END, f"    Рекомендация: {error['code']} - {get_error_description(error['code'])}\n\n")

        self.output_text.config(state="disabled")
        self.check_button.config(state="normal")

    def exit_app(self) -> None:
        """
        Завершает работу приложения.
        """
        self.loop.stop()  # Останавливаем цикл событий asyncio
        self.root.quit()  # Завершаем цикл событий tkinter
        self.root.destroy()  # Уничтожаем окно


def main() -> None:
    """
    Основная функция для запуска приложения.
    """
    root = tk.Tk()
    loop = asyncio.new_event_loop()  # Создаем новый цикл событий asyncio
    app = GrammarCheckerApp(root, loop)

    # Запускаем цикл событий asyncio в отдельном потоке
    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    import threading
    threading.Thread(target=run_loop, daemon=True).start()

    # Запускаем цикл событий tkinter
    root.mainloop()

    # Останавливаем цикл событий asyncio после завершения tkinter
    loop.stop()


if __name__ == "__main__":
    main()