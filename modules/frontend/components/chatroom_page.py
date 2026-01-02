"""Chatroom page component for individual chat sessions.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    Streamlit Chat Elements: https://docs.streamlit.io/develop/api-reference/chat
"""

import streamlit as st
from datetime import datetime
from typing import List
from modules.frontend.managers import SessionManager, ChatManager, MessageManager
from modules.frontend.components.message_display import MessageDisplayComponent
from modules.client import OpenRouterClient


class ChatroomPageComponent:
    """Handles individual chatroom page interface (Single Responsibility Principle).

    This component manages a single chat session including message display,
    user input, AI responses, and room-specific navigation.
    """

    def __init__(
        self,
        session_manager: SessionManager,
        chat_manager: ChatManager,
        message_manager: MessageManager,
        message_display: MessageDisplayComponent,
    ):
        """Initialize the chatroom page component.

        Args:
            session_manager (SessionManager): Session state manager.
            chat_manager (ChatManager): Chat operations manager.
            message_manager (MessageManager): Message processing manager.
            message_display (MessageDisplayComponent): Message display component.
        """
        self.session_manager = session_manager
        self.chat_manager = chat_manager
        self.message_manager = message_manager
        self.message_display = message_display

    def render(self) -> None:
        """Render the chatroom page interface."""
        # Configure sidebar for chat settings
        self._render_sidebar_config()

        if not self.session_manager.has_active_room():
            self._render_no_room_error()
            return

        # Get current room info
        room_info = self.chat_manager.get_chat_room_info(
            self.session_manager.active_room
        )
        if not room_info:
            self._render_room_not_found()
            return

        room_name, created_at = room_info

        # Initialize the room model if not already configured
        self._initialize_room_model()

        # Note: Header is now handled by the page file itself
        # Render chat interface using Streamlit's built-in elements with real streaming
        self._render_streamlit_chat_interface()

    def _render_sidebar_config(self) -> None:
        """Render configuration sidebar with model selection and chat settings."""
        with st.sidebar:
            st.header("⚙️ Chat Configuration")

            if self.session_manager.has_active_room():
                # Model selection section
                with st.expander("🤖 AI Model", expanded=True):
                    self._render_model_selection()

                # Chat history settings
                with st.expander("📝 Chat History", expanded=False):
                    self._render_history_settings()

                # Room management
                with st.expander("🏠 Room Management", expanded=False):
                    self._render_room_management()

                # Export options
                with st.expander("📤 Export Chat", expanded=False):
                    self._render_export_options()

                # Bottom navigation button
                st.divider()
                if st.button(
                    "🏠 Back to Homepage", use_container_width=True, type="primary"
                ):
                    self._go_to_homepage()
            else:
                st.info("Select a chat room to access configuration options.")

    def _render_model_selection(self) -> None:
        """Render model selection interface."""
        current_room = self.session_manager.active_room
        current_model = self.session_manager.get_state_value(
            f"room_model_{current_room}", OpenRouterClient.get_available_models()[0]
        )

        # Check if model is actually initialized
        chat_client = self.session_manager.chat_model
        is_initialized = chat_client is not None
        actual_model = chat_client.default_model if chat_client else None

        # Model selection
        new_model = st.selectbox(
            "Select Model",
            OpenRouterClient.get_available_models(),
            help="Choose the AI model for this chat room",
        )

        # Show model info
        if new_model != current_model:
            st.info(f"🔄 Model will change to: {new_model}")
            if st.button("✅ Apply Model Change", use_container_width=True):
                self._change_room_model(new_model)

        # Current model display with status
        if is_initialized and actual_model == current_model:
            st.success(f"🤖 Active: {self._get_short_model_name(current_model)}")
        elif is_initialized and actual_model != current_model:
            st.warning(
                f"⚠️ Mismatch - Expected: {self._get_short_model_name(current_model)}, Active: {self._get_short_model_name(actual_model)}"
            )
        else:
            st.error(f"❌ Not initialized: {self._get_short_model_name(current_model)}")

        # Model capabilities
        self._show_model_capabilities(current_model)

        # Debug: Force reinitialize button if model not working
        if not is_initialized or actual_model != current_model:
            if st.button(
                "🔄 Force Reinitialize Model",
                use_container_width=True,
                help="Force reinitialize the AI model",
            ):
                try:
                    self._initialize_room_model()
                    st.success("Model reinitialized!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to reinitialize: {str(e)}")

    def _render_history_settings(self) -> None:
        """Render chat history management settings."""
        # History limit setting
        current_limit = self.session_manager.history_token
        new_limit = st.slider(
            "Context Window (message pairs)",
            min_value=3,
            max_value=50,
            value=current_limit,
            help="Number of previous message pairs to include in AI context",
        )

        if new_limit != current_limit:
            self.session_manager.history_token = new_limit
            st.success(f"📝 Context updated to {new_limit} message pairs")

        # Message count info
        try:
            db_messages = self.chat_manager.get_room_messages(
                self.session_manager.active_room
            )
            total_messages = len(db_messages)
            user_messages = len([m for m in db_messages if m[0] == "human"])
            ai_messages = len([m for m in db_messages if m[0] == "assistant"])

            st.metric("Total Messages", total_messages)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Your Messages", user_messages)
            with col2:
                st.metric("AI Messages", ai_messages)

        except Exception:
            st.warning("Unable to load message statistics")

        # Trim chat history
        if st.button(
            "✂️ Trim to Context Window",
            use_container_width=True,
            help="Keep only recent messages within context window",
        ):
            self._trim_chat_history()

    def _render_room_management(self) -> None:
        """Render room management options."""
        room_info = self.chat_manager.get_chat_room_info(
            self.session_manager.active_room
        )
        if room_info:
            room_name, created_at = room_info

            st.markdown(f"**Room:** {room_name}")
            st.markdown(f"**Created:** {created_at.split('.')[0]}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🏠 Home", use_container_width=True):
                    self._go_to_homepage()

            with col2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()

    def _render_export_options(self) -> None:
        """Render chat export options."""
        try:
            db_messages = self.chat_manager.get_room_messages(
                self.session_manager.active_room
            )

            if not db_messages:
                st.info("No messages to export")
                return

            # Export as text
            if st.button("📄 Export as Text", use_container_width=True):
                self._export_as_text(db_messages)

            # Export as JSON
            if st.button("📋 Export as JSON", use_container_width=True):
                self._export_as_json(db_messages)

        except Exception as e:
            st.error(f"Export unavailable: {str(e)}")

    def _render_streamlit_chat_interface(self) -> None:
        """Render the chat interface using only Streamlit's built-in chat elements."""
        # Get messages from database
        db_messages = self.chat_manager.get_room_messages(
            self.session_manager.active_room
        )

        if not db_messages:
            # Show welcome message using st.chat_message
            self._render_welcome_message_builtin()
        else:
            # Render message history using st.chat_message
            self._render_messages_with_builtin_elements(db_messages)

        # Use st.chat_input for user input (Streamlit handles positioning)
        self._render_builtin_chat_input()

    def _render_welcome_message_builtin(self) -> None:
        """Render welcome message using Streamlit's built-in chat elements."""
        room_info = self.chat_manager.get_chat_room_info(
            self.session_manager.active_room
        )
        room_name = room_info[0] if room_info else "Chat Room"

        with st.chat_message("assistant"):
            st.markdown(
                f"""
            🎉 **Welcome to {room_name}!**

            I'm your AI assistant, ready to help with:
            - ❓ Answering questions
            - 💡 Creative brainstorming
            - 💻 Coding assistance
            - 📝 Writing and editing
            - 🔍 Research and analysis

            Just type a message below to get started!
            """
            )

    def _render_messages_with_builtin_elements(self, db_messages: List) -> None:
        """Render messages using Streamlit's built-in chat elements."""
        # Get context window limit
        history_limit = (
            self.session_manager.history_token * 2
        )  # Convert pairs to individual messages

        # Show only recent messages within context window
        if len(db_messages) > history_limit:
            shown_messages = db_messages[-history_limit:]

            # Show info about hidden messages
            hidden_count = len(db_messages) - len(shown_messages)
            st.info(
                f"📜 Showing last {len(shown_messages)} messages ({hidden_count} older messages hidden)"
            )
        else:
            shown_messages = db_messages

        # Render each message using st.chat_message
        for role, content, llm_model, timestamp in shown_messages:
            # Convert database role to chat_message role
            if role == "human":
                chat_role = "user"
            elif role == "assistant":
                chat_role = "assistant"
            else:
                chat_role = "assistant"  # fallback

            with st.chat_message(chat_role):
                # Add timestamp and model info for assistant messages
                if chat_role == "assistant" and llm_model:
                    st.caption(
                        f"🤖 {self._get_short_model_name(llm_model)} • {timestamp.split('.')[0] if '.' in timestamp else timestamp}"
                    )

                # Render the message content
                st.markdown(content)

    def _render_builtin_chat_input(self) -> None:
        """Render chat input using Streamlit's st.chat_input."""
        # Get room info for personalized placeholder
        room_info = self.chat_manager.get_chat_room_info(
            self.session_manager.active_room
        )
        room_name = room_info[0] if room_info else "this room"

        user_input = st.chat_input(placeholder=f"Ask me anything about {room_name}...")

        if user_input:
            self._process_user_input(user_input)

    def _process_user_input(self, user_message: str) -> None:
        """Process user input and generate AI response using Streamlit's built-in streaming."""
        if not user_message.strip():
            st.warning("Please enter a message")
            return

        if not self.session_manager.has_chat_model():
            st.error("🤖 No AI model configured for this room")
            return

        try:
            # Show user message immediately using st.chat_message
            with st.chat_message("user"):
                st.markdown(user_message)

            # Show AI response using st.chat_message with st.write_stream
            with st.chat_message("assistant"):
                # Prepare messages for AI
                final_messages = self._prepare_messages_for_ai(user_message)

                # Use st.status for long-running AI generation
                with st.status("Generating response...", expanded=True) as status:
                    try:
                        # Use st.write_stream with the actual stream from OpenRouter
                        response_stream = self.session_manager.chat_model.stream_chat(
                            final_messages
                        )
                        full_response = st.write_stream(response_stream)

                        status.update(
                            label="Response complete!", state="complete", expanded=False
                        )

                    except Exception:
                        status.update(
                            label="Stream failed, using fallback",
                            state="error",
                            expanded=False,
                        )
                        # Fallback to non-streaming if stream fails
                        response = self.session_manager.chat_model.chat(final_messages)
                        full_response = (
                            response.content
                            if hasattr(response, "content")
                            else str(response)
                        )
                        st.markdown(full_response)

            # Save messages to database
            self.chat_manager.add_user_message(
                self.session_manager.active_room, user_message
            )
            self.chat_manager.add_ai_message(
                self.session_manager.active_room,
                full_response,
                self.session_manager.chat_model.default_model,
            )

            # Rerun to refresh the interface
            st.rerun()

        except Exception as e:
            st.error(f"Error processing message: {str(e)}")

    def _prepare_messages_for_ai(self, user_message: str) -> list:
        """Prepare messages for AI processing with proper context."""
        # Get conversation context
        db_messages = self.chat_manager.get_room_messages(
            self.session_manager.active_room
        )

        # Add the current user message to context
        current_messages = db_messages + [("human", user_message, "", "")]

        # Convert to OpenAI format
        openai_messages = self.message_manager.db_messages_to_openai_format(
            current_messages
        )

        # Trim to history limit
        trimmed_messages = self.message_manager.trim_messages(
            openai_messages, self.session_manager.history_token
        )

        # Sanitize messages
        final_messages = self.message_manager.sanitize_messages(trimmed_messages)

        return final_messages

    def _handle_message_processing(self) -> None:
        """Handle any pending message processing."""
        # This method can be used for any post-render processing
        pass

    def _change_room_model(self, new_model: str) -> None:
        """Change the AI model for the current room."""
        try:
            current_room = self.session_manager.active_room

            # Update room model in session state
            self.session_manager.set_state_value(
                f"room_model_{current_room}", new_model
            )

            # Create new client with updated model
            new_client = OpenRouterClient(default_model=new_model)
            self.session_manager.chat_model = new_client

            st.success(f"🤖 Model changed to {self._get_short_model_name(new_model)}")

            # Brief delay to show the success message
            import time

            time.sleep(0.5)

            st.rerun()

        except Exception as e:
            st.error(f"Failed to change model: {str(e)}")
            # Try to reinitialize with the old model
            self._initialize_room_model()

    def _trim_chat_history(self) -> None:
        """Trim chat history to context window size."""
        try:
            # Get current messages
            db_messages = self.chat_manager.get_room_messages(
                self.session_manager.active_room
            )

            # Calculate how many to keep
            history_limit = (
                self.session_manager.history_token * 2
            )  # Convert pairs to individual messages

            if len(db_messages) <= history_limit:
                st.info("Chat history is already within the context window")
                return

            # This would require implementing a trim function in the database
            # For now, show info about what would be trimmed
            messages_to_remove = len(db_messages) - history_limit
            st.warning(
                f"Would remove {messages_to_remove} older messages (keeping {history_limit} recent messages)"
            )
            st.info(
                "💡 Trimming feature requires database implementation - currently showing filtered view only"
            )

        except Exception as e:
            st.error(f"Failed to trim history: {str(e)}")

    def _export_as_text(self, db_messages: List) -> None:
        """Export chat as plain text."""
        try:
            room_info = self.chat_manager.get_chat_room_info(
                self.session_manager.active_room
            )
            room_name = room_info[0] if room_info else "Chat Room"

            export_text = f"Chat Export: {room_name}\n"
            export_text += "=" * 50 + "\n\n"

            for role, content, llm_model, timestamp in db_messages:
                role_display = "You" if role == "human" else "Assistant"
                export_text += f"{role_display} ({timestamp}):\n{content}\n\n"

            st.download_button(
                label="💾 Download Text File",
                data=export_text,
                file_name=f"{room_name}_chat_export.txt",
                mime="text/plain",
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"Export failed: {str(e)}")

    def _export_as_json(self, db_messages: List) -> None:
        """Export chat as JSON."""
        try:
            import json

            room_info = self.chat_manager.get_chat_room_info(
                self.session_manager.active_room
            )
            room_name = room_info[0] if room_info else "Chat Room"

            export_data = {
                "room_name": room_name,
                "export_timestamp": str(datetime.now()),
                "messages": [
                    {
                        "role": role,
                        "content": content,
                        "model": llm_model,
                        "timestamp": timestamp,
                    }
                    for role, content, llm_model, timestamp in db_messages
                ],
            }

            st.download_button(
                label="📄 Download JSON File",
                data=json.dumps(export_data, indent=2),
                file_name=f"{room_name}_chat_export.json",
                mime="application/json",
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"JSON export failed: {str(e)}")

    def _show_model_capabilities(self, model_name: str) -> None:
        """Show model capabilities and information."""
        capabilities = []

        if ":free" in model_name:
            capabilities.append("🆓 Free to use")
        if "vision" in model_name.lower():
            capabilities.append("🖼️ Image understanding")
        if "coder" in model_name.lower() or "code" in model_name.lower():
            capabilities.append("💻 Code specialist")

        if capabilities:
            st.markdown("**Capabilities:**")
            for cap in capabilities:
                st.markdown(f"• {cap}")

    def _get_short_model_name(self, full_model_name: str) -> str:
        """Get a shortened version of the model name."""
        if "/" in full_model_name:
            parts = full_model_name.split("/")
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1].split(':')[0]}"
        return (
            full_model_name[:30] + "..."
            if len(full_model_name) > 30
            else full_model_name
        )

    def _initialize_room_model(self) -> None:
        """Initialize the AI model for this room."""
        current_room = self.session_manager.active_room
        room_model = self.session_manager.get_state_value(f"room_model_{current_room}")

        # Check if we need to initialize or update the model
        current_client = self.session_manager.chat_model

        if room_model:
            # If we have a room model but no client, or the client model differs, create new client
            if not current_client or current_client.default_model != room_model:
                try:
                    client = OpenRouterClient(default_model=room_model)
                    self.session_manager.chat_model = client
                    print(f"✅ Initialized model: {room_model}")
                except Exception as e:
                    st.error(f"Failed to initialize model {room_model}: {str(e)}")
        else:
            # No room model set, use default and save it
            try:
                default_model = OpenRouterClient.get_available_models()[0]
                client = OpenRouterClient(default_model=default_model)
                self.session_manager.chat_model = client
                self.session_manager.set_state_value(
                    f"room_model_{current_room}", default_model
                )
                print(f"✅ Initialized default model: {default_model}")
            except Exception as e:
                st.error(f"Failed to initialize default model: {str(e)}")

    def _render_no_room_error(self) -> None:
        """Render error when no room is selected."""
        st.error("❌ No chatroom selected")
        if st.button("🏠 Back to Homepage"):
            self._go_to_homepage()

    def _render_room_not_found(self) -> None:
        """Render error when room is not found."""
        st.error("❌ Chatroom not found")
        if st.button("🏠 Back to Homepage"):
            self._go_to_homepage()
        self.session_manager.active_room = None

    def _go_to_homepage(self) -> None:
        """Navigate back to homepage by clearing session state and rerunning."""
        # Clear active room
        self.session_manager.active_room = None

        # Trigger rerun to switch to homepage view
        st.rerun()
