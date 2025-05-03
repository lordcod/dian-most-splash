import logging
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os

from client import Client
from parsers.result import ResultParser
from parsers.main import FileParser
from listeners.splash import FileHandler

MAX_PATH_LENGTH = 40  # Максимальная длина пути для отображения
BTN_WIDTH = 210  # Максимальная ширина кнопок


class FileSelectionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Выбор файлов и папки")
        self.geometry("450x400")
        ctk.set_appearance_mode("dark")

        # Переменные для хранения путей
        self.file1_label = tk.StringVar(value="Файл не выбран")
        self.file2_label = tk.StringVar(value="Файл не выбран")
        self.folder_label = tk.StringVar(value="Папка не выбрана")
        self.file1_path = None
        self.file2_path = None
        self.folder_path = None

        # Фрейм для выбора файлов
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.frame, text="Автохронометраж Meet Manager",
                     font=("Arial", 14)).pack(pady=5)

        # Первый файл
        self.label_file1 = ctk.CTkLabel(
            self.frame,
            textvariable=self.file1_label,
            wraplength=400
        )
        self.label_file1.pack(pady=(5, 2))
        self.btn_file1 = ctk.CTkButton(
            self.frame,
            text="Выбрать Swimming-файл",
            width=BTN_WIDTH,
            command=self.select_file1
        )
        self.btn_file1.pack(pady=5)

        # Второй файл
        self.label_file2 = ctk.CTkLabel(
            self.frame,
            textvariable=self.file2_label,
            wraplength=400
        )
        self.label_file2.pack(pady=(10, 2))
        self.btn_file2 = ctk.CTkButton(
            self.frame,
            text="Выбрать Lenex-файл",
            width=BTN_WIDTH,
            command=self.select_file2
        )
        self.btn_file2.pack(pady=5)

        self.label_folder = ctk.CTkLabel(
            self.frame, textvariable=self.folder_label, wraplength=400)
        self.label_folder.pack(pady=(10, 2))
        self.btn_folder = ctk.CTkButton(
            self.frame,
            text="Выбрать папку обмена",
            width=BTN_WIDTH,
            command=self.select_folder
        )
        self.btn_folder.pack(pady=5)

        self.btn_start = ctk.CTkButton(
            self.frame,
            text="Старт!",
            width=BTN_WIDTH,
            command=self.start_process,
            state='disabled'
        )
        self.btn_start.pack(pady=20)

    def truncate_path(self, path):
        if len(path) > MAX_PATH_LENGTH:
            return f"...{os.sep}{os.path.basename(path)}"
        return path

    def update_start_state(self):
        self.btn_start.configure(
            state='normal' if (
                self.file1_path
                and self.file2_path
                and self.folder_path
            ) else 'disabled'
        )

    def select_file1(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[('Swimming Файл', '*.swimming')]
        )
        if file_path:
            self.file1_path = file_path
            self.file1_label.set(self.truncate_path(file_path))
        self.update_start_state()

    def select_file2(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[('Lenex файл', ('*.lxf', '.lef'))]
        )
        if file_path:
            self.file2_path = file_path
            self.file2_label.set(self.truncate_path(file_path))
        self.update_start_state()

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку")
        if folder_path:
            self.folder_path = folder_path
            self.folder_label.set(self.truncate_path(folder_path))
        self.update_start_state()

    def start_process(self):
        self.withdraw()
        ProcessingWindow(self)


class ProcessingWindow(ctk.CTkToplevel):
    def __init__(self, parent: FileSelectionApp):
        super().__init__(parent)

        self.parent = parent
        self.title("Обработка данных")
        self.geometry("400x250")

        # Фокусировка на новом окне
        self.grab_set()
        self.focus_force()

        # Информация о выбранных файлах (в одну строку)
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(pady=5, padx=10, fill="both")

        # Сортируем информацию по центру
        self.file1_label = ctk.CTkLabel(
            self.info_frame, text=self.parent.file1_label.get(), anchor="center", wraplength=380)
        self.file1_label.pack(fill="x")

        self.file2_label = ctk.CTkLabel(
            self.info_frame, text=self.parent.file2_label.get(), anchor="center", wraplength=380)
        self.file2_label.pack(fill="x")

        self.folder_label = ctk.CTkLabel(
            self.info_frame, text=self.parent.folder_label.get(), anchor="center", wraplength=380)
        self.folder_label.pack(fill="x")

        self.btn_exit = ctk.CTkButton(
            self,
            text="Завершить!",
            width=BTN_WIDTH,
            command=self.close_process
        )
        self.btn_exit.pack(pady=5)

        self.client = Client(
            self.parent.file2_path,
            self.parent.file1_path,
            self.parent.folder_path
        )
        self.client.observe()

        self.protocol("WM_DELETE_WINDOW", self.close_process)

    def close_process(self):
        self.client.stop()
        self.destroy()
        self.parent.deiconify()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = FileSelectionApp()
    app.mainloop()
