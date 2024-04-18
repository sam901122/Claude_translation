from api_client import APIClient, load_api_key
from translator import Translator


def main():
    input_file = "./test.txt"
    output_file = "./translated.txt"
    model = "claude-3-haiku-20240307"
    to_language = "Traditional Chinese"

    # UI = ui.UI()
    # params = UI.get_params()

    translator = Translator(model, to_language)
    translated_txt = translator.translate(input_file)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(translated_txt)


if __name__ == "__main__":
    main()