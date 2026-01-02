"""Sidebar UI component for chat room management and model selection.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    Streamlit Sidebar: https://docs.streamlit.io/library/api-reference/layout/st.sidebar
"""

import streamlit as st
from typing import Optional, Tuple, List
from modules.client import OpenRouterClient
from modules.frontend.managers import SessionManager, ChatManager
from constants import DEFAULT_SYSTEM_PROMPT


class SidebarComponent:
    """Handles sidebar UI components (Single Responsibility Principle).

    This class manages all sidebar-related UI elements including chat room
    creation, model selection, and room navigation.
    """

    def __init__(self, session_manager: SessionManager, chat_manager: ChatManager):
        """Initialize the sidebar component.

        Args:
            session_manager (SessionManager): Session state manager.
            chat_manager (ChatManager): Chat operations manager.
        """
        self.session_manager = session_manager
        self.chat_manager = chat_manager

    def render(self) -> None:
        """Render the complete sidebar interface."""
        with st.sidebar:
            st.header("Chat Rooms")

            # Chat room creation section
            self._render_room_creation()

            # Model and settings section
            self._render_model_selection()

            st.divider()

            # Room list section
            self._render_room_list()

    def _render_room_creation(self) -> None:
        """Render the chat room creation form."""
        with st.form(key="create_room_form", clear_on_submit=True):
            new_room_name = st.text_input(
                "New chat room name",
                placeholder="Enter room name...",
                help="Create a new chat room for a different conversation",
            )

            system_prompt_message = st.text_area(
                "System Prompt",
                value=DEFAULT_SYSTEM_PROMPT,
                height=100,
                help="Set the AI's behavior and personality for this chat room",
            )

            submit_button = st.form_submit_button(
                "Create New Chat", use_container_width=True
            )

            if submit_button:
                self._handle_room_creation(new_room_name, system_prompt_message)

    def _handle_room_creation(self, room_name: str, system_prompt: str) -> None:
        """Handle chat room creation logic.

        Args:
            room_name (str): Name for the new room.
            system_prompt (str): System prompt for the room.
        """
        if not room_name or not room_name.strip():
            st.error("Please enter a name for the chat room")
            return

        try:
            room_id = self.chat_manager.create_chat_room(
                room_name.strip(), system_prompt
            )
            self.session_manager.active_room = room_id
            st.success(f"Created room: {room_name}")
            st.rerun()

        except ValueError as e:
            st.error(f"Error creating room: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

    def _render_model_selection(self) -> None:
        """Render model selection and configuration."""
        st.subheader("AI Model")

        # Model selection
        available_models = OpenRouterClient.get_available_models()

        col1, col2 = st.columns([2, 1])

        with col1:
            model_choice = st.selectbox(
                "Select Model",
                available_models,
                help="Choose the AI model for generating responses",
            )

        with col2:
            if st.button("🔄", help="Refresh model", use_container_width=True):
                self._refresh_model(model_choice)

        # Model info display
        self._render_model_info(model_choice)

        # History settings
        history_token = st.slider(
            "Conversation History",
            min_value=5,
            max_value=25,
            value=self.session_manager.history_chat,
            step=1,
            help="Number of previous message pairs to include in context",
        )

        # Update session state
        self.session_manager.history_token = history_token
        self.session_manager.history_chat = history_token

        # Create or update chat model
        self._update_chat_model(model_choice)

        # Model status indicator
        self._render_model_status()

    def _render_model_info(self, model_choice: str) -> None:
        """Render information about the selected model.

        Args:
            model_choice (str): Selected model name.
        """
        # Extract provider and model info
        if "/" in model_choice:
            provider, model_info = model_choice.split("/", 1)

            # Create a compact info display
            with st.expander("ℹ️ Model Info", expanded=False):
                st.markdown(f"**Provider:** {provider.title()}")
                st.markdown(f"**Model:** {model_info}")

                # Add model-specific information
                if "vision" in model_choice.lower():
                    st.info("🖼️ This model supports image understanding")
                if "coder" in model_choice.lower() or "code" in model_choice.lower():
                    st.info("💻 This model is optimized for coding tasks")
                if ":free" in model_choice:
                    st.success("🆓 Free model - no cost per request")

    def _update_chat_model(self, model_choice: str) -> None:
        """Update the chat model in session state.

        Args:
            model_choice (str): Selected model name.
        """
        try:
            # Create new client instance with selected model
            new_client = OpenRouterClient(default_model=model_choice)
            self.session_manager.chat_model = new_client

        except Exception as e:
            st.error(f"Failed to initialize model: {str(e)}")
            self.session_manager.chat_model = None

    def _refresh_model(self, model_choice: str) -> None:
        """Refresh the chat model connection.

        Args:
            model_choice (str): Current model choice.
        """
        with st.spinner("Refreshing model connection..."):
            self._update_chat_model(model_choice)

            if self.session_manager.has_chat_model():
                is_working = self.chat_manager.test_chat_model(
                    self.session_manager.chat_model
                )
                if is_working:
                    st.success("Model connection refreshed successfully")
                else:
                    st.error("Model connection test failed")
            else:
                st.error("Failed to refresh model")

    def _render_model_status(self) -> None:
        """Render current model status information."""
        if not self.session_manager.has_chat_model():
            st.warning("⚠️ No model configured")
            return

        try:
            model_info = self.chat_manager.get_model_info(
                self.session_manager.chat_model
            )
            status = model_info.get("status", "unknown")
            model_name = model_info.get("model", "unknown")

            # Create a compact status display
            status_container = st.container()
            with status_container:
                if status == "connected":
                    st.success(f"✅ {self._get_short_model_name(model_name)}")
                elif status == "disconnected":
                    st.error(f"❌ {self._get_short_model_name(model_name)}")
                else:
                    st.warning(f"⚠️ {self._get_short_model_name(model_name)}")

        except Exception:
            st.error("❌ Model status check failed")

    def _get_short_model_name(self, full_model_name: str) -> str:
        """Get a shortened version of the model name for display.

        Args:
            full_model_name (str): Full model name.

        Returns:
            str: Shortened model name.
        """
        if "/" in full_model_name:
            parts = full_model_name.split("/")
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1].split(':')[0]}"
        return (
            full_model_name[:30] + "..."
            if len(full_model_name) > 30
            else full_model_name
        )

    def _render_room_list(self) -> None:
        """Render the list of existing chat rooms."""
        st.subheader("Your Rooms")

        try:
            rooms = self.chat_manager.get_all_chat_rooms()

            if not rooms:
                st.info("No chat rooms yet. Create one above!")
                return

            # Display rooms
            for room_id, room_name, created_at in rooms:
                self._render_room_button(room_id, room_name, created_at)

        except Exception as e:
            st.error(f"Failed to load chat rooms: {str(e)}")

    def _render_room_button(
        self, room_id: str, room_name: str, created_at: str
    ) -> None:
        """Render a single room button with additional info.

        Args:
            room_id (str): The room ID.
            room_name (str): The room name.
            created_at (str): Creation timestamp.
        """
        # Create columns for room info and actions
        col1, col2 = st.columns([4, 1])

        with col1:
            # Main room button
            display_name = f"{room_name} - {created_at.split('.')[0]}"
            is_active = self.session_manager.active_room == room_id

            button_type = "primary" if is_active else "secondary"
            if st.button(
                display_name,
                key=f"room_{room_id}",
                type=button_type,
                use_container_width=True,
                help=f"Switch to {room_name}",
            ):
                self._handle_room_selection(room_id)

        with col2:
            # Room info (message count, etc.)
            try:
                message_count = self.chat_manager.count_room_messages(room_id)
                st.caption(f"{message_count} msgs")
            except Exception:
                st.caption("?")

    def _handle_room_selection(self, room_id: str) -> None:
        """Handle room selection logic.

        Args:
            room_id (str): Selected room ID.
        """
        try:
            # Verify room exists
            room_info = self.chat_manager.get_chat_room_info(room_id)
            if room_info is None:
                st.error("Room not found")
                return

            # Set active room
            self.session_manager.active_room = room_id
            st.rerun()

        except Exception as e:
            st.error(f"Failed to select room: {str(e)}")

    def get_current_room_info(self) -> Optional[Tuple[str, str]]:
        """Get information about the currently active room.

        Returns:
            Optional[Tuple[str, str]]: (room_name, created_at) or None if no active room.
        """
        if not self.session_manager.has_active_room():
            return None

        return self.chat_manager.get_chat_room_info(self.session_manager.active_room)
