import threading
import time
from queue import Empty, Queue

from api_client import APIClient, load_api_key


class Translator:
    def __init__(
        self,
        model: str,
        to_language: str,
        input_file_path: str,
        progress_callback: callable,
        stop_event: threading.Event,
    ):
        """
        Init the Translator

        Args:
            model (str): the model name, provided by Anthropic
            to_language (str): the target language. Every language is available, it will be sent to the API
            input_file_path (str): the input file path
            stop_event (threading.Event): the stop event
            progress_callback (function): the progress callback function, update the number of paragraphs that have been translated
        Return:
            None
        """

        self.client = APIClient(load_api_key(), model)
        self.to_language = to_language
        self.progress_callback = progress_callback
        self.stop_event = stop_event

        # read article
        with open(input_file_path, "r", encoding="utf-8") as file:
            self.article = file.read()
        self.paragraphs = self._preprocess(self.article)
        self.translated_paragraphs = [None for _ in range(len(self.paragraphs))]

        self.prompt = f"""
        Translate the following text into {self.to_language}.
        Leave the names in original language. 
        The translated text should be in {self.to_language}.
        The response should be the translation only. Do not include other text.
        You must follow the above instructions. Or the result will be poor and ruin my career.
        
        Here is the paragraph: [[[TP]]]"""

    @property
    def translated_cnt(self):
        return len([p for p in self.translated_paragraphs if p != None])

    @property
    def paragraph_cnt(self):
        return len(self.paragraphs)

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

    def _translate_worker(self, par_index_queue):
        while self.stop_event.is_set() == False:
            try:
                par_index = par_index_queue.get(block=False)
                paragraph = self.paragraphs[par_index]

                translated = False
                while not translated:
                    try:
                        translated_paragraph = self.client.get_response(self.prompt.replace("[[[TP]]]", paragraph))
                        self.translated_paragraphs[par_index] = translated_paragraph
                        translated = True
                    except:
                        time.sleep(20)  # Wait for 20 seconds and try again

                if self.progress_callback:
                    self.progress_callback(
                        self.translated_cnt, self.paragraph_cnt, translate_preview=translated_paragraph
                    )

            except Empty:
                break

    def translate(self, thread_cnt=5):
        par_index_queue = Queue()
        par_index_queue.queue.extend(range(len(self.paragraphs)))
        threads = []

        for _ in range(thread_cnt):
            thread = threading.Thread(target=self._translate_worker, args=(par_index_queue,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        if self.stop_event.is_set():
            self.progress_callback(self.translated_cnt, self.paragraph_cnt, stopped=True)
            return None

        translated_txt = "\n\n".join(self.translated_paragraphs)
        return translated_txt
