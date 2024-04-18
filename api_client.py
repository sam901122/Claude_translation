import os

import anthropic
from dotenv import load_dotenv


class APIClient:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def get_response(self, prompt, max_tokens=3000):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return response.content[0].text


def load_api_key():
    load_dotenv()
    return os.getenv("CLAUDE_API_KEY")
