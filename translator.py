import time

from api_client import APIClient, load_api_key


class Translator:
    def __init__(self, model: str, to_language: str, stop_event: threading.Event):
        """
        Init the Translator

        Args:
            model (str): the model name, provided by Anthropic
            to_language (str): the target language. Every language is available, it will be sent to the API
            stop_event (threading.Event): the stop event
        Return:
            None
        """

        self.client = APIClient(load_api_key(), model)
        self.to_language = to_language
        self.stop_event = stop_event
        self.prompt = f"""
        Translate the following text into {self.to_language}.
        Leave the names in original language. 
        The translated text should be in {self.to_language}.
        The response should be the translation only. Do not include other text.
        You must follow the above instructions. Or the result will be poor and ruin my career.
        
        Here is the paragraph: [[[TP]]]"""

    def _preprocess(self, txt: str):
        """
        Preprocess the text before translation, including
            1. Split the text into paragraphs by "\n\n", which means an empty line means the end of a paragraph
            2. Remove leading and trailing whitespaces
            3. replace "\n" with " "
            4. Remove "-" at the beginning of a line.

        Args:
            txt (str): the text to be preprocessed
        Return:
            list[str]: the list of preprocessed paragraphs.
        """

        paragraphs = txt.split("\n\n")
        preprocessed_paragraphs = [p.strip().replace("\n", " ").replace("- ", "") for p in paragraphs if p.strip()]
        return preprocessed_paragraphs

    def translate(self, file_path: str, progress_callback: function = None):
        """
        Translate the text given the file path

        Args:
            file_path (str): the file path.
            progress_callback (Callable): the progress callback, execute after each paragraph is translated.
        Return:
            str: the translated text. Seperated into paragraphs by "\n\n".
        """

        # Read the text from the file
        with open(file_path, "r", encoding="utf-8") as file:
            txt = file.read()

        # Preprocess the text
        paragraphs = self._preprocess(txt)

        par_cnt = len(paragraphs)
        translated_pars = []

        # Translate paragraph by paragraph
        for par_index, paragraph in enumerate(paragraphs):
            if self.stop_event.is_set():  # If the translation is stopped, break the loop
                break

            # Keep trying until the translation is successful
            translated = False
            while not translated:
                try:
                    translated_pars.append(self.client.get_response(self.prompt.replace("[[[TP]]]", paragraph)))
                    translated = True

                    if progress_callback:  # Update the UI
                        progress_callback(par_index + 1, par_cnt, translated_pars[-1])
                except:
                    time.sleep(20)  # Usually is the error of rate limit, wait for 20 seconds and try again

        translated_txt = "\n\n".join(translated_pars)
        return translated_txt
