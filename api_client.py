import os

import anthropic
from dotenv import load_dotenv


class APIClient:
    def __init__(self, api_key: str, model: str):
        """
        init the Anthropic API client

        Args:
            api_key (str): the Anthropic API key
            model (str): the model name
        Return:
            None
        """

        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def get_response(self, prompt: str, max_tokens: int = 3000):
        """
        Get the response from the API

        Args:
            prompt (str): the prompt
            max_tokens (int): the maximum token length of response
        Return:
            str: the response
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return response.content[0].text


def load_api_key():
    """Load Anthropic API key from .env file"""

    load_dotenv()
    return os.getenv("CLAUDE_API_KEY")
