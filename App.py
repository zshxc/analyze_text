import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import asyncio
from checker import GrammarChecker
from utils import get_error_description

class GrammarCheckerApp:

    def __init__(self, root: tk.Tk, loop: asyncio.AbstractEventLoop) -> None: # инициализация графики

        self.root = root
        self.loop = loop
        self.root.title("Проверка грамматики и орфографии")
        self.root.geometry("600x400")

        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Открыть файл (TXT)", command=lambda: self.open_file("txt"))
        self.file_menu.add_command(label="Сохранить результаты", command=self.save_results)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

        self.input_label = tk.Label(root, text="Введите текст для проверки:")
        self.input_label.pack(pady=5)

        self.input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=10)
        self.input_text.pack(pady=5)

        self.input_text.tag_configure("error", foreground="red", underline=True)

        self.check_button = tk.Button(root, text="Проверить текст", command=self.start_check_text)
        self.check_button.pack(pady=10)

        self.fix_button = tk.Button(root, text="Исправить всё", command=self.fix_all_errors, state="disabled")
        self.fix_button.pack(pady=10)

        self.output_label = tk.Label(root, text="Результаты проверки:")
        self.output_label.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=10, state="disabled")
        self.output_text.pack(pady=5)

        self.exit_button = tk.Button(root, text="Выход", command=self.exit_app)
        self.exit_button.pack(pady=10)

        self.errors = []

    def open_file(self, file_type: str) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.input_text.delete("1.0", tk.END)
                    self.input_text.insert(tk.END, file.read())
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def save_results(self) -> None:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt")]) #открывает диалог о сохраненгии файла
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.output_text.get("1.0", tk.END))

    def start_check_text(self) -> None:
        # Получаем текст из ввода
        text = self.input_text.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Ошибка", "Введите текст для проверки.")
            return

        # Отключаем кнопки на время выполнения
        self.check_button.config(state="disabled")
        self.fix_button.config(state="disabled")
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Проверка текста...")
        self.output_text.config(state="disabled")

        # Запускаем асинхронную проверку
        asyncio.run_coroutine_threadsafe(self.check_text_async(text), self.loop)

    async def check_text_async(self, text: str) -> None:

        checker = GrammarChecker(text)
        await checker.check_text()  # Асинхронный запрос
        self.errors = checker.get_errors()

        # Очищение предыдущих выделений
        self.input_text.tag_remove("error", "1.0", tk.END)

        # Выводим результаты
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)

        if not self.errors:
            self.output_text.insert(tk.END, "Ошибок не найдено.")
        else:
            self.output_text.insert(tk.END, f"Найдено {len(self.errors)} ошибок:\n\n")
            for error in self.errors:
                # Подсвечиваем ошибки в поле ввода
                start_index = f"1.0+{error['pos']}c"
                end_index = f"1.0+{error['pos'] + len(error['word'])}c"
                self.input_text.tag_add("error", start_index, end_index)

                # вывод error
                self.output_text.insert(tk.END, f"  - Ошибка: '{error['word']}' (позиция: {error['pos']})\n")
                self.output_text.insert(tk.END, f"    Возможные исправления: {', '.join(error['s'])}\n")
                self.output_text.insert(tk.END, f"    Рекомендация: {error['code']} - {get_error_description(error['code'])}\n\n")

        self.output_text.config(state="disabled")
        self.check_button.config(state="normal")
        self.fix_button.config(state="normal" if self.errors else "disabled")

    def fix_all_errors(self) -> None: # автоматический фикс ошибок
  
        if not self.errors:
            return

        text = self.input_text.get("1.0", tk.END)
        text_list = list(text)  # Преобразание текста в массив

        # фиксим ошибки, начиная с конца, дабы не сбивать позиции
        for error in reversed(self.errors):
            start_pos = error["pos"]
            end_pos = start_pos + len(error["word"])
            if error["s"]:  # Если есть предложенные исправления
                text_list[start_pos:end_pos] = error["s"][0]  # Заменяем ошибку на первое предложенное исправление

        # Обновляем текст в поле ввода
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, "".join(text_list))

        self.input_text.tag_remove("error", "1.0", tk.END) #подсветка
        self.errors = []

        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "Все ошибки исправлены.")
        self.output_text.config(state="disabled")
        self.fix_button.config(state="disabled")  #исправление ошибок

    def exit_app(self) -> None:
        self.loop.stop()
        self.root.quit()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    loop = asyncio.new_event_loop()  # новый ивент async
    app = GrammarCheckerApp(root, loop)

    # Запускаем ивент в отдельном потоке(мешается tkinter'y)
    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    import threading
    threading.Thread(target=run_loop, daemon=True).start()

    # Запускаем ивент tkinter
    root.mainloop()

    # Останавливаем ивент asyncio после завершения tkinter
    loop.stop()


if __name__ == "__main__":
    main()