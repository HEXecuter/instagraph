import json
import os
import sqlite3
import pandas as pd
import calmap
from tkinter import filedialog
from tkinter import Tk
import datetime


def is_valid(message: dict):
    if "content" not in message:
        return False

    if message["content"].startswith("Reacted ") and message["content"].endswith(" to your message "):
        return False

    if message["content"] == "Liked a message":
        return False

    return True


cur = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES).cursor()
cur.execute("CREATE TABLE messages("
            "name TEXT,"
            "date DATE,"
            "count INTEGER)"
            )

print("SELECT YOUR inbox FOLDER: ")
root = Tk()
root.withdraw()
folder_selected = filedialog.askdirectory()

if not folder_selected.endswith("/inbox"):
    raise ValueError(f"File path supplied does not appear to be the inbox folder\nValue supplied was {folder_selected}")

for folder_name in os.listdir(folder_selected):
    message_filepath = os.path.join(folder_selected, folder_name, "message_1.json")
    with open(message_filepath, 'r') as json_file:
        conversation = json.load(json_file)

        # Don't want group chats
        if len(conversation['participants']) > 2:
            continue

        for message in conversation["messages"]:
            if is_valid(message):
                cur.execute("INSERT INTO messages VALUES(?, ?, ?)", (
                    folder_name,
                    datetime.date.fromtimestamp(message["timestamp_ms"] / 1000),
                    1
                ))

for aggregate_conversations in cur.execute("SELECT name, date, SUM(count) FROM messages GROUP BY name, date").fetchall():
    min_date, max_date = cur.execute("SELECT MIN(date), MAX(date) from messages WHERE name = ? GROUP BY name", (aggregate_conversations[0],)).fetchall()[0]
