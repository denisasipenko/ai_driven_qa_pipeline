import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MistralClient:
    API_URL = "https://api.mistral.ai/v1/chat/completions"
    API_KEY = os.getenv("MISTRAL_API_KEY")

    @staticmethod
    def call(prompt: str) -> str:
        """
        Calls the Mistral API with a given prompt.

        Args:
            prompt: The user prompt to send to the model.

        Returns:
            The raw JSON response body from the API as a string.

        Raises:
            RuntimeError: If the MISTRAL_API_KEY is not set or if the API call fails.
        """
        if not MistralClient.API_KEY or MistralClient.API_KEY == "YOUR_API_KEY_HERE":
            raise RuntimeError("MISTRAL_API_KEY not set or is a placeholder in .env file")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MistralClient.API_KEY}",
        }

        # The 'requests' library handles JSON serialization, so no manual string escaping is needed.
        body = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "system", "content": "You are a QA automation engineer. Return structured output."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        try:
            response = requests.post(
                MistralClient.API_URL, headers=headers, json=body, timeout=60
            )
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API call failed: {e}") from e
