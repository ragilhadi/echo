"""Message display UI component for chat messages.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    Streamlit Chat Elements: https://docs.streamlit.io/library/api-reference/chat
"""

import streamlit as st
from typing import List, Tuple
from constants import ChatRole


class MessageDisplayComponent:
    """Handles message display UI (Single Responsibility Principle).

    This class manages the rendering of chat messages in different formats
    and styles based on the message type and sender, with ChatGPT-like appearance.
    """

    def __init__(self):
        """Initialize the message display component."""
        self.role_config = {
            ChatRole.HUMAN: {
                "icon": "👤",
                "label": "You",
                "badge_color": "blue",
                "avatar": "user",
            },
            ChatRole.AI: {
                "icon": "🤖",
                "label": "Assistant",
                "badge_color": "green",
                "avatar": "assistant",
            },
            ChatRole.SYSTEM: {
                "icon": "⚙️",
                "label": "System",
                "badge_color": "gray",
                "avatar": "assistant",
            },
        }

        # Inject ChatGPT-like CSS styling
        self._inject_message_styles()

    def _inject_message_styles(self) -> None:
        """Inject CSS for ChatGPT-like message styling."""
        css_styles = """
        <style>
        /* ChatGPT-like message styling */
        .stChatMessage {
            margin-bottom: 1.5rem !important;
            border-radius: 8px !important;
        }

        /* User message styling */
        .stChatMessage[data-testid="chat-message-user"] {
            background-color: transparent !important;
        }

        /* Assistant message styling */
        .stChatMessage[data-testid="chat-message-assistant"] {
            background-color: #f7f7f8 !important;
            border: 1px solid #e5e5e5 !important;
        }

        /* Message content styling */
        .stChatMessage .stMarkdown {
            padding: 0.5rem 0 !important;
        }

        /* Badge styling */
        .stChatMessage .stBadge {
            margin-bottom: 0.5rem !important;
        }

        /* Improve text readability */
        .stChatMessage p {
            line-height: 1.6 !important;
            margin-bottom: 0.5rem !important;
        }

        /* Typing indicator animation */
        .typing-indicator {
            animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        /* Message spacing */
        .chat-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        </style>
        """
        st.markdown(css_styles, unsafe_allow_html=True)

    def render_messages(self, messages: List[Tuple[str, str, str, str]]) -> None:
        """Render a list of messages from the database with ChatGPT-like layout.

        Args:
            messages (List[Tuple[str, str, str, str]]): Messages as (role, content, llm, timestamp) tuples.
        """
        if not messages:
            return

        # Render messages in a container for better layout
        with st.container():
            for role, content, llm, timestamp in messages:
                self._render_single_message(role, content, llm, timestamp)

    def _render_single_message(
        self, role: str, content: str, llm: str, timestamp: str
    ) -> None:
        """Render a single message with ChatGPT-like styling.

        Args:
            role (str): Message role (human, assistant, system).
            content (str): Message content.
            llm (str): LLM model name (for AI messages).
            timestamp (str): Message timestamp.
        """
        # Skip empty messages
        if not content or not content.strip():
            return

        # Skip system messages from display (they're for AI context only)
        if role == ChatRole.SYSTEM:
            return

        # Get role configuration
        config = self.role_config.get(role, self.role_config[ChatRole.HUMAN])

        # Render message with appropriate chat message container
        with st.chat_message(config["avatar"]):
            self._render_message_header(config, role, llm)
            self._render_message_content(content)

    def _render_message_header(self, config: dict, role: str, llm: str) -> None:
        """Render the message header with badge and model info.

        Args:
            config (dict): Role configuration.
            role (str): Message role.
            llm (str): LLM model name.
        """
        # Create header with proper spacing
        header_col1, header_col2 = st.columns([1, 4])

        with header_col1:
            if role == ChatRole.AI and llm:
                # For AI messages, show a more detailed label
                st.markdown(
                    f"""
                    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                        <span style='font-weight: 600; color: #374151;'>{config['label']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                # For user messages, simple label
                st.markdown(
                    f"""
                    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                        <span style='font-weight: 600; color: #374151;'>{config['label']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with header_col2:
            if role == ChatRole.AI and llm:
                # Show model name for AI responses
                st.caption(f"Model: {llm}")

    def _render_message_content(self, content: str) -> None:
        """Render the main message content with improved formatting.

        Args:
            content (str): Message content to render.
        """
        # Render content in a styled container
        st.markdown(
            f"""
            <div style='color: #374151; line-height: 1.6; word-wrap: break-word;'>
                {self._format_message_content(content)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _format_message_content(self, content: str) -> str:
        """Format message content for better display.

        Args:
            content (str): Raw message content.

        Returns:
            str: Formatted content.
        """
        # Basic markdown formatting (Streamlit will handle most of this)
        # Just ensure proper line breaks and spacing
        formatted_content = content.replace("\n", "<br>")
        return formatted_content

    def render_streaming_message(self, role: str, model_name: str) -> st.empty:
        """Start rendering a streaming message and return the placeholder.

        Args:
            role (str): Message role (should be assistant for streaming).
            model_name (str): Name of the model generating the response.

        Returns:
            st.empty: Streamlit placeholder for updating content.
        """
        config = self.role_config.get(role, self.role_config[ChatRole.AI])

        with st.chat_message(config["avatar"]):
            # Render header for streaming message
            self._render_streaming_header(config, model_name)

            # Return placeholder for streaming content
            return st.empty()

    def _render_streaming_header(self, config: dict, model_name: str) -> None:
        """Render header for streaming messages.

        Args:
            config (dict): Role configuration.
            model_name (str): Model name.
        """
        header_col1, header_col2 = st.columns([1, 4])

        with header_col1:
            st.markdown(
                f"""
                <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                    <span style='font-weight: 600; color: #374151;'>{config['label']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with header_col2:
            # Show typing indicator and model
            st.markdown(
                f"""
                <div class='typing-indicator' style='font-size: 0.8rem; color: #6b7280;'>
                    <span>Thinking... </span>
                    <span style='font-size: 0.7rem;'>({model_name})</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    def update_streaming_message(
        self, placeholder: st.empty, content: str, is_complete: bool = False
    ) -> None:
        """Update a streaming message placeholder with new content.

        Args:
            placeholder (st.empty): Streamlit placeholder to update.
            content (str): Current content to display.
            is_complete (bool, optional): Whether the message is complete. Defaults to False.
        """
        if is_complete:
            # Final message without typing indicator
            placeholder.markdown(
                f"""
                <div style='color: #374151; line-height: 1.6; word-wrap: break-word;'>
                    {self._format_message_content(content)}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Show typing indicator with content
            placeholder.markdown(
                f"""
                <div style='color: #374151; line-height: 1.6; word-wrap: break-word;'>
                    {self._format_message_content(content)}
                    <span class='typing-indicator' style='color: #6b7280;'>▊</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    def render_error_message(self, error_message: str) -> None:
        """Render an error message in the chat.

        Args:
            error_message (str): Error message to display.
        """
        with st.chat_message("assistant"):
            st.markdown(
                """
                <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                    <span style='font-weight: 600; color: #dc2626;'>⚠️ Error</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div style='color: #dc2626; background-color: #fef2f2; padding: 12px; border-radius: 6px; border-left: 4px solid #dc2626;'>
                    {error_message}
                </div>
                """,
                unsafe_allow_html=True,
            )

    def render_system_info(self, info_message: str) -> None:
        """Render a system information message.

        Args:
            info_message (str): Information message to display.
        """
        st.markdown(
            f"""
            <div style='text-align: center; padding: 12px; margin: 16px 0; background-color: #f0f9ff; border-radius: 6px; color: #0369a1; border: 1px solid #bae6fd;'>
                ℹ️ {info_message}
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_typing_indicator(self) -> st.empty:
        """Render a typing indicator for AI responses.

        Returns:
            st.empty: Placeholder for the typing indicator.
        """
        with st.chat_message("assistant"):
            st.markdown(
                """
                <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                    <span style='font-weight: 600; color: #374151;'>Assistant</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            placeholder = st.empty()
            placeholder.markdown(
                """
                <div class='typing-indicator' style='color: #6b7280; font-style: italic;'>
                    Thinking...
                </div>
                """,
                unsafe_allow_html=True,
            )
            return placeholder

    def clear_typing_indicator(self, placeholder: st.empty) -> None:
        """Clear the typing indicator.

        Args:
            placeholder (st.empty): Typing indicator placeholder to clear.
        """
        placeholder.empty()

    def render_welcome_message(self, room_name: str) -> None:
        """Render a welcome message for new chat rooms.

        Args:
            room_name (str): Name of the chat room.
        """
        st.markdown(
            f"""
            <div style='text-align: center; padding: 40px 20px; color: #6b7280; background-color: #f9fafb; border-radius: 8px; margin: 20px 0;'>
                <h3 style='color: #374151; margin-bottom: 16px;'>Welcome to {room_name}! 👋</h3>
                <p style='margin-bottom: 8px;'>Start a conversation by typing a message below.</p>
                <p style='font-size: 0.9em; color: #9ca3af;'>
                    💡 Your conversation history will appear here as you chat.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_model_change_notice(self, old_model: str, new_model: str) -> None:
        """Render a notice about model changes.

        Args:
            old_model (str): Previous model name.
            new_model (str): New model name.
        """
        st.markdown(
            f"""
            <div style='text-align: center; padding: 8px 16px; margin: 12px 0; background-color: #fef3c7; border-radius: 6px; color: #92400e; font-size: 0.9em;'>
                🔄 Model changed from {old_model} to {new_model}
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_connection_status(self, is_connected: bool, model_name: str) -> None:
        """Render connection status information.

        Args:
            is_connected (bool): Whether the model is connected.
            model_name (str): Name of the model.
        """
        if is_connected:
            st.markdown(
                f"""
                <div style='text-align: center; padding: 8px 16px; margin: 12px 0; background-color: #d1fae5; border-radius: 6px; color: #065f46; font-size: 0.9em;'>
                    ✅ Connected to {model_name}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div style='text-align: center; padding: 8px 16px; margin: 12px 0; background-color: #fee2e2; border-radius: 6px; color: #991b1b; font-size: 0.9em;'>
                    ❌ Failed to connect to {model_name}
                </div>
                """,
                unsafe_allow_html=True,
            )

    def count_visible_messages(self, messages: List[Tuple[str, str, str, str]]) -> int:
        """Count how many messages will be visibly rendered.

        Args:
            messages (List[Tuple[str, str, str, str]]): Messages to count.

        Returns:
            int: Number of visible messages.
        """
        count = 0
        for role, content, llm, timestamp in messages:
            # Skip empty messages and system messages
            if content and content.strip() and role != ChatRole.SYSTEM:
                count += 1
        return count

    def render_message_separator(self, text: str = "Today") -> None:
        """Render a message separator (like date separators in ChatGPT).

        Args:
            text (str, optional): Separator text. Defaults to "Today".
        """
        st.markdown(
            f"""
            <div style='text-align: center; margin: 24px 0; position: relative;'>
                <div style='border-top: 1px solid #e5e7eb; width: 100%;'></div>
                <div style='position: absolute; top: -8px; left: 50%; transform: translateX(-50%); background: white; padding: 0 12px; color: #6b7280; font-size: 0.8rem;'>
                    {text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
