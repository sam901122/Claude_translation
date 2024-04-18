import time

from api_client import APIClient, load_api_key


class Translator:
    def __init__(self, model, to_language, stop_event):
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

    def _preprocess(self, txt):
        paragraphs = txt.split("\n\n")
        preprocessed_paragraphs = [p.strip().replace("\n", " ").replace("- ", "") for p in paragraphs if p.strip()]
        return preprocessed_paragraphs

    def translate(self, file_path, progress_callback=None):
        with open(file_path, "r", encoding="utf-8") as file:
            txt = file.read()

        paragraphs = self._preprocess(txt)
        par_cnt = len(paragraphs)

        translated_pars = []

        for par_index, paragraph in enumerate(paragraphs):
            if self.stop_event.is_set():
                break

            translated = False

            while not translated:
                try:
                    translated_pars.append(self.client.get_response(self.prompt.replace("[[[TP]]]", paragraph)))
                    translated = True

                    if progress_callback:
                        progress_callback(par_index + 1, par_cnt)
                    print(f"Paragraph {par_index+1}/{par_cnt}: {translated_pars[-1][:10]}...")
                except:
                    time.sleep(20)  # Usually is the error of rate limit, wait for 20 seconds and try again

        translated_txt = "\n\n".join(translated_pars)
        return translated_txt
