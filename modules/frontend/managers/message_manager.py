"""Message processing and format management.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    OpenAI Chat API: https://platform.openai.com/docs/api-reference/chat
"""

from typing import List, Dict, Tuple
from constants import ChatRole


class MessageManager:
    """Manages message processing and format conversion (Single Responsibility Principle).

    This class handles all message-related operations including format conversion,
    message trimming, and role mapping without LangChain dependencies.
    """

    def __init__(self):
        """Initialize the message manager."""
        self.role_mapping = {
            ChatRole.HUMAN: "user",
            ChatRole.AI: "assistant",
            ChatRole.SYSTEM: "system",
        }

    def db_messages_to_openai_format(
        self, db_messages: List[Tuple]
    ) -> List[Dict[str, str]]:
        """Convert database messages to OpenAI chat format.

        Args:
            db_messages (List[Tuple]): Database messages as (role, content, llm, timestamp) tuples.

        Returns:
            List[Dict[str, str]]: Messages in OpenAI format [{"role": "user", "content": "..."}].
        """
        openai_messages = []

        for role, content, llm, timestamp in db_messages:
            # Skip empty messages
            if not content or not content.strip():
                continue

            # Map role to OpenAI format
            openai_role = self._map_role_to_openai(role)

            openai_messages.append({"role": openai_role, "content": content.strip()})

        return openai_messages

    def _map_role_to_openai(self, db_role: str) -> str:
        """Map database role to OpenAI role format.

        Args:
            db_role (str): Role from database (ChatRole constants).

        Returns:
            str: OpenAI API role format.
        """
        return self.role_mapping.get(db_role, "user")

    def trim_messages(
        self, messages: List[Dict[str, str]], max_history: int
    ) -> List[Dict[str, str]]:
        """Trim messages to keep within history limit while preserving system messages.

        Args:
            messages (List[Dict[str, str]]): Messages in OpenAI format.
            max_history (int): Maximum number of conversation pairs to keep.

        Returns:
            List[Dict[str, str]]: Trimmed messages.
        """
        if not messages:
            return []

        # Separate system messages from conversation messages
        system_messages = [msg for msg in messages if msg["role"] == "system"]
        conversation_messages = [msg for msg in messages if msg["role"] != "system"]

        # Group conversation messages into pairs (user + assistant)
        conversation_pairs = self._group_conversation_pairs(conversation_messages)

        # Keep only the most recent pairs within the limit
        if len(conversation_pairs) > max_history:
            conversation_pairs = conversation_pairs[-max_history:]

        # Flatten pairs back to individual messages
        trimmed_conversation = []
        for pair in conversation_pairs:
            trimmed_conversation.extend(pair)

        # Combine: system messages first, then trimmed conversation
        return system_messages + trimmed_conversation

    def _group_conversation_pairs(
        self, messages: List[Dict[str, str]]
    ) -> List[List[Dict[str, str]]]:
        """Group conversation messages into user-assistant pairs.

        Args:
            messages (List[Dict[str, str]]): Conversation messages (no system).

        Returns:
            List[List[Dict[str, str]]]: Grouped message pairs.
        """
        pairs = []
        i = 0

        while i < len(messages):
            current_msg = messages[i]

            if current_msg["role"] == "user":
                # Start a new pair with user message
                pair = [current_msg]

                # Look for the next assistant message
                if i + 1 < len(messages) and messages[i + 1]["role"] == "assistant":
                    pair.append(messages[i + 1])
                    i += 2
                else:
                    # User message without assistant response
                    i += 1

                pairs.append(pair)
            else:
                # Skip standalone assistant messages (shouldn't happen in normal flow)
                i += 1

        return pairs

    def add_user_message(
        self, messages: List[Dict[str, str]], content: str
    ) -> List[Dict[str, str]]:
        """Add a user message to the conversation.

        Args:
            messages (List[Dict[str, str]]): Existing messages.
            content (str): User message content.

        Returns:
            List[Dict[str, str]]: Messages with new user message added.
        """
        return messages + [{"role": "user", "content": content.strip()}]

    def create_system_message(self, content: str) -> Dict[str, str]:
        """Create a system message in OpenAI format.

        Args:
            content (str): System message content.

        Returns:
            Dict[str, str]: System message in OpenAI format.
        """
        return {"role": "system", "content": content.strip()}

    def extract_message_content(
        self, messages: List[Dict[str, str]], role: str = "assistant"
    ) -> List[str]:
        """Extract content from messages with specific role.

        Args:
            messages (List[Dict[str, str]]): Messages to search.
            role (str, optional): Role to filter by. Defaults to "assistant".

        Returns:
            List[str]: List of message contents with the specified role.
        """
        return [msg["content"] for msg in messages if msg["role"] == role]

    def get_last_user_message(self, messages: List[Dict[str, str]]) -> str:
        """Get the last user message content.

        Args:
            messages (List[Dict[str, str]]): Messages to search.

        Returns:
            str: Last user message content, or empty string if none found.
        """
        user_messages = self.extract_message_content(messages, "user")
        return user_messages[-1] if user_messages else ""

    def validate_message_format(self, message: Dict[str, str]) -> bool:
        """Validate that a message has the correct OpenAI format.

        Args:
            message (Dict[str, str]): Message to validate.

        Returns:
            bool: True if valid format, False otherwise.
        """
        if not isinstance(message, dict):
            return False

        required_keys = {"role", "content"}
        if not required_keys.issubset(message.keys()):
            return False

        valid_roles = {"system", "user", "assistant"}
        if message["role"] not in valid_roles:
            return False

        if not isinstance(message["content"], str):
            return False

        return True

    def sanitize_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove invalid messages and sanitize content.

        Args:
            messages (List[Dict[str, str]]): Messages to sanitize.

        Returns:
            List[Dict[str, str]]: Sanitized messages.
        """
        sanitized = []

        for message in messages:
            if self.validate_message_format(message):
                # Sanitize content
                sanitized_content = message["content"].strip()
                if sanitized_content:  # Only add non-empty messages
                    sanitized.append(
                        {"role": message["role"], "content": sanitized_content}
                    )

        return sanitized
