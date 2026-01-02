"""Session state management for Streamlit application.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    Streamlit Session State: https://docs.streamlit.io/library/api-reference/session-state
"""

import streamlit as st
from typing import Optional, Any
from modules.db import ChatDatabase
from modules.client import OpenRouterClient


class SessionManager:
    """Manages Streamlit session state following Single Responsibility Principle.

    This class centralizes all session state management, providing a clean
    interface for accessing and updating application state.
    """

    def __init__(self):
        """Initialize the session manager."""
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize all required session state variables."""
        if "db" not in st.session_state:
            st.session_state.db = ChatDatabase()

        if "active_room" not in st.session_state:
            st.session_state.active_room = None

        if "chat_model" not in st.session_state:
            st.session_state.chat_model = None

        if "history_chat" not in st.session_state:
            st.session_state.history_chat = 10

        if "history_token" not in st.session_state:
            st.session_state.history_token = 10

    @property
    def db(self) -> ChatDatabase:
        """Get the database instance."""
        return st.session_state.db

    @property
    def active_room(self) -> Optional[str]:
        """Get the currently active chat room ID."""
        return st.session_state.active_room

    @active_room.setter
    def active_room(self, room_id: Optional[str]) -> None:
        """Set the active chat room."""
        st.session_state.active_room = room_id

    @property
    def chat_model(self) -> Optional[OpenRouterClient]:
        """Get the current chat model instance."""
        return st.session_state.chat_model

    @chat_model.setter
    def chat_model(self, model: Optional[OpenRouterClient]) -> None:
        """Set the chat model instance."""
        st.session_state.chat_model = model

    @property
    def history_token(self) -> int:
        """Get the history token limit."""
        return st.session_state.history_token

    @history_token.setter
    def history_token(self, value: int) -> None:
        """Set the history token limit."""
        st.session_state.history_token = value

    @property
    def history_chat(self) -> int:
        """Get the history chat limit."""
        return st.session_state.history_chat

    @history_chat.setter
    def history_chat(self, value: int) -> None:
        """Set the history chat limit."""
        st.session_state.history_chat = value

    def get_state_value(self, key: str, default: Any = None) -> Any:
        """Get a session state value safely.

        Args:
            key (str): The session state key.
            default (Any, optional): Default value if key doesn't exist.

        Returns:
            Any: The session state value or default.
        """
        return st.session_state.get(key, default)

    def set_state_value(self, key: str, value: Any) -> None:
        """Set a session state value.

        Args:
            key (str): The session state key.
            value (Any): The value to set.
        """
        st.session_state[key] = value

    def clear_session(self) -> None:
        """Clear all session state (useful for logout/reset)."""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        self._initialize_session_state()

    def has_active_room(self) -> bool:
        """Check if there's an active chat room.

        Returns:
            bool: True if there's an active room, False otherwise.
        """
        return self.active_room is not None

    def has_chat_model(self) -> bool:
        """Check if there's a chat model configured.

        Returns:
            bool: True if chat model is configured, False otherwise.
        """
        return self.chat_model is not None
