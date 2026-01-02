"""Main chat interface UI component.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    Streamlit Chat Input: https://docs.streamlit.io/library/api-reference/chat/st.chat_input
"""

import streamlit as st
from typing import List, Dict, Optional
from modules.frontend.managers import SessionManager, ChatManager, MessageManager
from modules.frontend.components.message_display import MessageDisplayComponent
from modules.client.exception import APIConnectionError, InvalidModelError
from constants import ChatRole


class ChatInterfaceComponent:
    """Handles the main chat interface (Single Responsibility Principle).

    This class manages the main chat area including message display,
    user input handling, and AI response generation with ChatGPT-like behavior.
    """

    def __init__(
        self,
        session_manager: SessionManager,
        chat_manager: ChatManager,
        message_manager: MessageManager,
        message_display: MessageDisplayComponent,
    ):
        """Initialize the chat interface component.

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

        # Inject ChatGPT-like interface styles
        self._inject_interface_styles()

    def _inject_interface_styles(self) -> None:
        """Inject CSS for ChatGPT-like interface styling."""
        css_styles = """
        <style>
        /* Main chat container */
        .main .block-container {
            max-width: 100% !important;
            padding-top: 2rem !important;
            padding-bottom: 6rem !important;
        }
        
        /* Chat input container - make it sticky */
        .stChatInput {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            background: white !important;
            border-top: 1px solid #e5e7eb !important;
            padding: 1rem !important;
            z-index: 999 !important;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1) !important;
        }
        
        /* Chat input field styling */
        .stChatInput > div {
            max-width: 900px !important;
            margin: 0 auto !important;
        }
        
        /* Ensure content doesn't go behind fixed input */
        .main-chat-content {
            margin-bottom: 120px !important;
        }
        
        /* Smooth scrolling */
        html {
            scroll-behavior: smooth !important;
        }
        
        /* Message container max width */
        .chat-message-container {
            max-width: 900px !important;
            margin: 0 auto !important;
        }
        
        /* Header styling */
        .chat-header {
            position: sticky !important;
            top: 0 !important;
            background: white !important;
            z-index: 100 !important;
            border-bottom: 1px solid #e5e7eb !important;
            padding: 1rem 0 !important;
            margin-bottom: 1rem !important;
        }
        
        /* Sidebar width adjustment */
        .css-1d391kg {
            width: 21rem !important;
        }
        
        /* Main content area adjustment */
        .css-18e3th9 {
            padding-left: 22rem !important;
        }
        
        /* Chat messages spacing */
        .stChatMessage {
            margin-bottom: 1.5rem !important;
            max-width: 100% !important;
        }
        
        /* Welcome message styling */
        .welcome-message {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 50vh !important;
        }
        
        /* Loading spinner */
        .stSpinner {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        
        /* Auto-scroll to bottom button */
        .scroll-to-bottom {
            position: fixed !important;
            bottom: 140px !important;
            right: 30px !important;
            z-index: 998 !important;
            background: #f3f4f6 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        }
        
        .scroll-to-bottom:hover {
            background: #e5e7eb !important;
        }
        </style>
        """
        st.markdown(css_styles, unsafe_allow_html=True)

    def render(self) -> None:
        """Render the main chat interface with ChatGPT-like behavior."""
        if not self.session_manager.has_active_room():
            self._render_no_room_selected()
            return

        # Get current room info
        room_info = self.chat_manager.get_chat_room_info(
            self.session_manager.active_room
        )
        if not room_info:
            self._render_room_not_found()
            return

        room_name, created_at = room_info

        # Render room header (sticky)
        self._render_room_header(room_name)

        # Create the main chat container with proper height
        self._render_chat_container()

    def _render_chat_container(self) -> None:
        """Render the main chat container with proper scrolling behavior."""
        # Create a container for the chat messages
        st.markdown('<div class="main-chat-content">', unsafe_allow_html=True)

        chat_container = st.container()

        with chat_container:
            # Add message container wrapper
            st.markdown('<div class="chat-message-container">', unsafe_allow_html=True)

            # Render message history
            self._render_message_history()

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Render the chat input at the bottom (sticky)
        self._render_chat_input()

        # Add auto-scroll functionality
        self._inject_auto_scroll_functionality()

    def _render_no_room_selected(self) -> None:
        """Render message when no room is selected."""
        st.markdown(
            """
            <div class="welcome-message">
                <div style='text-align: center; color: #6b7280; max-width: 600px;'>
                    <div style='font-size: 3rem; margin-bottom: 1rem;'>💬</div>
                    <h2 style='color: #374151; margin-bottom: 1rem;'>Welcome to Chat Assistant</h2>
                    <p style='font-size: 1.1rem; margin-bottom: 2rem; line-height: 1.6;'>
                        Get started by creating a new chat room or selecting an existing one from the sidebar.
                    </p>
                    <div style='display: flex; gap: 2rem; justify-content: center; margin-top: 2rem;'>
                        <div style='text-align: center;'>
                            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>🚀</div>
                            <p style='font-size: 0.9rem; color: #9ca3af;'>Choose an AI model</p>
                        </div>
                        <div style='text-align: center;'>
                            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>✨</div>
                            <p style='font-size: 0.9rem; color: #9ca3af;'>Create a chat room</p>
                        </div>
                        <div style='text-align: center;'>
                            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>💡</div>
                            <p style='font-size: 0.9rem; color: #9ca3af;'>Start chatting</p>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _render_room_not_found(self) -> None:
        """Render message when selected room is not found."""
        st.error("Selected chat room not found. Please select another room.")
        self.session_manager.active_room = None

    def _render_room_header(self, room_name: str) -> None:
        """Render a compact chat room header.

        Args:
            room_name (str): Name of the current room.
        """
        st.markdown(
            f"""
            <div class="chat-header">
                <div style='max-width: 900px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 1rem;'>
                    <h3 style='margin: 0; color: #374151; font-weight: 600;'>{room_name}</h3>
                    <div style='display: flex; gap: 0.5rem; align-items: center;'>
                        <span style='font-size: 0.8rem; color: #6b7280;'>
                            {self._get_message_count()} messages
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _get_message_count(self) -> int:
        """Get the number of messages in the current room."""
        try:
            db_messages = self.chat_manager.get_room_messages(
                self.session_manager.active_room
            )
            return self.message_display.count_visible_messages(db_messages)
        except Exception:
            return 0

    def _render_message_history(self) -> None:
        """Render the message history with proper spacing and layout."""
        try:
            # Get messages from database
            db_messages = self.chat_manager.get_room_messages(
                self.session_manager.active_room
            )

            if not db_messages:
                # Show welcome message for empty rooms
                room_info = self.chat_manager.get_chat_room_info(
                    self.session_manager.active_room
                )
                if room_info:
                    room_name, _ = room_info
                    self._render_welcome_message(room_name)
                return

            # Render messages using the display component
            self.message_display.render_messages(db_messages)

        except Exception as e:
            st.error(f"Failed to load message history: {str(e)}")

    def _render_welcome_message(self, room_name: str) -> None:
        """Render a welcome message for empty chat rooms.

        Args:
            room_name (str): Name of the chat room.
        """
        st.markdown(
            f"""
            <div style='text-align: center; padding: 60px 20px; color: #6b7280;'>
                <div style='font-size: 2rem; margin-bottom: 1rem;'>👋</div>
                <h3 style='color: #374151; margin-bottom: 1rem; font-weight: 600;'>Welcome to {room_name}!</h3>
                <p style='margin-bottom: 1rem; font-size: 1.1rem;'>Start a conversation by typing a message below.</p>
                <p style='font-size: 0.9em; color: #9ca3af;'>
                    💡 Your conversation history will appear here as you chat with the AI.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _render_chat_input(self) -> None:
        """Render the chat input with sticky positioning."""
        # Chat input with ChatGPT-like styling
        user_input = st.chat_input(
            placeholder="Message ChatBot... (Press Enter to send)",
            key="main_chat_input",
        )

        if user_input:
            self._process_user_message(user_input)

    def _process_user_message(self, user_message: str) -> None:
        """Process a user message and generate AI response.

        Args:
            user_message (str): The user's message.
        """
        if not user_message.strip():
            st.warning("Please enter a message")
            return

        if not self.session_manager.has_chat_model():
            st.error("🤖 No AI model configured. Please select a model in the sidebar.")
            return

        try:
            # Add user message to database first
            self.chat_manager.add_user_message(
                self.session_manager.active_room, user_message
            )

            # Rerun to show user message immediately, then generate AI response
            st.rerun()

        except Exception as e:
            st.error(f"Error processing message: {str(e)}")

    def _inject_auto_scroll_functionality(self) -> None:
        """Inject JavaScript for auto-scrolling and scroll-to-bottom functionality."""
        scroll_script = """
        <script>
        // Auto-scroll to bottom function
        function scrollToBottom() {
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        }
        
        // Check if user is near bottom
        function isNearBottom() {
            return (window.innerHeight + window.scrollY) >= document.body.offsetHeight - 200;
        }
        
        // Show/hide scroll to bottom button
        function toggleScrollButton() {
            const button = document.getElementById('scroll-to-bottom-btn');
            if (button) {
                if (isNearBottom()) {
                    button.style.display = 'none';
                } else {
                    button.style.display = 'flex';
                }
            }
        }
        
        // Create scroll to bottom button
        function createScrollButton() {
            if (!document.getElementById('scroll-to-bottom-btn')) {
                const button = document.createElement('div');
                button.id = 'scroll-to-bottom-btn';
                button.className = 'scroll-to-bottom';
                button.innerHTML = '↓';
                button.onclick = scrollToBottom;
                button.style.display = 'none';
                document.body.appendChild(button);
            }
        }
        
        // Auto-scroll observer for new messages
        const observer = new MutationObserver(function(mutations) {
            let shouldScroll = false;
            const wasNearBottom = isNearBottom();
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if new chat messages were added
                    for (let node of mutation.addedNodes) {
                        if (node.nodeType === 1 && 
                            (node.querySelector('[data-testid="chat-message"]') || 
                             node.getAttribute && node.getAttribute('data-testid') === 'chat-message')) {
                            shouldScroll = true;
                            break;
                        }
                    }
                }
            });
            
            // Auto-scroll if user was near bottom when new message arrived
            if (shouldScroll && wasNearBottom) {
                setTimeout(scrollToBottom, 100);
            }
            
            // Update scroll button visibility
            setTimeout(toggleScrollButton, 200);
        });
        
        // Start observing
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Create scroll button and initial scroll
        setTimeout(() => {
            createScrollButton();
            scrollToBottom();
        }, 500);
        
        // Update scroll button on scroll
        window.addEventListener('scroll', toggleScrollButton);
        </script>
        """

        st.markdown(scroll_script, unsafe_allow_html=True)

    def render_chat_stats(self) -> None:
        """Render chat statistics in an expandable section."""
        if not self.session_manager.has_active_room():
            return

        with st.expander("📊 Chat Statistics", expanded=False):
            try:
                # Get room messages
                db_messages = self.chat_manager.get_room_messages(
                    self.session_manager.active_room
                )

                # Calculate stats
                total_messages = len(db_messages)
                visible_messages = self.message_display.count_visible_messages(
                    db_messages
                )
                user_messages = len([m for m in db_messages if m[0] == ChatRole.HUMAN])
                ai_messages = len([m for m in db_messages if m[0] == ChatRole.AI])

                # Display stats in a clean layout
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("💬 Total", total_messages)
                    st.metric("👤 User", user_messages)

                with col2:
                    st.metric("👁️ Visible", visible_messages)
                    st.metric("🤖 AI", ai_messages)

                # Model info
                if self.session_manager.has_chat_model():
                    st.markdown("**Current Model:**")
                    model_info = self.chat_manager.get_model_info(
                        self.session_manager.chat_model
                    )
                    for key, value in model_info.items():
                        st.text(f"{key.title()}: {value}")

            except Exception as e:
                st.error(f"Failed to load statistics: {str(e)}")

    def render_debug_info(self) -> None:
        """Render debug information (for development)."""
        if st.checkbox("🐛 Debug Mode", value=False):
            with st.expander("Debug Information", expanded=True):
                st.markdown("**Session State:**")
                debug_info = {
                    "active_room": self.session_manager.active_room,
                    "has_chat_model": self.session_manager.has_chat_model(),
                    "history_token": self.session_manager.history_token,
                }
                st.json(debug_info)

                if self.session_manager.has_active_room():
                    st.markdown("**Recent Messages:**")
                    try:
                        db_messages = self.chat_manager.get_room_messages(
                            self.session_manager.active_room
                        )
                        for i, (role, content, llm, timestamp) in enumerate(
                            db_messages[-3:]
                        ):  # Last 3 messages
                            st.text(f"{i+1}. [{role}] {content[:100]}...")
                    except Exception as e:
                        st.error(f"Failed to load debug info: {str(e)}")

    def export_conversation(self) -> None:
        """Export the current conversation."""
        if not self.session_manager.has_active_room():
            return

        if st.button("📥 Export Chat", help="Download conversation as text file"):
            try:
                db_messages = self.chat_manager.get_room_messages(
                    self.session_manager.active_room
                )
                room_info = self.chat_manager.get_chat_room_info(
                    self.session_manager.active_room
                )
                room_name = room_info[0] if room_info else "Unknown"

                # Create formatted export
                export_text = f"Chat Export: {room_name}\n"
                export_text += "=" * 50 + "\n\n"

                for role, content, llm, timestamp in db_messages:
                    if role != ChatRole.SYSTEM:
                        speaker = "You" if role == ChatRole.HUMAN else f"AI ({llm})"
                        export_text += f"{speaker}:\n{content}\n\n"

                export_text += f"\nExported on: {timestamp}\n"

                st.download_button(
                    "💾 Download",
                    export_text,
                    file_name=f"chat_{room_name.replace(' ', '_').lower()}_{self.session_manager.active_room[:8]}.txt",
                    mime="text/plain",
                    help="Download the conversation as a text file",
                )

            except Exception as e:
                st.error(f"Failed to export conversation: {str(e)}")

    def render_quick_actions(self) -> None:
        """Render quick action buttons."""
        if not self.session_manager.has_active_room():
            return

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🔄 Refresh", help="Refresh the chat", use_container_width=True
            ):
                st.rerun()

        with col2:
            if st.button(
                "⬇️ Scroll", help="Scroll to latest message", use_container_width=True
            ):
                st.markdown(
                    "<script>setTimeout(() => window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'}), 100);</script>",
                    unsafe_allow_html=True,
                )
