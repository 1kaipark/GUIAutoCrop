"""The sub-window for processing and cropping slides
Souce: passing from subwindow to main window https://www.youtube.com/watch?v=wHeoWM4xv0U

TODO: series of buttons like 
* 'Raise Threshold', 'Lower Threshold'
* Toggle Force Light BG, Toggle Force Dark BG
* +10 Padding, -10 Padding
* Ultimately want to make these sliders. Is there any way to make them automatically update when changed value?

TODO: delete print statements
TODO: (lazy so optional) if cropped, load indices and crop automatically 

 ／l、               
（ﾟ､ ｡ ７         
  l  ~ヽ       
  じしf_,)ノ

"""

from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter import messagebox


from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PIL import Image as PILImage
import numpy as np
import cv2 as cv

import os

from .imgutil import load_img_array
from .autocrop import generate_thresholded_image, get_cropped_images
from .image_data import ImageData

from typing import Callable, Any

class CropWindow(Toplevel):
    def __init__(self, master: Tk, image_path: str, update_callable: Callable, iid: Any, image_data: "ImageData" = ImageData()) -> None:
        super().__init__(master)

        # this is used to pass to update function to update the tree view
        self.iid = iid

        self.image_path = image_path 

        # parse title from file path
        self.image_title = self.image_path.split('/')[-1].split('.')[0] # title of image
        self.title(self.image_title)

        # load image_path into array self.image
        self.image = load_img_array(self.image_path)


        # globally store these
        self.thresh = image_data.thresh # the thresholded image
        self.brs = image_data.brs # list of boundingRects (tuple[x,y,w,h])
        self.idx = image_data.idx # indices of bounding rects to crop by
        self.padding = image_data.padding # padding of cropping rects

        self.cropped_images = [] # list of ndarrays corresponding to each cropped section
        self.is_cropped = False

        # valid indices input entry
        self.valid_idx = StringVar()

        # update callable -- to pass to mainwindow
        self.update_callable = update_callable

        # these parameters are for the object detection and cropping. stored internally
        self.k = 5 # default value

        # initialize UI
        self.init_ui()

    def init_ui(self) -> None: # initialize UI elements
        self.show_image_button = Button(self, command=self.show_image,
                                        height=2, width=10, text = 'Process')
        self.show_image_button.grid(row=1, column=0)

        self.valid_idx_label = Label(self, text='Valid Indices')
        self.valid_idx_entry = Entry(self, textvariable=self.valid_idx)
        self.crop_button = Button(self, command=self.crop_rects,
                                        height=1, width=5, text='Crop')


        self.pad_label = Label(self, text='padding')
        self.pad_spinbox = Spinbox(self, from_=-1000, to = 1000)
        self.pad_spinbox.delete(0, 'end')
        self.pad_spinbox.insert(0, self.padding)
        self.update_padding_btn = Button(self, command=self.update_padding,
                                         height=1, width=8, text='Update Padding')
        

        self.save_button = Button(self, command=self.write_images,
                                  height=1, width=10, text='Save Images')


        self.rotate_button = Button(self, command=self.rotate,
                                    height=1, width=10, text='Rotate')

        self.resizable(False, False)

        # if already fed thresholded image, display it
        if self.thresh is not None and self.brs is not None:
            self.show_image(pad=self.padding)

    def update_image_data(self):
        return ImageData(thresh=self.thresh, brs=self.brs, idx=self.idx, padding=self.padding)

    def update_ui(self) -> None:
        # once the image is processed, grid everything
        self.pad_label.grid(row=1, column=4)
        self.pad_spinbox.grid(row=1, column=5)
        self.update_padding_btn.grid(row=1, column=6)


        self.valid_idx_label.grid(row=3, column=4)
        self.valid_idx_entry.grid(row=3, column=5)
        if self.idx:
            self.valid_idx_entry.delete(0, 'end')
            self.valid_idx_entry.insert(0, ','.join([str(i) for i in self.idx]))
        self.crop_button.grid(row=3, column=6)

    def update_ui_post_crop(self) -> None:
        self.rotate_button.grid(row=5, column=4)
        self.save_button.grid(row=5, column=5)

    # function to process (threshold, display indices) passed image to init
    def show_image(self, pad: int = 50) -> None:
        # self.image
        if (self.image is not None and 
                self.thresh is None and
                self.brs is None):
            self.title('Processing Image') # update status as title
            self.is_cropped = False # use this to keep tabs on whether the image is cropped
            self.thresh, self.brs = generate_thresholded_image(self.image, self.k, pad)

        fig = Figure()
        plot = fig.add_subplot()

        # pass thresh and brs to update function
        self.update_callable(iid=self.iid, image_data = self.update_image_data())

        # show on plot widget
        plot.imshow(self.thresh)

        for n, rect in enumerate(self.brs):
            x, y, w, h = rect
            plot.text(x=x, y=y - (0.2*y), s=f'idx {n}', color='w')

        # HIDE AXES: https://www.tutorialspoint.com/how-to-turn-off-the-ticks-and-marks-of-a-matlibplot-axes
        # Hide X and Y axes label marks
        plot.xaxis.set_tick_params(labelbottom=False)
        plot.yaxis.set_tick_params(labelleft=False)

        # Hide X and Y axes tick marks
        plot.set_xticks([])
        plot.set_yticks([])

        fig.tight_layout(pad=0)

        # add to tkinter canvas
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()

        self.title(self.image_title)

        canvas.get_tk_widget().grid(row=2, column=0)
        self.update_ui()


    def update_padding(self) -> None:
        self.padding = int(self.pad_spinbox.get())
        self.update_callable(self.iid, self.update_image_data())
        self.thresh, self.brs = generate_thresholded_image(image=self.image, k=self.k, pad=self.padding)
        self.show_image(pad=self.padding)

    # code to crop the image according to the defined boundingRects
    def crop_rects(self) -> None:
        try:
            # try to parse indices entry
            self.idx = self.valid_idx.get().split(',')
            self.idx = [int(i.strip()) for i in self.idx]
            print(self.idx)
        except Exception:
            print("unable to parse input {}".format(self.valid_idx.get()))
            return 0

        print(self.image, self.brs)
        if (self.image is not None and self.brs is not None):
            print('will attempt to crop image of size {} into {} rects.'.format(self.image.shape, len(self.brs)))
            # crop the images and save to self.cropped_images list
            self.cropped_images = get_cropped_images(source_image=self.image,
                                                      valid_idx=self.idx,
                                                      brs=self.brs)
            print("{} images cropped".format(len(self.cropped_images)))

            self.update_ui_post_crop()

            # call update function
            self.update_callable(iid=self.iid, image_data=self.update_image_data())

            self.is_cropped = True

        if len(self.cropped_images) != 0:
            self.image_shown = False # the OG/processed image is no longer shown
            fig = Figure()
            plot = fig.subplots(1, len(self.idx))
            if len(self.cropped_images) > 1:
                for i, cropped_img in enumerate(self.cropped_images):
                    plot[i].imshow(cropped_img)
                    plot[i].set_title(f'_s{str(i+1).zfill(3)}')

                    # hide axes
                    plot[i].axis('off')
            else:
                plot.imshow(self.cropped_images[0])
                plot.set_title(f'_s{str(1).zfill(3)}')

                # hide axes
                plot.axis('off')



            fig.tight_layout(pad=0)

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()

            canvas.get_tk_widget().grid(row=2, column=0)

            self.is_cropped = True
            self.rotate_button.grid(row=5, column=0)


    # rotate button will perform a 90 degree clockwise rotation
    def rotate(self) -> None:
        if len(self.cropped_images) != 0:
            self.cropped_images = [cv.rotate(img, cv.ROTATE_90_CLOCKWISE) for img in self.cropped_images]

            fig = Figure()
            plot = fig.subplots(1, len(self.idx))
            if len(self.cropped_images) > 1:
                for i, cropped_img in enumerate(self.cropped_images):
                    plot[i].imshow(cropped_img)
                    plot[i].set_title(f'_s{str(i+1).zfill(3)}')

                    # hide axes
                    plot[i].axis('off')
            else:
                plot.imshow(self.cropped_images[0])
                plot.set_title(f'_s{str(1).zfill(3)}')
                # hide axes
                plot.axis('off')

            fig.tight_layout(pad=0)

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()

            canvas.get_tk_widget().grid(row=2, column=0)
            self.is_cropped = True
            self.rotate_button.grid(row=5, column=0)

    def write_images(self) -> None:
        if len(self.cropped_images) != 0:
            root = Tk()
            root.withdraw()
            save_path = askdirectory()

            for idx, o in enumerate(self.cropped_images):
                out_img = PILImage.fromarray(o)
                out_name = "{}_s{}".format(self.image_title, str(idx+1).zfill(3))
                out_path = os.path.join(save_path, out_name)
                out_img.save(out_path + '.png')

            messagebox.showinfo('Saved', 'Saved Images to {}'.format(out_path))
