import json
import os
import sqlite3
import pandas as pd
import calmap
from tkinter import filedialog
from tkinter import Tk
import datetime

def isValid(message: dict):
    if "content" not in message:
        return False

    if message["content"].startswith("Reacted ") and message["content"].endswith(" to your message "):
        return False

    if message["content"] == "Liked a message":
        return False

    return True


# Liked a message
# Reacted \u00f0\u009f\u0098\u00ad to your message

cur = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES).cursor()
cur.execute("CREATE TABLE messages("
            "name TEXT PRIMARY KEY,"
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
            if isValid(message):
                cur.execute("INSERT INTO messages(?, ?, ?)", (
                    folder_name,
                    datetime.date.fromtimestamp(message["timestamp_ms"] / 1000),
                    1
                ))