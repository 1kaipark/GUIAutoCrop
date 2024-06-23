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

from typing import Any

image_paths_list = None

metadata_dict = {}
names_thresholded_dict = {}
names_brs_dict = {}


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

def update_metadata(iid: Any, valid_indices: list, thresholded_image: Any, brs: list[Any]):
    # this function will be called by the subwindow, and will update the dict

    if valid_indices:
        # can be fed list of indices to update the treeview and internal storage dict
        metadata_dict[iid] = valid_indices
        tree.item((iid, ), values=('Yes', valid_indices))
        print(metadata_dict)

    if thresholded_image is not None and brs:
        # store these two in memory
        names_thresholded_dict[iid] = thresholded_image
        names_brs_dict[iid] = brs


    # update treeview as well

def on_item_click(event):
    selected_item = tree.selection()  # Get the selected item iid
    show_subwindow(selected_item)


def show_subwindow(iid):
    fpath = tree.item(iid, option='text')
    print("IID", iid)
    print(names_thresholded_dict)
    try:
        thresh = names_thresholded_dict[iid]
        brs = names_brs_dict[iid]
    except KeyError:
        thresh = None
        brs = None
    app = CropWindow(window, fpath, thresh, brs, update_metadata, iid)

    # TODO!
    print(app.image_title)
    try:
        idx = metadata_dict[iid]
    except KeyError:
        idx = None
    tree.item(iid, values=('Yes', idx))


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
