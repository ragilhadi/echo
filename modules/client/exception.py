"""
Exception classes for the ChatClient.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    None
"""


class ChatClientError(Exception):
    """Base exception for ChatClient errors."""

    pass


class APIConnectionError(ChatClientError):
    """Raised when API connection fails."""

    pass


class InvalidModelError(ChatClientError):
    """Raised when an invalid model is specified."""

    pass
