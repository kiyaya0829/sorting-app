import os
import shutil
import time
import tkinter as tk

from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 分类规则
file_types = {
    "Images": [".jpg", ".png"],
    "Videos": [".mp4"],
    "Documents": [".pdf", ".txt"],
    "Archives": [".zip", ".rar"]
}

observer = None

# 文件整理
def organize_file(file_path, folder_path):

    if os.path.isdir(file_path):
        return

    file_name = os.path.basename(file_path)

    _, extension = os.path.splitext(file_name)

    extension = extension.lower()

    moved = False

    # 分类
    for category, extensions in file_types.items():

        if extension in extensions:

            category_folder = os.path.join(folder_path, category)

            os.makedirs(category_folder, exist_ok=True)

            shutil.move(
                file_path,
                os.path.join(category_folder, file_name)
            )

            print(f"Moved: {file_name} -> {category}")

            moved = True

            break

    # Others
    if not moved:

        other_folder = os.path.join(folder_path, "Others")

        os.makedirs(other_folder, exist_ok=True)

        shutil.move(
            file_path,
            os.path.join(other_folder, file_name)
        )

        print(f"Moved: {file_name} -> Others")

# 监听类
class MyHandler(FileSystemEventHandler):

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def on_created(self, event):

        time.sleep(1)

        organize_file(event.src_path, self.folder_path)

# 选择文件夹
def select_folder():

    global observer

    folder_path = filedialog.askdirectory()

    if not folder_path:
        return

    print(f"Watching: {folder_path}")

    # 如果之前已经监听
    if observer:
        observer.stop()

    event_handler = MyHandler(folder_path)

    observer = Observer()

    observer.schedule(
        event_handler,
        folder_path,
        recursive=False
    )

    observer.start()

def on_close():

    global observer

    if observer:
        observer.stop()
        observer.join()

    window.destroy()

window.protocol(
    "WM_DELETE_WINDOW",
    on_close
)

# GUI
window = tk.Tk()

window.title("File Organizer")

window.geometry("300x150")

button = tk.Button(
    window,
    text="Select Folder",
    command=select_folder,
    width=20,
    height=2
)

button.pack(pady=40)

window.mainloop()