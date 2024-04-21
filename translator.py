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
            progress_callback (callable): the progress callback function, update the number of paragraphs that have been translated
            stop_event (threading.Event): the stop event
        Return:
            None
        """

        self.client = APIClient(load_api_key(), model)
        self.to_language = to_language
        self.progress_callback = progress_callback
        self.stop_event = stop_event

        # Read article and split into paragraphs
        with open(input_file_path, "r", encoding="utf-8") as file:
            self.article = file.read()
        self.paragraphs = self._preprocess(self.article)
        self.translated_paragraphs = [None for _ in range(len(self.paragraphs))]

        self.prompt_template = f"""
        Here is the context of the article: [[[CTX]]]. 
        
        Translate the following paragraph into {self.to_language}.
        Leave the names in original language.
        The translated text should be in {self.to_language}.
        The response should be the translation only. Do not include other text.
        You must follow the above instructions. Or the result will be poor and ruin my career.
        
        Here is the paragraph: [[[TP]]]"""

    @property
    def translated_cnt(self):
        """Return the number of translated paragraphs."""
        return len([p for p in self.translated_paragraphs if p != None])

    @property
    def paragraph_cnt(self):
        """Return the number of paragraphs."""
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
        """
        The work function for the translation thread.
        This function will read the paragraph index from the queue, translate the paragraph, and update the translated_paragraphs list.

        Args:
            par_index_queue (Queue): the queue of paragraph indexes
        Return:
            None
        """

        # Keep translating until the queue is empty or the stop event is set
        while self.stop_event.is_set() == False:
            try:
                # Get the paragraph
                par_index = par_index_queue.get(block=False)
                paragraph = self.paragraphs[par_index]

                # Translate the paragraph
                prompt = self.prompt_template.replace(
                    "[[[CTX]]]", "\n".join(self.paragraphs[max(0, par_index - 5) : par_index + 5])
                )
                prompt = prompt.replace("[[[TP]]]", paragraph)

                translated = False
                while not translated:
                    try:
                        translated_paragraph = self.client.get_response(prompt)
                        self.translated_paragraphs[par_index] = translated_paragraph
                        translated = True
                    except:
                        time.sleep(20)  # Wait for 20 seconds and try again

                # Update the progress bar info
                if self.progress_callback:
                    self.progress_callback(
                        self.translated_cnt, self.paragraph_cnt, translate_preview=translated_paragraph
                    )

            except Empty:
                break

    def translate(self, thread_cnt=5):
        """
        Translate the whole article paragraph by paragraph.
        The implementation is multi-threaded, which means it will translate multiple paragraphs at the same time.

        Args:
            thread_cnt (int): the number of threads for translation
        Return:
            str: the translated text
        """

        # Prepare the queue of paragraph indexes
        par_index_queue = Queue()
        par_index_queue.queue.extend(range(len(self.paragraphs)))

        # Start the translation threads
        threads = []
        for _ in range(thread_cnt):
            thread = threading.Thread(target=self._translate_worker, args=(par_index_queue,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Check if the translation is stopped
        if self.stop_event.is_set():
            self.progress_callback(self.translated_cnt, self.paragraph_cnt, stopped=True)
            return None

        # Combine the translated paragraphs
        translated_txt = "\n\n".join(self.translated_paragraphs)
        return translated_txt
