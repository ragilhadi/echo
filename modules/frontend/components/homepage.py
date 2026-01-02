"""Homepage component for chatroom management.

Authors:
    Ragil Hadi (ragilhadi@ragilhadi.com)

References:
    Streamlit Layout: https://docs.streamlit.io/library/api-reference/layout
"""

import streamlit as st
from modules.frontend.managers import SessionManager, ChatManager
from modules.client import OpenRouterClient
from constants import DEFAULT_SYSTEM_PROMPT


class HomepageComponent:
    """Handles the homepage interface for chatroom management (Single Responsibility Principle).

    This component manages the main landing page where users can view existing
    chatrooms and create new ones.
    """

    def __init__(self, session_manager: SessionManager, chat_manager: ChatManager):
        """Initialize the homepage component.

        Args:
            session_manager (SessionManager): Session state manager.
            chat_manager (ChatManager): Chat operations manager.
        """
        self.session_manager = session_manager
        self.chat_manager = chat_manager

    def render(self) -> None:
        """Render the complete homepage interface."""
        # Page header
        self._render_header()

        # Main content in columns
        col1, col2 = st.columns([2, 1])

        with col1:
            # Existing chatrooms
            self._render_chatroom_list()

        with col2:
            # Create new chatroom form
            self._render_create_room_form()

    def _render_header(self) -> None:
        """Render the homepage header."""
        st.title("💬 Chat Assistant")
        st.caption("Powered by OpenRouter AI")
        st.divider()

    def _render_chatroom_list(self) -> None:
        """Render the list of existing chatrooms."""
        st.markdown("## 📂 Your Chat Rooms")

        try:
            rooms = self.chat_manager.get_all_chat_rooms()

            if not rooms:
                self._render_empty_state()
                return

            # Check if there's a newly created room to highlight
            newly_created_room = self.session_manager.get_state_value(
                "newly_created_room"
            )

            # Show quick access for newly created room
            if newly_created_room:
                # Find the room info
                new_room_info = None
                for room_id, room_name, created_at in rooms:
                    if room_id == newly_created_room:
                        new_room_info = (room_id, room_name, created_at)
                        break

                if new_room_info:
                    room_id, room_name, created_at = new_room_info
                    # Show highlighted new room with quick access
                    st.success(
                        f"🎉 New Room Created: **{room_name}** - Ready to start chatting!"
                    )

                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(
                            "Enter New Room",
                            key="enter_newly_created",
                            type="primary",
                            use_container_width=True,
                        ):
                            self._enter_chatroom(room_id)

                    with col2:
                        if st.button(
                            "✅ Dismiss",
                            key="dismiss_new_room",
                            use_container_width=True,
                        ):
                            self.session_manager.set_state_value(
                                "newly_created_room", None
                            )
                            st.rerun()

                    st.divider()

            # Display all rooms
            for room_id, room_name, created_at in rooms:
                # Highlight the newly created room
                is_new_room = newly_created_room == room_id
                self._render_room_card(
                    room_id, room_name, created_at, highlight=is_new_room
                )

        except Exception as e:
            st.error(f"Failed to load chat rooms: {str(e)}")

    def _render_empty_state(self) -> None:
        """Render empty state when no rooms exist."""
        st.info("📝 No chat rooms yet. Create your first chat room to get started!")

    def _render_room_card(
        self, room_id: str, room_name: str, created_at: str, highlight: bool = False
    ) -> None:
        """Render a single chatroom card.

        Args:
            room_id (str): The room ID.
            room_name (str): The room name.
            created_at (str): Creation timestamp.
            highlight (bool, optional): Whether to highlight this room as newly created.
        """
        # Get message count
        try:
            message_count = self.chat_manager.count_room_messages(room_id)
        except Exception:
            message_count = 0

        # Format creation date
        formatted_date = created_at.split(".")[0] if "." in created_at else created_at

        # Create room card container with standard Streamlit styling
        with st.container():
            # Room card using standard elements
            col1, col2 = st.columns([3, 1])

            with col1:
                if highlight:
                    st.markdown(f"### {room_name} ✨")
                else:
                    st.markdown(f"### {room_name}")
                st.caption(f"Created: {formatted_date}")

            with col2:
                st.metric("Messages", message_count)

            # Check if this room is in delete confirmation mode
            confirmation_key = f"confirm_delete_{room_id}"
            clear_confirmation_key = f"confirm_clear_{room_id}"

            is_confirming_delete = self.session_manager.get_state_value(
                confirmation_key, False
            )
            is_confirming_clear = self.session_manager.get_state_value(
                clear_confirmation_key, False
            )

            # Show confirmation dialogs if needed
            if is_confirming_delete:
                self._render_delete_confirmation_dialog(room_id, room_name)
            elif is_confirming_clear:
                self._render_clear_confirmation_dialog(room_id, room_name)
            else:
                # Show normal action buttons
                self._render_room_action_buttons(room_id, room_name)

    def _render_room_action_buttons(self, room_id: str, room_name: str) -> None:
        """Render the action buttons for a room.

        Args:
            room_id (str): Room ID.
            room_name (str): Room name.
        """
        # Action buttons
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            if st.button(
                "Enter Chat", key=f"enter_{room_id}", use_container_width=True
            ):
                self._enter_chatroom(room_id)

        with col2:
            if st.button("📊 Stats", key=f"stats_{room_id}", use_container_width=True):
                self._show_room_stats(room_id, room_name)

        with col3:
            if st.button(
                "🧹 Clear",
                key=f"clear_{room_id}",
                use_container_width=True,
                help="Clear chat history (preserves system messages)",
            ):
                # Set clear confirmation mode
                self.session_manager.set_state_value(f"confirm_clear_{room_id}", True)
                st.rerun()

        with col4:
            if st.button(
                "🗑️ Delete",
                key=f"delete_{room_id}",
                use_container_width=True,
                type="secondary",
            ):
                # Set delete confirmation mode
                self.session_manager.set_state_value(f"confirm_delete_{room_id}", True)
                st.rerun()

    def _render_delete_confirmation_dialog(self, room_id: str, room_name: str) -> None:
        """Render the delete confirmation dialog.

        Args:
            room_id (str): Room ID.
            room_name (str): Room name.
        """
        st.error("⚠️ **CONFIRM DELETION**")
        st.warning(f"Are you sure you want to permanently delete '{room_name}'?")
        st.info(
            "This will delete the room and ALL its messages. This cannot be undone!"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🗑️ YES, DELETE PERMANENTLY",
                key=f"confirm_yes_{room_id}",
                type="primary",
                use_container_width=True,
            ):
                # Clear confirmation state and delete
                self.session_manager.set_state_value(f"confirm_delete_{room_id}", False)
                self._delete_room(room_id, room_name)

        with col2:
            if st.button(
                "❌ Cancel", key=f"confirm_no_{room_id}", use_container_width=True
            ):
                # Clear confirmation state
                self.session_manager.set_state_value(f"confirm_delete_{room_id}", False)
                st.rerun()

    def _render_clear_confirmation_dialog(self, room_id: str, room_name: str) -> None:
        """Render the clear messages confirmation dialog.

        Args:
            room_id (str): Room ID.
            room_name (str): Room name.
        """
        st.warning("⚠️ **CONFIRM CLEAR CHAT HISTORY**")
        st.info(
            f"Clear chat history from '{room_name}'? User and AI messages will be deleted, but system messages will be preserved."
        )
        st.caption("💡 System messages (like initial prompts) will remain intact.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🧹 YES, CLEAR CHAT HISTORY",
                key=f"clear_yes_{room_id}",
                type="primary",
                use_container_width=True,
            ):
                # Clear confirmation state and clear messages
                self.session_manager.set_state_value(f"confirm_clear_{room_id}", False)
                self._clear_room_messages(room_id)

        with col2:
            if st.button(
                "❌ Cancel", key=f"clear_no_{room_id}", use_container_width=True
            ):
                # Clear confirmation state
                self.session_manager.set_state_value(f"confirm_clear_{room_id}", False)
                st.rerun()

    def _render_create_room_form(self) -> None:
        """Render the create new chatroom form."""
        st.markdown("## ✨ Create New Chat Room")

        with st.form(key="create_room_form", clear_on_submit=True):
            # Room name input
            room_name = st.text_input(
                "Room Name",
                placeholder="e.g., Work Project, Study Session, Creative Ideas...",
                help="Give your chat room a descriptive name",
            )

            # Model selection
            st.markdown("**AI Model Selection**")

            selected_model = st.selectbox(
                "Select Model",
                OpenRouterClient.get_available_models(),
                help="Choose the AI model for this chat room",
            )

            # Model info
            self._show_model_info(selected_model)

            # System prompt
            system_prompt = st.text_area(
                "System Prompt (Optional)",
                value=DEFAULT_SYSTEM_PROMPT,
                height=100,
                help="Customize the AI's behavior and personality for this chat",
            )

            # Submit button
            submitted = st.form_submit_button(
                "🚀 Create Chat Room", use_container_width=True
            )

            if submitted:
                self._handle_room_creation(room_name, selected_model, system_prompt)

    def _show_model_info(self, model_name: str) -> None:
        """Show information about the selected model.

        Args:
            model_name (str): Name of the selected model.
        """
        if "/" in model_name:
            provider, model_info = model_name.split("/", 1)

            info_text = f"**Provider:** {provider.title()}"

            # Add special badges
            badges = []
            if ":free" in model_name:
                badges.append("🆓 Free")
            if "vision" in model_name.lower():
                badges.append("🖼️ Vision")
            if "coder" in model_name.lower() or "code" in model_name.lower():
                badges.append("💻 Coding")

            if badges:
                info_text += f" | {' | '.join(badges)}"

            print("info text", info_text)

            st.info(info_text)

    def _handle_room_creation(
        self, room_name: str, model_name: str, system_prompt: str
    ) -> None:
        """Handle the creation of a new chat room.

        Args:
            room_name (str): Name of the new room.
            model_name (str): Selected AI model.
            system_prompt (str): System prompt for the room.
        """
        if not room_name or not room_name.strip():
            st.error("Please enter a room name")
            return

        try:
            # Create the room
            room_id = self.chat_manager.create_chat_room(
                room_name.strip(), system_prompt
            )

            # Store the selected model for this room
            self.session_manager.set_state_value(f"room_model_{room_id}", model_name)

            # Store the newly created room ID for highlighting
            self.session_manager.set_state_value("newly_created_room", room_id)

            # Show success feedback
            st.success(f"✅ Created '{room_name}' successfully!")
            st.balloons()

            # Show info about what to do next
            st.info(
                "💡 Your new chat room has been created! Refreshing the room list..."
            )

            # Small delay to show the success message, then refresh
            import time

            time.sleep(1)

            # Refresh the page to update the room list
            st.rerun()

        except ValueError as e:
            st.error(f"❌ Error creating room: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            # Show debug info for unexpected errors
            with st.expander("Debug Information", expanded=False):
                import traceback

                st.code(traceback.format_exc())

    def _enter_chatroom(self, room_id: str) -> None:
        """Enter a specific chatroom by setting session state and rerunning.

        Args:
            room_id (str): ID of the room to enter.
        """
        try:
            # Verify room exists before entering
            room_info = self.chat_manager.get_chat_room_info(room_id)
            if not room_info:
                st.error("❌ Chat room not found! Please refresh the page.")
                return

            # Set active room in session state
            self.session_manager.active_room = room_id

            # Clear newly created room flag if entering that room
            newly_created_room = self.session_manager.get_state_value(
                "newly_created_room"
            )
            if newly_created_room == room_id:
                self.session_manager.set_state_value("newly_created_room", None)

            # Show brief success message
            st.success(f"✅ Entering {room_info[0]}...")

            # Trigger rerun to switch to chatroom view
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error entering chat room: {str(e)}")
            st.error("Please try refreshing the page or contact support.")

    def _show_room_stats(self, room_id: str, room_name: str) -> None:
        """Show statistics for a specific room.

        Args:
            room_id (str): Room ID.
            room_name (str): Room name.
        """
        try:
            # Get room messages
            db_messages = self.chat_manager.get_room_messages(room_id)

            # Calculate stats
            total_messages = len(db_messages)
            user_messages = len([m for m in db_messages if m[0] == "human"])
            ai_messages = len([m for m in db_messages if m[0] == "assistant"])

            # Show in a modal-like expander
            with st.expander(f"📊 Statistics for '{room_name}'", expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Messages", total_messages)

                with col2:
                    st.metric("Your Messages", user_messages)

                with col3:
                    st.metric("AI Messages", ai_messages)

                # Room model info
                room_model = self.session_manager.get_state_value(
                    f"room_model_{room_id}"
                )
                if room_model:
                    st.info(f"🤖 Model: {room_model}")

        except Exception as e:
            st.error(f"Failed to load statistics: {str(e)}")

    def _clear_room_messages(self, room_id: str) -> None:
        """Clear chat history for a specific room (preserves system messages).

        Args:
            room_id (str): Room ID to clear chat history for.
        """
        try:
            # Get room info first
            room_info = self.chat_manager.get_chat_room_info(room_id)
            room_name = room_info[0] if room_info else "Unknown Room"

            # Clear chat history (preserves system messages)
            deleted_count = self.chat_manager.clear_room_chat_history(room_id)

            # Show success message
            if deleted_count > 0:
                st.success(
                    f"✅ Cleared {deleted_count} chat messages from '{room_name}' (system messages preserved)"
                )
            else:
                st.info(
                    f"ℹ️ No chat messages to clear in '{room_name}' (system messages preserved)"
                )

            # Brief delay to show the message, then refresh to update message counts
            import time

            time.sleep(0.5)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Failed to clear chat history: {str(e)}")

    def _delete_room(self, room_id: str, room_name: str) -> None:
        """Delete a chat room and all its messages.

        Args:
            room_id (str): Room ID to delete.
            room_name (str): Room name to delete.
        """
        # Show deletion in progress
        with st.spinner(f"Deleting '{room_name}'..."):
            try:
                # Attempt to delete the room
                success = self.chat_manager.delete_chat_room(room_id)

                if success:
                    # Clear any session state related to this room
                    room_model_key = f"room_model_{room_id}"
                    confirm_key = f"confirm_delete_{room_id}"
                    clear_confirm_key = f"confirm_clear_{room_id}"

                    # Clear all related session state
                    self.session_manager.set_state_value(room_model_key, None)
                    self.session_manager.set_state_value(confirm_key, False)
                    self.session_manager.set_state_value(clear_confirm_key, False)

                    # If this was the active room, clear it
                    if self.session_manager.active_room == room_id:
                        self.session_manager.active_room = None
                        # Also clear the current page if we're in that room
                        if (
                            self.session_manager.get_state_value("current_page")
                            == "chatroom"
                        ):
                            self.session_manager.set_state_value(
                                "current_page", "homepage"
                            )

                    # Show success message
                    st.success(f"✅ Successfully deleted '{room_name}'!")
                    st.balloons()

                    # Short delay then refresh
                    import time

                    time.sleep(0.5)
                    st.rerun()

                else:
                    st.error(f"❌ Room '{room_name}' not found or already deleted")

            except ValueError as e:
                st.error(f"❌ Invalid room: {str(e)}")
            except RuntimeError as e:
                st.error(f"❌ Failed to delete room: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                # Show more details in debug mode
                with st.expander("Debug Info", expanded=False):
                    st.code(f"Error type: {type(e).__name__}")
                    st.code(f"Error message: {str(e)}")
                    import traceback

                    st.code(traceback.format_exc())

    def render_footer(self) -> None:
        """Render the homepage footer."""
        st.divider()
        st.caption("Built with ❤️ using Streamlit & OpenRouter AI")
