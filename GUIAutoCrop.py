# https://pythonassets.com/posts/treeview-in-tk-tkinter/

from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askopenfilenames

from crop_window import CropWindow

image_paths_list = None


def load_images():
    global image_paths_list
    root = Tk()
    root.withdraw()
    image_paths_list = askopenfilenames(parent=root)
    image_paths_list = sorted(image_paths_list)
    for i, image_path in enumerate(image_paths_list):
        tree.insert("", END, text=image_path, values=('No'), iid=f'00{i}')


def on_item_click(event):
    selected_item = tree.selection()[0]  # Get the selected item's iid
    show_subwindow(selected_item)


def show_subwindow(iid):
    fpath = tree.item(iid, option='text')
    app = CropWindow(window, fpath)
    tree.item(iid, values=('Yes'))


window = Tk()
window.title("Treeview Test")

tree = ttk.Treeview(master=window, columns=('processed'))
tree.heading('#0', text='Item')
tree.heading('processed', text='Viewed')

# Bind the click event
tree.bind("<ButtonRelease-1>", on_item_click)

open_files_button = Button(master=window, text="open files", command=load_images)

tree.grid(row=1, column=0)
open_files_button.grid(row=0, column=0)

window.resizable(False, False)
window.mainloop()
