import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

from translator import Translator


class TranslationUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Claude 翻譯機")
        self.window.geometry("800x600")

        self.model = {
            "Haiku": "claude-3-haiku-20240307",
            "Sonnet": "claude-3-sonnet-20240229",
            "Opus": "claude-3-opus-20240229",
        }

        # Varaibles
        self.input_file_path = tk.StringVar()
        self.model_var = tk.StringVar()
        self.model_var.set("Haiku")
        self.to_language_var = tk.StringVar()
        self.output_file_name = tk.StringVar()

        # input_file
        self.select_file_button = tk.Button(self.window, text="選擇要翻譯的檔案", command=self.select_input_file)
        self.select_file_button.pack(pady=5)
        file_entry = tk.Entry(self.window, textvariable=self.input_file_path, width=100)
        file_entry.pack()

        # Model
        self.model_dropdown = tk.OptionMenu(self.window, self.model_var, *(list(self.model.keys())))
        self.model_dropdown.pack(pady=5)

        # To Language
        self.language_choices = [
            "Traditional Chinese",
            "English",
        ]
        self.language_dropdown = ttk.Combobox(
            self.window, textvariable=self.to_language_var, values=self.language_choices
        )
        self.language_dropdown.pack(pady=5)

        # Start translate
        self.start_btn = tk.Button(self.window, text="開始翻譯", command=self.translate)
        self.start_btn.pack(pady=5)

    def select_input_file(self):
        file_path = filedialog.askopenfilename(title="選擇要翻譯的檔案")
        self.input_file_path.set(file_path)

    def translate(self):
        self.translator = Translator(self.model[self.model_var.get()], self.to_language_var.get())
        self.translator.translate(self.input_file_path.get())
        return

    def run(self):
        self.window.mainloop()
        pass
