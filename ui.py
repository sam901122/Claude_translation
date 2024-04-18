import tkinter as tk
from tkinter import filedialog, scrolledtext

from translator import Translator


class TranslationUI:
    def __init__(self, translator):
        self.translator = translator
        self.window = tk.Tk()
        self.window.title("Translation Machine")

        self.input_text = scrolledtext.ScrolledText(self.window, width=50, height=10)
        self.input_text.pack(pady=10)

        self.translate_button = tk.Button(self.window, text="Translate", command=self.translate_text)
        self.translate_button.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(self.window, width=50, height=10)
        self.output_text.pack(pady=10)

        self.select_file_button = tk.Button(self.window, text="Select File", command=self.select_file)
        self.select_file_button.pack(pady=5)

    def translate_text(self):
        input_text = self.input_text.get("1.0", tk.END)
        translated_text = self.translator.translate(input_text, model="claude-3-haiku-20240307")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, translated_text)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select File")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                input_text = file.read()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, input_text)

    def run(self):
        self.window.mainloop()
