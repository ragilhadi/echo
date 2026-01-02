"""OpenRouter chat client implementation.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    OpenRouter API Documentation: https://openrouter.ai/docs
"""

from openai import OpenAI
from typing import Generator, Optional, Dict, Any, List
import os
import requests
import dotenv
from modules.client.base import BaseChatClient, ChatResponse
from modules.client.exception import APIConnectionError, InvalidModelError

dotenv.load_dotenv()


class OpenRouterClient(BaseChatClient):
    """OpenRouter implementation of the chat client (Single Responsibility Principle).

    This class handles OpenRouter-specific API interactions while inheriting
    common functionality from BaseChatClient.

    Attributes:
        client (OpenAI): The underlying OpenAI-compatible client instance.
        api_key (str): The OpenRouter API key.
    """

    base_url = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "openai/gpt-4.1",
        default_temperature: float = 0.7,
    ):
        """Initialize the OpenRouter client.

        Args:
            api_key (str, optional): OpenRouter API key. Defaults to environment variable.
            default_model (str, optional): Default model to use. Defaults to DEFAULT_MODEL from config.
            default_temperature (float, optional): Default temperature. Defaults to 0.7.

        Raises:
            APIConnectionError: If API key is missing or invalid.
        """
        super().__init__(default_model, default_temperature)
        print("default model", default_model)

        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise APIConnectionError("OpenRouter API key is required")

        self._create_client()

    @classmethod
    def _build_headers(cls) -> Dict[str, Any]:
        """Build headers for API requests.

        Args:
            headers (Dict[str, Any], optional): Additional headers to include. Defaults to None.

        Returns:
            Dict[str, Any]: Complete headers dictionary for API requests.
        """
        base_headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
        }
        return base_headers

    @classmethod
    def get_available_models(cls) -> List[str]:
        response = requests.get(
            f"{cls.base_url}/models",
            headers=cls._build_headers(),
        )
        response_json = response.json()
        result = [x["id"] for x in response_json["data"]]
        return result

    @classmethod
    def get_available_models_free(cls) -> List[str]:
        model_list = cls.get_available_models()
        result = [x for x in model_list if x.endswith("free")]
        return result

    def _create_client(self) -> None:
        """Create the OpenRouter client instance (Template Method Pattern)."""
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> ChatResponse:
        """Generate a chat completion using OpenRouter API.

        Args:
            messages (list[dict]): List of message dictionaries with 'role' and 'content'.
            model (str, optional): Model to use. Defaults to instance default.
            temperature (float, optional): Temperature for randomness. Defaults to instance default.

        Returns:
            ChatResponse: Response containing generated content and metadata.

        Raises:
            APIConnectionError: If API request fails.
            InvalidModelError: If specified model is invalid.
        """
        resolved_model, resolved_temperature = self._resolve_parameters(
            model, temperature
        )

        try:
            response = self.client.chat.completions.create(
                model=resolved_model,
                messages=messages,
                temperature=resolved_temperature,
            )

            content = response.choices[0].message.content

            return ChatResponse(content=content, model=resolved_model)

        except Exception as e:
            self._handle_api_error(e, resolved_model)

    def stream_chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """Generate a streaming chat completion using OpenRouter API.

        Args:
            messages (list[dict]): List of message dictionaries with 'role' and 'content'.
            model (str, optional): Model to use. Defaults to instance default.
            temperature (float, optional): Temperature for randomness. Defaults to instance default.

        Yields:
            str: Incremental content chunks from the completion.

        Raises:
            APIConnectionError: If API request fails.
            InvalidModelError: If specified model is invalid.
        """
        resolved_model, resolved_temperature = self._resolve_parameters(
            model, temperature
        )
        print("resolved model", resolved_model)

        try:
            stream = self.client.chat.completions.create(
                model=resolved_model,
                messages=messages,
                temperature=resolved_temperature,
                stream=True,
            )

            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except Exception as e:
            self._handle_api_error(e, resolved_model)

    def _handle_api_error(self, error: Exception, model: str) -> None:
        """Handle API errors with appropriate exception mapping (Single Responsibility).

        Args:
            error (Exception): The original exception from the API.
            model (str): The model that was being used when the error occurred.

        Raises:
            InvalidModelError: If the error is related to an invalid model.
            APIConnectionError: For all other API-related errors.
        """
        error_message = str(error).lower()

        if "model" in error_message or "not found" in error_message:
            raise InvalidModelError(f"Invalid model specified: {model}")

        raise APIConnectionError(f"OpenRouter API request failed: {str(error)}")
