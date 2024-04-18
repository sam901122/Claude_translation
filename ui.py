import threading
import tkinter as tk
from tkinter import filedialog, ttk

from translator import Translator


class TranslationUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Claude translator")
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
        self.to_language_var.set("繁體中文")

        # input_file
        input_file_frame = tk.Frame(self.window)
        input_file_frame.pack(pady=10)

        self.select_file_button = tk.Button(input_file_frame, text="Select file", command=self.select_input_file)
        self.select_file_button.pack(side=tk.LEFT, padx=5)
        file_entry = tk.Entry(input_file_frame, textvariable=self.input_file_path, width=100)
        file_entry.pack(side=tk.LEFT)

        # Model
        model_frame = tk.Frame(self.window)
        model_frame.pack(pady=5)
        model_label = tk.Label(model_frame, text="Translation Model:")
        model_label.pack(side=tk.LEFT, padx=5)
        self.model_dropdown = tk.OptionMenu(model_frame, self.model_var, *(list(self.model.keys())))
        self.model_dropdown.pack(side=tk.LEFT)

        # To Language
        language_frame = tk.Frame(self.window)
        language_frame.pack(pady=5)
        language_label = tk.Label(language_frame, text="Target Language:")
        language_label.pack(side=tk.LEFT, padx=5)
        self.language_choices = [
            "繁體中文",
            "English",
        ]
        self.language_dropdown = ttk.Combobox(
            language_frame, textvariable=self.to_language_var, values=self.language_choices
        )
        self.language_dropdown.pack(side=tk.LEFT)

        # Start translate
        self.start_btn = tk.Button(self.window, text="Start Translation", command=self.translate)
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
        file_path = filedialog.askopenfilename(title="Select file", filetypes=[("Text Files", "*.txt")])
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
