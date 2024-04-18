from api_client import APIClient, load_api_key
from translator import Translator
from ui import TranslationUI


def main():
    translation_UI = TranslationUI()
    translation_UI.run()


if __name__ == "__main__":
    main()
