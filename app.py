"""Echo - AI Chat Assistant Application

This is the main Streamlit application that provides a chatbot interface.
Users can create chat rooms and interact with AI models via OpenRouter in a single-page application.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    Streamlit Chat Elements: https://docs.streamlit.io/develop/api-reference/chat
"""

import streamlit as st
from modules.frontend.managers import SessionManager, ChatManager, MessageManager
from modules.frontend.components.homepage import HomepageComponent
from modules.frontend.components.chatroom_page import ChatroomPageComponent
from modules.frontend.components.message_display import MessageDisplayComponent

# Configure the application
st.set_page_config(
    page_title="Echo - AI Chat Assistant",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main application function handling both homepage and chatroom views."""
    # Initialize managers
    session_manager = SessionManager()
    chat_manager = ChatManager(session_manager.db)
    message_manager = MessageManager()
    message_display = MessageDisplayComponent()

    # Initialize components
    homepage = HomepageComponent(session_manager, chat_manager)
    chatroom_page = ChatroomPageComponent(
        session_manager, chat_manager, message_manager, message_display
    )

    # Check if we have an active room (chatroom view) or show homepage
    active_room = session_manager.active_room

    if active_room:
        # Chatroom view
        try:
            room_name = chat_manager.get_room_name(active_room)
            if room_name:
                st.title(f"Chat: {room_name}")
                st.divider()

                # Render the chatroom interface
                chatroom_page.render()
            else:
                # Room doesn't exist anymore, clear active room and show homepage
                session_manager.active_room = None
                st.rerun()
        except Exception as e:
            st.error(f"Error loading chat room: {str(e)}")
            session_manager.active_room = None
            st.rerun()
    else:
        # Homepage view
        homepage.render()
        homepage.render_footer()


if __name__ == "__main__":
    main()
