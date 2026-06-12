import os
import shutil
import time
import tkinter as tk
import json

from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 分类规则
file_types = {

    "Images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp"
    ],

    "Videos": [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov"
    ],

    "Documents": [
        ".pdf",
        ".txt",
        ".doc",
        ".docx",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx"
    ],

    "Code": [
        ".py",
        ".c",
        ".cpp",
        ".java"
    ],

    "Archives": [
        ".zip",
        ".rar",
        ".7z"
    ]
}

observer = None

log_history = []

CONFIG_FILE = "config.json"

files_moved = 0

current_folder = None

category_count = {
    "Images": 0,
    "Videos": 0,
    "Documents": 0,
    "Code": 0,
    "Archives": 0,
    "Others": 0
}

import subprocess
import os

def open_config_file():

    if os.path.exists(CONFIG_FILE):
        os.startfile(CONFIG_FILE)
    else:
        print("config.json not found")

def save_config(folder_path):

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:

        json.dump(
            {
                "folder_path": folder_path,
                "rules": rules
            },
            file,
            indent=4
        )

def load_config():

    if not os.path.exists(CONFIG_FILE):
        return None, {}

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("folder_path"), data.get("rules", {})

def get_unique_path(folder, filename):

    name, ext = os.path.splitext(filename)

    new_path = os.path.join(folder, filename)

    counter = 1

    while os.path.exists(new_path):

        new_filename = f"{name}_{counter}{ext}"

        new_path = os.path.join(folder, new_filename)

        counter += 1

    return new_path

# 文件整理
def organize_file(file_path, folder_path):

    global files_moved
    global counter_label
    global stats_label
    global category_count

    global log_label
    global rules

    if os.path.isdir(file_path):
        return

    file_name = os.path.basename(file_path)

    _, extension = os.path.splitext(file_name)

    extension = extension.lower()

    moved = False

    category = "Others"

    for ext, cat in rules.items():
        if extension == ext:
            category = cat
            break

    category_folder = os.path.join(folder_path, category)
    os.makedirs(category_folder, exist_ok=True)

    target_path = get_unique_path(
        category_folder,
        file_name
    )

    try:
        shutil.move(file_path, target_path)

    except PermissionError:
        print(f"File in use: {file_name}")
        return

    message = f"Moved: {file_name} -> {category}"
    print(message)

    log_history.append(message)

    category_count[category] = category_count.get(category, 0) + 1

    stats_label.config(
        text="\n".join(
            f"{name}: {count}"
            for name, count in category_count.items()
        )
    )

    files_moved += 1

    counter_label.config(
        text=f"Files moved: {files_moved}"
    )

    log_label.config(
        text="\n".join(log_history[-5:])
    )

    # Others
    if not moved:

        other_folder = os.path.join(folder_path, "Others")

        os.makedirs(other_folder, exist_ok=True)

        target_path = get_unique_path(
            other_folder,
            file_name
        )

        try:
            shutil.move(file_path, target_path)

        except PermissionError:
            print(f"File in use: {file_name}")
            return
        
        files_moved += 1

        counter_label.config(
            text=f"Files moved: {files_moved}"
        )
        
        print(f"Moved: {file_name} -> Others")

        log_label.config(
            text=f"Moved: {file_name} -> Others"
        )
# 监听类
class MyHandler(FileSystemEventHandler):

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def on_created(self, event):

        time.sleep(1)

        organize_file(event.src_path, self.folder_path)

def start_watching(folder_path):

    global current_folder
    current_folder = folder_path

    global observer

    print(f"Watching: {folder_path}")

    status_label.config(
        text=f"Watching:\n{folder_path}"
    )

    if observer:
        observer.stop()
        observer.join()

    event_handler = MyHandler(folder_path)

    observer = Observer()

    observer.schedule(
        event_handler,
        folder_path,
        recursive=False
    )

    observer.start()

# 选择文件夹
def select_folder():

    folder_path = filedialog.askdirectory()

    if not folder_path:
        return

    save_config(folder_path)

    start_watching(folder_path)

def on_close():

    global observer

    if observer:
        observer.stop()
        observer.join()

    window.destroy()

def add_rule():

    ext = ext_entry.get().strip().lower()
    cat = cat_entry.get().strip()

    if not ext or not cat:
        return

    rules[ext] = cat

    # 关键：立刻写入 config
    save_config(current_folder)

    # 关键：立刻刷新 UI（可选但推荐）
    stats_label.config(text="Rules updated")

    print(f"Rule added: {ext} -> {cat}")


# GUI
window = tk.Tk()

window.protocol(
    "WM_DELETE_WINDOW",
    on_close
)

window.title("File Organizer")

window.geometry("300x350")

button = tk.Button(
    window,
    text="Select Folder",
    command=select_folder,
    width=20,
    height=2
)

button.pack(pady=20)

status_label = tk.Label(
    window,
    text="No folder selected"
)

status_label.pack(pady=(0, 5))

counter_label = tk.Label(
    window,
    text="Files moved: 0"
)

counter_label.pack(pady=(0, 5))

stats_label = tk.Label(
    window,
    text="No statistics yet"
)


stats_label.pack(pady=(0, 5))

log_label = tk.Label(
    window,
    text="No files moved yet"
)

log_label.pack(pady=(0, 5))

open_btn = tk.Button(
    window,
    text="Open Config",
    command=open_config_file,
    width=20,
    height=1
)

open_btn.pack(pady=5)

saved_path, rules = load_config()

rule_frame = tk.Frame(window)
rule_frame.pack(pady=10)

ext_entry = tk.Entry(rule_frame, width=10)
ext_entry.pack(side=tk.LEFT, padx=5)
ext_entry.insert(0, ".ext")

cat_entry = tk.Entry(rule_frame, width=10)
cat_entry.pack(side=tk.LEFT, padx=5)
cat_entry.insert(0, "Category")

add_rule_btn = tk.Button(
    rule_frame,
    text="Add Rule",
    command=add_rule
)
add_rule_btn.pack(side=tk.LEFT, padx=5)

print(saved_path)
print(rules)

if saved_path:
    start_watching(saved_path)


window.mainloop()