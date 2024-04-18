import threading
import tkinter as tk
from tkinter import filedialog, ttk

from translator import Translator


class TranslationUI:
    def __init__(self):
        # Window setting
        self.window = tk.Tk()
        self.window.title("Claude translator")
        self.window.geometry("800x600")

        self.model_name_mapping = {
            "Haiku": "claude-3-haiku-20240307",
            "Sonnet": "claude-3-sonnet-20240229",
            "Opus": "claude-3-opus-20240229",
        }

        # Varaibles
        self.input_file_path = tk.StringVar()
        self.model = tk.StringVar()
        self.to_language = tk.StringVar()

        # Default values
        self.model.set("Haiku")
        self.to_language.set("繁體中文")

        # UI elements
        self.create_ui_elmts()

    def create_ui_elmts(self):
        def create_input_file_path_elmt():
            input_file_frame = tk.Frame(self.window)
            input_file_frame.pack(pady=10)
            self.select_file_button = tk.Button(input_file_frame, text="Select file", command=self.select_input_file)
            self.select_file_button.pack(side=tk.LEFT, padx=5)
            file_entry = tk.Entry(input_file_frame, textvariable=self.input_file_path, width=100)
            file_entry.pack(side=tk.LEFT)

        def create_model_elmt():
            model_frame = tk.Frame(self.window)
            model_frame.pack(pady=5)
            model_label = tk.Label(model_frame, text="Translation Model:")
            model_label.pack(side=tk.LEFT, padx=5)
            self.model_dropdown = tk.OptionMenu(model_frame, self.model, *(list(self.model_name_mapping.keys())))
            self.model_dropdown.pack(side=tk.LEFT)

        def create_language_elmt():
            language_frame = tk.Frame(self.window)
            language_frame.pack(pady=5)
            language_label = tk.Label(language_frame, text="Target Language:")
            language_label.pack(side=tk.LEFT, padx=5)
            self.language_choices = [
                "繁體中文",
                "English",
            ]
            self.language_dropdown = ttk.Combobox(
                language_frame, textvariable=self.to_language, values=self.language_choices
            )
            self.language_dropdown.pack(side=tk.LEFT)

        def create_translate_elmt():
            translate_frame = tk.Frame(self.window)
            translate_frame.pack(pady=5)

            self.start_btn = tk.Button(translate_frame, text="Start Translation", command=self.translate)
            self.start_btn.pack(side=tk.LEFT)

            self.stop_translation_event = threading.Event()
            self.stop_btn = tk.Button(
                translate_frame, text="Stop translation", command=self.stop_translate, state="disabled"
            )
            self.stop_btn.pack(side=tk.LEFT)

            self.progress_bar = ttk.Progressbar(translate_frame, length=300, mode="determinate")
            self.progress_bar.pack(side=tk.LEFT)

            self.progress_info_label = tk.Label(translate_frame, text="")
            self.progress_info_label.pack(side=tk.LEFT)

            translate_preview_frame = tk.Frame(self.window)
            translate_preview_frame.pack(pady=10)

            self.translate_preview = tk.Label(translate_preview_frame, text="")
            self.translate_preview.pack(side=tk.TOP)

        create_input_file_path_elmt()
        create_model_elmt()
        create_language_elmt()
        create_translate_elmt()

    def stop_translate(self):
        self.stop_translation_event.set()
        self.progress_info_label.config(text="Translation stopped")

    def select_input_file(self):
        file_path = filedialog.askopenfilename(title="Select file", filetypes=[("Text Files", "*.txt")])
        self.input_file_path.set(file_path)

    def update_progress(self, current, total, translate_preview):
        progress = current / total * 100
        self.progress_bar["value"] = progress
        if self.stop_translation_event.is_set():
            self.progress_info_label.config(text="Translation stopped")
        else:
            self.progress_info_label.config(text=f"{current}/{total} paragraphs")
            self.translate_preview.config(text=f"Translated Preview: {translate_preview[:20]}...")
        self.window.update_idletasks()

    def translate(self):
        def translate_thread():
            print("start translation")
            self.toggle_widgets("disabled")
            self.stop_btn.config(state="normal")

            self.translator = Translator(
                self.model_name_mapping[self.model.get()], self.to_language.get(), self.stop_translation_event
            )
            translated_txt = self.translator.translate(self.input_file_path.get(), self.update_progress)

            self.toggle_widgets("normal")
            self.stop_btn.config(state="disabled")
            self.stop_translation_event.clear()

            if not self.stop_translation_event.is_set():
                with open(
                    self.input_file_path.get().replace(".", f"_{self.to_language.get()}."), "w", encoding="utf-8"
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
