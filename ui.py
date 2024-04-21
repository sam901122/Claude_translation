import threading
import tkinter as tk
from tkinter import filedialog, ttk

from translator import Translator


class TranslationUI:
    def __init__(self):
        """Init the TranslationUI"""

        # Window setting
        self.window = tk.Tk()
        self.window.title("Claude translator")
        self.window.geometry("800x600")

        # Model name mapping
        self.model_name_mapping = {
            "Haiku": "claude-3-haiku-20240307",
            "Sonnet": "claude-3-sonnet-20240229",
            "Opus": "claude-3-opus-20240229",
        }

        # Varaibles
        self.input_file_path = tk.StringVar()
        self.model = tk.StringVar()
        self.to_language = tk.StringVar()

        # Event
        self.stop_translation_event = threading.Event()

        # Default values
        self.model.set("Haiku")
        self.to_language.set("繁體中文")

        # UI elements
        self.create_ui_elmts()

    def create_ui_elmts(self):
        """
        Create the UI elements, contains:
            - Choose input file path
            - Choose model
            - Choose language
            - Translation relevant
        """

        def create_input_file_path_elmt():
            """Create the input file path element"""
            input_file_frame = tk.Frame(self.window)
            input_file_frame.pack(pady=10)

            # Button to select file
            self.select_file_button = tk.Button(input_file_frame, text="Select file", command=self.select_input_file)
            self.select_file_button.pack(side=tk.LEFT, padx=5)

            # Entry to show the file path
            file_entry = tk.Entry(input_file_frame, textvariable=self.input_file_path, width=100)
            file_entry.pack(side=tk.LEFT)

        def create_model_elmt():
            """Create the model element"""
            model_frame = tk.Frame(self.window)
            model_frame.pack(pady=5)

            # Model label
            model_label = tk.Label(model_frame, text="Translation Model:")
            model_label.pack(side=tk.LEFT, padx=5)

            # Model dropdown
            self.model_dropdown = tk.OptionMenu(model_frame, self.model, *(list(self.model_name_mapping.keys())))
            self.model_dropdown.pack(side=tk.LEFT)

        def create_language_elmt():
            """Create the language element"""
            language_frame = tk.Frame(self.window)
            language_frame.pack(pady=5)

            # Language label
            language_label = tk.Label(language_frame, text="Target Language:")
            language_label.pack(side=tk.LEFT, padx=5)

            # Language dropdown
            self.language_choices = [
                "繁體中文",
                "English",
            ]
            self.language_dropdown = ttk.Combobox(
                language_frame, textvariable=self.to_language, values=self.language_choices
            )
            self.language_dropdown.pack(side=tk.LEFT)

        def create_translate_elmt():
            """Create the translation element"""
            translate_frame = tk.Frame(self.window)
            translate_frame.pack(pady=5)

            # Start translation button
            self.start_btn = tk.Button(translate_frame, text="Start Translation", command=self.translate)
            self.start_btn.pack(side=tk.LEFT)

            # Stop translation button
            self.stop_btn = tk.Button(
                translate_frame, text="Stop translation", command=self.stop_translate, state="disabled"
            )
            self.stop_btn.pack(side=tk.LEFT)

            # Progress bar
            self.progress_bar = ttk.Progressbar(translate_frame, length=300, mode="determinate")
            self.progress_bar.pack(side=tk.LEFT)

            # Progress info label
            self.progress_info_label = tk.Label(translate_frame, text="")
            self.progress_info_label.pack(side=tk.LEFT)

            # Translate preview
            translate_preview_frame = tk.Frame(self.window)
            translate_preview_frame.pack(pady=10)

            self.translate_preview = tk.Label(translate_preview_frame, text="")
            self.translate_preview.pack(side=tk.TOP)

        create_input_file_path_elmt()
        create_model_elmt()
        create_language_elmt()
        create_translate_elmt()

    def stop_translate(self):
        """Stop the translation process, set the stop event & update the progress info label"""
        self.stop_translation_event.set()
        self.progress_info_label.config(text="Translation stopping...")

    def select_input_file(self):
        """Select the input file path and set the input_file_path variable"""
        file_path = filedialog.askopenfilename(title="Select file", filetypes=[("Text Files", "*.txt")])
        self.input_file_path.set(file_path)

    def update_progress(self, translated_cnt, par_cnt, stopped=False, translate_preview=""):
        """
        Callback function to update the progress bar and progress info label
        This function will be called by the Translator class, each time a paragraph is translated

        Args:
            translated_cnt (int): the number of translated paragraphs
            par_cnt (int): the total number of paragraphs
            stopped (bool): whether the translation is stopped
            translate_preview (str): the preview of the translated paragraph
        Returns:
            None
        """

        # Update the progress bar
        progress = translated_cnt / par_cnt * 100
        self.progress_bar["value"] = progress

        # Update the progress info label
        if self.stop_translation_event.is_set():
            if stopped == False:
                self.progress_info_label.config(text="Translation stopping...")
            else:
                self.progress_info_label.config(text="Translation stopped")
        else:
            # Show the ratio of translated paragraphs and paragraphs preview
            self.progress_info_label.config(text=f"{translated_cnt}/{par_cnt} paragraphs")
            self.translate_preview.config(text=f"Translated Preview: {translate_preview[:20]}...")

        self.window.update_idletasks()

    def translate(self):
        """Start the translation process in a new thread"""

        def translate_thread():
            """Translate the input file and write the translated text to a new file"""

            # Update button state when translation starts
            self.update_widgets_state("disabled")
            self.stop_btn.config(state="normal")

            # Start the translation
            self.translator = Translator(
                self.model_name_mapping[self.model.get()],
                self.to_language.get(),
                self.input_file_path.get(),
                self.update_progress,
                self.stop_translation_event,
            )
            translated_txt = self.translator.translate()

            # Write the translated text to a new file
            if not self.stop_translation_event.is_set():
                with open(
                    self.input_file_path.get().replace(".", f"_{self.to_language.get()}."), "w", encoding="utf-8"
                ) as file:
                    file.write(translated_txt)

            # Update button state when translation ends
            self.update_widgets_state("normal")
            self.stop_btn.config(state="disabled")
            self.stop_translation_event.clear()

        threading.Thread(target=translate_thread).start()

    def update_widgets_state(self, state):
        """
        Update the state of the widgets, disable or enable them. This function will update the following widgets:
            - select_file_button
            - model_dropdown
            - language_dropdown
            - start_btn

        Args:
            state (str): the state to set, "disabled" or "normal"
        Returns:
            None
        """

        self.select_file_button.config(state=state)
        self.model_dropdown.config(state=state)
        self.language_dropdown.config(state=state)
        self.start_btn.config(state=state)

    def run(self):
        """Run the UI"""
        self.window.mainloop()
