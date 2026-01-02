"""Chat room and AI interaction management.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    None
"""

from typing import List, Dict, Optional, Generator, Tuple
from modules.db import ChatDatabase
from modules.client import OpenRouterClient
from modules.client.exception import APIConnectionError, InvalidModelError
from constants import ChatRole


class ChatManager:
    """Manages chat rooms and AI interactions (Single Responsibility Principle).

    This class handles all chat-related business logic including room management,
    AI communication, and message persistence.
    """

    def __init__(self, db: ChatDatabase):
        """Initialize the chat manager.

        Args:
            db (ChatDatabase): Database instance for persistence.
        """
        self.db = db

    def create_chat_room(self, room_name: str, system_prompt: str) -> str:
        """Create a new chat room with system prompt.

        Args:
            room_name (str): Name for the new chat room.
            system_prompt (str): Initial system prompt for the room.

        Returns:
            str: The new room ID.

        Raises:
            ValueError: If room name is empty.
        """
        if not room_name or not room_name.strip():
            raise ValueError("Room name cannot be empty")

        room_id = self.db.add_chat_room(room_name.strip())

        # Add system message to the room
        if system_prompt and system_prompt.strip():
            self.db.add_message(
                room_id,
                ChatRole.SYSTEM,
                system_prompt.strip(),
                ChatRole.SYSTEM,
            )

        return room_id

    def get_chat_room_info(self, room_id: str) -> Optional[Tuple[str, str]]:
        """Get chat room information.

        Args:
            room_id (str): The room ID to get info for.

        Returns:
            Optional[Tuple[str, str]]: (room_name, created_at) or None if not found.
        """
        try:
            return self.db.get_chat_room(room_id)
        except Exception:
            return None

    def get_room_name(self, room_id: str) -> Optional[str]:
        """Get the name of a specific chat room.

        Args:
            room_id (str): The room ID to get the name for.

        Returns:
            Optional[str]: Room name or None if not found.
        """
        room_info = self.get_chat_room_info(room_id)
        return room_info[0] if room_info else None

    def get_all_chat_rooms(self) -> List[Tuple[str, str, str]]:
        """Get all chat rooms.

        Returns:
            List[Tuple[str, str, str]]: List of (room_id, room_name, created_at) tuples.
        """
        try:
            return self.db.get_all_chat_rooms()
        except Exception:
            return []

    def get_room_messages(self, room_id: str) -> List[Tuple[str, str, str, str]]:
        """Get all messages for a specific room.

        Args:
            room_id (str): The room ID to get messages for.

        Returns:
            List[Tuple[str, str, str, str]]: List of (role, content, llm, timestamp) tuples.
        """
        try:
            return self.db.get_messages_by_room(room_id)
        except Exception:
            return []

    def add_user_message(self, room_id: str, content: str) -> None:
        """Add a user message to the room.

        Args:
            room_id (str): The room ID to add message to.
            content (str): User message content.

        Raises:
            ValueError: If content is empty.
        """
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        self.db.add_message(
            room_id,
            ChatRole.HUMAN,
            content.strip(),
            ChatRole.HUMAN,
        )

    def add_ai_message(self, room_id: str, content: str, model_name: str) -> None:
        """Add an AI response message to the room.

        Args:
            room_id (str): The room ID to add message to.
            content (str): AI response content.
            model_name (str): Name of the model that generated the response.

        Raises:
            ValueError: If content is empty.
        """
        if not content or not content.strip():
            raise ValueError("AI response content cannot be empty")

        self.db.add_message(
            room_id,
            ChatRole.AI,
            content.strip(),
            model_name,
        )

    def stream_ai_response(
        self, client: OpenRouterClient, messages: List[Dict[str, str]]
    ) -> Generator[str, None, None]:
        """Stream AI response for the given messages.

        Args:
            client (OpenRouterClient): Chat client instance.
            messages (List[Dict[str, str]]): Messages in OpenAI format.

        Yields:
            str: Streaming response chunks.

        Raises:
            APIConnectionError: If API connection fails.
            InvalidModelError: If model is invalid.
        """
        try:
            for chunk in client.stream_chat(messages):
                yield chunk
        except APIConnectionError as e:
            raise APIConnectionError(f"Failed to get AI response: {str(e)}")
        except InvalidModelError as e:
            raise InvalidModelError(f"Invalid model configuration: {str(e)}")
        except Exception as e:
            raise APIConnectionError(f"Unexpected error during AI response: {str(e)}")

    def get_ai_response(
        self, client: OpenRouterClient, messages: List[Dict[str, str]]
    ) -> str:
        """Get a complete AI response for the given messages.

        Args:
            client (OpenRouterClient): Chat client instance.
            messages (List[Dict[str, str]]): Messages in OpenAI format.

        Returns:
            str: Complete AI response.

        Raises:
            APIConnectionError: If API connection fails.
            InvalidModelError: If model is invalid.
        """
        try:
            response = client.chat(messages)
            return response.content
        except APIConnectionError as e:
            raise APIConnectionError(f"Failed to get AI response: {str(e)}")
        except InvalidModelError as e:
            raise InvalidModelError(f"Invalid model configuration: {str(e)}")
        except Exception as e:
            raise APIConnectionError(f"Unexpected error during AI response: {str(e)}")

    def test_chat_model(self, client: OpenRouterClient) -> bool:
        """Test if the chat model is working properly.

        Args:
            client (OpenRouterClient): Chat client instance to test.

        Returns:
            bool: True if the model is working, False otherwise.
        """
        try:
            return client.test_connection()
        except Exception:
            return False

    def get_model_info(self, client: OpenRouterClient) -> Dict[str, str]:
        """Get information about the current model.

        Args:
            client (OpenRouterClient): Chat client instance.

        Returns:
            Dict[str, str]: Model information including name and status.
        """
        try:
            is_working = self.test_chat_model(client)
            return {
                "model": client.default_model,
                "status": "connected" if is_working else "disconnected",
                "temperature": str(client.default_temperature),
            }
        except Exception:
            return {"model": "unknown", "status": "error", "temperature": "unknown"}

    def count_room_messages(self, room_id: str) -> int:
        """Count messages in a specific room.

        Args:
            room_id (str): Room ID to count messages for.

        Returns:
            int: Number of messages in the room.
        """
        try:
            return self.db.count_messages_by_room(room_id)
        except Exception as e:
            raise RuntimeError(f"Failed to count messages for room {room_id}: {str(e)}")

    def delete_chat_room(self, room_id: str) -> bool:
        """Delete a chat room and all its messages.

        Args:
            room_id (str): Room ID to delete.

        Returns:
            bool: True if room was deleted successfully, False if room didn't exist.

        Raises:
            ValueError: If room_id is empty.
            RuntimeError: If deletion fails due to database error.
        """
        if not room_id or not room_id.strip():
            raise ValueError("Room ID cannot be empty")

        try:
            return self.db.delete_chat_room(room_id.strip())
        except Exception as e:
            raise RuntimeError(f"Failed to delete room {room_id}: {str(e)}")

    def clear_room_messages(self, room_id: str) -> int:
        """Clear all messages from a room without deleting the room itself.

        Args:
            room_id (str): Room ID to clear messages from.

        Returns:
            int: Number of messages deleted.

        Raises:
            ValueError: If room_id is empty.
            RuntimeError: If clearing fails due to database error.
        """
        if not room_id or not room_id.strip():
            raise ValueError("Room ID cannot be empty")

        try:
            return self.db.delete_messages_by_room(room_id.strip())
        except Exception as e:
            raise RuntimeError(f"Failed to clear messages for room {room_id}: {str(e)}")

    def clear_room_chat_history(self, room_id: str) -> int:
        """Clear chat history (user and assistant messages) but preserve system messages.

        Args:
            room_id (str): Room ID to clear chat history from.

        Returns:
            int: Number of messages deleted.

        Raises:
            ValueError: If room_id is empty.
            RuntimeError: If clearing fails due to database error.
        """
        if not room_id or not room_id.strip():
            raise ValueError("Room ID cannot be empty")

        try:
            return self.db.clear_room_chat_history(room_id.strip())
        except Exception as e:
            raise RuntimeError(
                f"Failed to clear chat history for room {room_id}: {str(e)}"
            )
