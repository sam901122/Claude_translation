import threading
import tkinter as tk
from tkinter import filedialog, ttk

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
        self.to_language_var = tk.StringVar()
        self.output_file_name = tk.StringVar()

        # Default values
        self.model_var.set("Haiku")
        self.to_language_var.set("Traditional Chinese")

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

        self.progress_bar = ttk.Progressbar(self.window, length=300, mode="determinate")
        self.progress_bar.pack(pady=5)

        # Stop button
        self.stop_translation_event = threading.Event()
        self.stop_btn = tk.Button(
            self.window, text="停止翻譯", command=self.stop_translation_event.set, state="disabled"
        )
        self.stop_btn.pack(pady=5)

    def select_input_file(self):
        file_path = filedialog.askopenfilename(title="選擇要翻譯的檔案")
        self.input_file_path.set(file_path)

    def update_progress(self, current, total):
        progress = current / total * 100
        self.progress_bar["value"] = progress
        self.window.update_idletasks()

    def translate(self):
        def translate_thread():
            print("start translation")
            self.toggle_widgets("disabled")
            self.stop_btn.config(state="normal")

            self.translator = Translator(
                self.model[self.model_var.get()], self.to_language_var.get(), self.stop_translation_event
            )
            translated_txt = self.translator.translate(self.input_file_path.get(), self.update_progress)

            self.toggle_widgets("normal")
            self.stop_btn.config(state="disabled")
            self.stop_translation_event.clear()

            with open(
                self.input_file_path.get().replace(".", f"{self.to_language_var.get()}."), "w", encoding="utf-8"
            ) as file:
                file.write(translated_txt)

        threading.Thread(target=translate_thread).start()

    def toggle_widgets(self, state):
        self.select_file_button.config(state=state)
        self.model_dropdown.config(state=state)
        self.language_dropdown.config(state=state)
        self.start_btn.config(state=state)

    def run(self):
        self.window.mainloop()
        pass
