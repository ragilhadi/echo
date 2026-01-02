"""Base chat client module.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    None
"""

from abc import ABC, abstractmethod
from typing import Generator, Optional
from dataclasses import dataclass


@dataclass
class ChatResponse:
    """Response data structure for chat completions.

    Attributes:
        content (str): The generated text content.
        model (str): The model used for generation.
    """

    content: str
    model: str


class BaseChatClient(ABC):
    """Abstract base class for chat clients (Open/Closed & Dependency Inversion Principles).

    This class defines the common interface and shared functionality for all chat clients.
    Each concrete implementation handles its specific API details.

    Attributes:
        default_model (str): Default model to use for completions.
        default_temperature (float): Default temperature for completions.
    """

    def __init__(self, default_model: str, default_temperature: float = 0.7):
        """Initialize the base chat client.

        Args:
            default_model (str): Default model to use for completions.
            default_temperature (float, optional): Default temperature. Defaults to 0.7.
        """
        self.default_model = default_model
        self.default_temperature = default_temperature

    @abstractmethod
    def _create_client(self) -> None:
        """Create the underlying client instance (Template Method Pattern).

        Each concrete implementation must define how to create their specific client.
        """
        pass

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> ChatResponse:
        """Generate a chat completion.

        Args:
            messages (list[dict]): List of message dictionaries with 'role' and 'content'.
            model (str, optional): Model to use. Defaults to instance default.
            temperature (float, optional): Temperature for randomness. Defaults to instance default.

        Returns:
            ChatResponse: Response containing generated content and metadata.
        """
        pass

    @abstractmethod
    def stream_chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """Generate a streaming chat completion.

        Args:
            messages (list[dict]): List of message dictionaries with 'role' and 'content'.
            model (str, optional): Model to use. Defaults to instance default.
            temperature (float, optional): Temperature for randomness. Defaults to instance default.

        Yields:
            str: Incremental content chunks from the completion.
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models.

        Returns:
            list[str]: List of available model names.
        """
        pass

    def _resolve_parameters(
        self, model: Optional[str], temperature: Optional[float]
    ) -> tuple[str, float]:
        """Resolve model and temperature parameters with defaults (DRY Principle).

        Args:
            model (str, optional): Model parameter to resolve.
            temperature (float, optional): Temperature parameter to resolve.

        Returns:
            tuple[str, float]: Resolved model and temperature values.
        """
        resolved_model = model or self.default_model
        resolved_temperature = temperature or self.default_temperature
        return resolved_model, resolved_temperature

    def test_connection(self) -> bool:
        """Test the API connection with a simple request.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            self.chat(test_messages)
            return True
        except Exception:
            return False

    def format_messages(self, conversation: list[tuple[str, str]]) -> list[dict]:
        """Format conversation tuples into message format.

        Args:
            conversation (list[tuple[str, str]]): List of (role, content) tuples.

        Returns:
            list[dict]: Formatted messages for API consumption.
        """
        return [{"role": role, "content": content} for role, content in conversation]

    def set_defaults(
        self, model: Optional[str] = None, temperature: Optional[float] = None
    ) -> None:
        """Update default model and temperature settings.

        Args:
            model (str, optional): New default model.
            temperature (float, optional): New default temperature.
        """
        if model is not None:
            self.default_model = model

        if temperature is not None:
            self.default_temperature = temperature
