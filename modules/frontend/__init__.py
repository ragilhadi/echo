"""Frontend module for the chatbot application.

This module provides a complete Streamlit-based user interface using Streamlit's
native multipage structure following the MVC pattern with proper separation of
concerns between managers, components, and pages.

Structure:
    - app.py: Homepage (entrypoint)
    - pages/chat.py: Chat room page
    - managers/: Business logic and state management
    - components/: Reusable UI components

References:
    Streamlit Multipage Apps: https://docs.streamlit.io/develop/concepts/multipage-apps/pages-directory
"""

from modules.frontend.managers import SessionManager, ChatManager, MessageManager
from modules.frontend.components import (
    MessageDisplayComponent,
    SidebarComponent,
    ChatInterfaceComponent,
)

__all__ = [
    "SessionManager",
    "ChatManager",
    "MessageManager",
    "MessageDisplayComponent",
    "SidebarComponent",
    "ChatInterfaceComponent",
]
