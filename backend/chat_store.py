import sqlite3
import json
import os

DB_PATH = "data/chats.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                chat_name TEXT,
                messages TEXT
            )
        """)

def load_all_chats():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT chat_id, chat_name, messages FROM chats")
        # Returns {chat_id: {"chat_name": name, "messages": [...]}}
        return {row[0]: {"chat_name": row[1], "messages": json.loads(row[2])} for row in cursor.fetchall()}

def save_chat(chat_id, chat_name, messages):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO chats (chat_id, chat_name, messages) VALUES (?, ?, ?)",
            (chat_id, chat_name, json.dumps(messages))
        )

def delete_chat_record(chat_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))