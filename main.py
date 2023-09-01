import json
import os
import sqlite3
import pandas as pd
import calmap
from tkinter import filedialog
from tkinter import Tk
import datetime
import matplotlib.pyplot


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
        # if len(conversation['participants']) > 2:
        #     continue

        for message in conversation["messages"]:
            if is_valid(message):
                cur.execute("INSERT INTO messages VALUES(?, ?, ?)", (
                    folder_name,
                    datetime.date.fromtimestamp(message["timestamp_ms"] / 1000),
                    1
                ))

for name in cur.execute("SELECT DISTINCT name FROM messages").fetchall():
    print("Working on ", name)
    min_date, max_date = cur.execute("SELECT MIN(date), MAX(date) from messages WHERE name = ? GROUP BY name", (name[0],)).fetchall()[0]
    min_date = datetime.date.fromisoformat(min_date)
    max_date = datetime.date.fromisoformat(max_date)
    difference_days = (max_date - min_date).days
    if difference_days == 0: continue
    all_days = pd.date_range(min_date, periods=difference_days + 1, freq="D")

    current_conversation = dict()
    for entry in cur.execute("SELECT date, SUM(count) FROM messages WHERE name = ? GROUP BY name, date", (name[0],)):
        current_conversation[entry[0]] = entry[1]
    for i in range(0, difference_days):
        calculated_date = min_date + datetime.timedelta(days=i)
        if calculated_date in current_conversation:
            pass
        else:
            current_conversation[calculated_date] = 0

    events = pd.Series(current_conversation,
                       index=all_days)
    fig, axes = calmap.calendarplot(events, fillcolor="gray", fig_suptitle=name[0], fig_kws=dict(figsize=(15, 12)))
    fig.colorbar(axes[0].get_children()[1], ax=axes.ravel().tolist())
    fig.savefig(f"./images/{name[0]}.png")
    matplotlib.pyplot.close()
