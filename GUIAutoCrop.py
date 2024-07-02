# https://pythonassets.com/posts/treeview-in-tk-tkinter/
"""Main window for opening files
TODO: 'Viewed' to 'Processed'
 ／l、               
（ﾟ､ ｡ ７         
  l  ~ヽ       
  じしf_,)ノ

"""
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askopenfilenames
from _tkinter import TclError

import random

from lib.crop_window import CropWindow
from lib.image_data import ImageData

from typing import Any

import os

image_paths_list = None

image_data_dict = {}


def load_images():
    global image_paths_list
    root = Tk()
    root.withdraw()
    image_paths_list = askopenfilenames(parent=root)
    image_paths_list = sorted(image_paths_list)
    for image_path in image_paths_list:
        fname = os.path.split(image_path)[-1]
        try:
            tree.insert("", END, text=image_path, values=(fname, 'No', None), iid=fname)
        except TclError:
            # if the IID is already taken, the image is already in the tree (unless something super weird happened.)
            pass
        image_data_dict[fname] = ImageData()

def update_metadata(iid: Any, image_data: "ImageData"):
    print('update callable', image_data.padding, image_data.idx)
    # this function will be called by the subwindow, and will update the dict
    fname = iid[0] if isinstance(iid, tuple) else iid
    image_data_dict[fname] = image_data
    if image_data.idx is not None:
        # can be fed list of indices to update the treeview and internal storage dict
        tree.item((fname, ), values=(fname, image_data.padding, ','.join([str(i) for i in image_data.idx])))
        print(image_data_dict)

def on_item_click(event):
    selected_item = tree.selection()  # Get the selected item iid
    show_subwindow(selected_item)


def show_subwindow(iid):
    fpath = tree.item(iid, option='text')
    fname = os.path.split(fpath)[-1]
    app = CropWindow(master=window, 
                     image_path=fpath, 
                     update_callable=update_metadata, 
                     iid=iid, 
                     image_data=image_data_dict[fname])

    # TODO!
    print(app.image_title)
    try:
        idx = image_data_dict[fname].idx
        padding = image_data_dict[fname].padding
    except Exception:
        idx = None
        padding = None

    tree.item(iid, values=(fname, padding, idx))


window = Tk()
window.title("Select Slides")

tree = ttk.Treeview(master=window, columns=('fname', 'padding', 'crop_indices'))
tree.heading('#0', text='Item')
tree.heading('fname', text='File Name')
tree.heading('padding', text='Padding')
tree.heading('crop_indices', text='Cropping Indices')

# bind to single click
tree.bind("<ButtonRelease-1>", on_item_click)

open_files_button = Button(master=window, text="open files", command=load_images)

tree.grid(row=1, column=0)
open_files_button.grid(row=0, column=0)

window.resizable(False, False)
window.mainloop()
