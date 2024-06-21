# https://pythonassets.com/posts/treeview-in-tk-tkinter/

from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askopenfilenames
from _tkinter import TclError

import random

from crop_window import CropWindow

from typing import Any

image_paths_list = None
metadata_dict = {}


def load_images():
    global image_paths_list
    root = Tk()
    root.withdraw()
    image_paths_list = askopenfilenames(parent=root)
    image_paths_list = sorted(image_paths_list)
    for image_path in image_paths_list:
        try:
            tree.insert("", END, text=image_path, values=('No', None), iid=f'{image_path.split("/")[-1]}')
        except TclError:
            # if the IID is already taken, just append a random digit to it. good enough for government work
            tree.insert("", END, text=image_path, values=('No', None), iid=f'{image_path.split("/")[-1]}_{random.choice(range(10))}')

def update_metadata(img_name: Any, valid_indices: list):
    # this function will be called by the subwindow, and will update the dict
    metadata_dict[img_name] = valid_indices
    tree.item((img_name, ), values=('Yes', valid_indices))

    print(metadata_dict)

    # update treeview as well



def on_item_click(event):
    selected_item = tree.selection()  # Get the selected item iid
    show_subwindow(selected_item)


def show_subwindow(iid):
    fpath = tree.item(iid, option='text')
    print("IID", iid)
    app = CropWindow(window, fpath, update_metadata, iid)
    # TODO!
    print(app.image_title)
    tree.item(iid, values=('Yes', None))


window = Tk()
window.title("Select Slides")

tree = ttk.Treeview(master=window, columns=('processed', 'crop_indices'))
tree.heading('#0', text='Item')
tree.heading('processed', text='Viewed')
tree.heading('crop_indices', text='Cropping Indices')

# bind to single click
tree.bind("<ButtonRelease-1>", on_item_click)

open_files_button = Button(master=window, text="open files", command=load_images)

tree.grid(row=1, column=0)
open_files_button.grid(row=0, column=0)

window.resizable(False, False)
window.mainloop()
