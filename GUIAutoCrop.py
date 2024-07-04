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
import json

image_paths_list = None



class SlidesManager(object):
    def __init__(self, root: Tk) -> None:
        """Initialize Class"""
        self.root = root

        self.image_paths_list = None
        self.image_data_dict = {}

        self.create_widgets()

        with open('config.json', 'rb') as fi:
            self.config = json.load(fi)


    def create_widgets(self) -> None:
        """Initialize UI elements"""
        self.tree = ttk.Treeview(master=self.root, columns=('fname', 'padding', 'crop_indices'))
        self.tree.heading('#0', text='Item')
        self.tree.heading('fname', text='File Name')
        self.tree.heading('padding', text='Padding')
        self.tree.heading('crop_indices', text='Cropping Indices')
        # bind to single click
        self.tree.bind("<ButtonRelease-1>", self.on_item_click)

        self.open_files_button = Button(master=self.root, text="open files", command=self.load_images)
        self.clear_files_button = Button(master=self.root, text="clear files", command=self.clear_files)

        self.tree.grid(row=2, column=0)
        self.open_files_button.grid(row=0, column=0)
        self.clear_files_button.grid(row=1, column=0)

        self.root.resizable(False, False)


    def load_images(self) -> None:
        """Called by the load images button. Opens a file dialog to choose slide images"""
        self.image_paths_list = askopenfilenames(parent=self.root)
        self.image_paths_list = sorted(self.image_paths_list)
        for image_path in self.image_paths_list:
            fname = os.path.split(image_path)[-1]
            try:
                self.tree.insert("", END, text=image_path, values=(fname, ImageData().padding, None), iid=fname)
            except TclError:
                # if the IID is already taken, the image is already in the tree (unless something super weird happened.)
                pass
            self.image_data_dict[fname] = ImageData(image_id=fname) # initialize dict with empty containers

    def clear_files(self) -> None:
        self.image_paths_list = []
        self.image_data_dict = {}

        for i in self.tree.get_children():
            self.tree.delete(i)

    def update_metadata(self, image_data: "ImageData"):
        print('update callable', image_data.padding, image_data.idx)

        # this function will be called by the subwindow, and will update the dict
        fname = image_data.image_id
        self.image_data_dict[fname] = image_data
        if image_data.idx is not None:
            idx_str = ','.join([str(i) for i in image_data.idx])
        else:
            idx_str = None
            # can be fed list of indices to update the treeview and internal storage dict
        self.tree.item((fname, ), values=(fname, image_data.padding, idx_str))

    def on_item_click(self, event):
        selected_item = self.tree.selection()  # Get the selected item iid
        self.show_subwindow(selected_item)


    def show_subwindow(self, iid):
        fpath = self.tree.item(iid, option='text')
        fname = os.path.split(fpath)[-1]
        app = CropWindow(root=self.root, 
                        image_path=fpath, 
                        update_callable=self.update_metadata,  
                        image_data=self.image_data_dict[fname],
                        config=self.config)

        # TODO!
        idx = self.image_data_dict[fname].idx
        padding = self.image_data_dict[fname].padding

        self.tree.item(iid, values=(fname, padding, idx))

if __name__ == "__main__":
    root = Tk()
    root.title('Select Slides')
    root.attributes("-alpha", 0.95)
    app = SlidesManager(root)
    root.mainloop()
