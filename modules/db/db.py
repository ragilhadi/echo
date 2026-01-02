"""Chat database implementation.

Authors:
    Ragil Prasetyo (ragilhprasetyo@gmail.com)

References:
    None
"""

import sqlite3
from datetime import datetime
import uuid
import os


class ChatDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv("DB_PATH", "chat_history.db")

        # Ensure the directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_tables()

    def _initialize_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_rooms (
                room_id TEXT PRIMARY KEY,
                room_name TEXT,
                created_at TIMESTAMP
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT,
                role TEXT,
                content TEXT,
                llm TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES chat_rooms (room_id)
            )
        """
        )
        self.conn.commit()

    def add_chat_room(self, room_name):
        room_id = str(uuid.uuid4())
        timestamp = datetime.now()
        self.cursor.execute(
            """
            INSERT INTO chat_rooms (room_id, room_name, created_at)
            VALUES (?, ?, ?)
            """,
            (room_id, room_name, timestamp),
        )
        self.conn.commit()

        return room_id

    def get_chat_room(self, room_id):
        self.cursor.execute(
            """
            SELECT room_name, created_at FROM chat_rooms
            WHERE room_id = ?
            """,
            (room_id,),
        )
        return self.cursor.fetchone()

    def get_all_chat_rooms(self):
        self.cursor.execute(
            """
            SELECT room_id, room_name, created_at FROM chat_rooms
            ORDER BY created_at DESC
            """
        )
        return self.cursor.fetchall()

    def add_message(self, room_id, role, content, llm):
        self.cursor.execute(
            """
            INSERT INTO messages (room_id, role, content, llm, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (room_id, role, content, llm, datetime.utcnow()),
        )
        self.conn.commit()

    def get_messages_by_room(self, room_id):
        self.cursor.execute(
            """
            SELECT role, content, llm, timestamp FROM messages
            WHERE room_id = ?
            ORDER BY timestamp ASC
            """,
            (room_id,),
        )
        return self.cursor.fetchall()

    def delete_chat_room(self, room_id):
        """Delete a chat room and all its messages.

        Args:
            room_id (str): The ID of the room to delete.

        Returns:
            bool: True if room was deleted, False if room didn't exist.
        """
        # First check if room exists
        self.cursor.execute(
            """
            SELECT room_id FROM chat_rooms WHERE room_id = ?
            """,
            (room_id,),
        )
        if not self.cursor.fetchone():
            return False

        # Delete all messages for this room first (foreign key constraint)
        self.cursor.execute(
            """
            DELETE FROM messages WHERE room_id = ?
            """,
            (room_id,),
        )

        # Then delete the room itself
        self.cursor.execute(
            """
            DELETE FROM chat_rooms WHERE room_id = ?
            """,
            (room_id,),
        )

        self.conn.commit()
        return True

    def delete_messages_by_room(self, room_id):
        """Delete all messages in a specific room.

        Args:
            room_id (str): The ID of the room whose messages to delete.

        Returns:
            int: Number of messages deleted.
        """
        self.cursor.execute(
            """
            DELETE FROM messages WHERE room_id = ?
            """,
            (room_id,),
        )
        deleted_count = self.cursor.rowcount
        self.conn.commit()
        return deleted_count

    def clear_room_chat_history(self, room_id):
        """Clear chat history (user and assistant messages) but preserve system messages.

        Args:
            room_id (str): The ID of the room whose chat history to clear.

        Returns:
            int: Number of messages deleted.
        """
        self.cursor.execute(
            """
            DELETE FROM messages 
            WHERE room_id = ? AND role IN ('human', 'assistant')
            """,
            (room_id,),
        )
        deleted_count = self.cursor.rowcount
        self.conn.commit()
        return deleted_count

    def count_messages_by_room(self, room_id):
        """Count messages in a specific room.

        Args:
            room_id (str): The ID of the room to count messages for.

        Returns:
            int: Number of messages in the room.
        """
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM messages WHERE room_id = ?
            """,
            (room_id,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def close(self):
        self.conn.close()
