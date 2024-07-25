"""The sub-window for processing and cropping slides
Souce: passing from subwindow to main window https://www.youtube.com/watch?v=wHeoWM4xv0U

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

from .autocrop import load_img_array, generate_thresholded_image, get_cropped_images
from .image_data import ImageData

from typing import Callable, Any


class CropWindow(Toplevel):
    def __init__(
        self,
        root: Tk,
        image_path: str,
        update_callable: Callable[["ImageData"], Any],
        image_data: "ImageData" = ImageData(),
        config: dict = None,
    ) -> None:
        """Initialize the class --
        * 'root' -- tkinter root,
        * 'image_path' -- path to image to be parsed.
        * 'image_data' -- ImageData object that contains attributes,
        * 'update_callable' -- communicate with parent window"""
        super().__init__(root)

        self.image_path = image_path

        # load image_path into array self.image
        self.image = load_img_array(self.image_path)

        # this information is stored in an ImageData object
        self.iid = image_data.image_id  # image identifier, useful for TreeView
        self.thresh = image_data.thresh  # the thresholded image
        self.brs = image_data.brs  # list of boundingRects (tuple[x,y,w,h])
        self.crop_indices = image_data.crop_indices  # indices of bounding rects to crop by
        self.padding = image_data.padding  # padding of cropping rects

        self.title(self.iid)

        self.cropped_images = (
            []
        )  # list of ndarrays corresponding to each cropped section

        # valid indices input entry
        self.entered_crop_indices = StringVar()

        # update callable -- to pass to mainwindow
        self.update_callable = update_callable

        # config stores parameters for thresholding algorithm
        self.config = config

        # initialize UI
        self.create_widgets()

    def create_widgets(self) -> None:
        """Initialize UI Elements"""
        self.show_image_button = Button(
            self, command=self.show_image, height=2, width=10, text="Process"
        )
        self.show_image_button.grid(row=1, column=0)

        self.crop_indices_label = Label(self, text="Valid Indices")
        self.crop_indices_entry = Entry(self, textvariable=self.entered_crop_indices)
        self.crop_button = Button(
            self, command=self.crop_rects, height=1, width=5, text="Crop"
        )

        self.pad_label = Label(self, text="padding")
        self.pad_spinbox = Spinbox(self, from_=-1000, to=1000)
        self.pad_spinbox.delete(0, "end")
        self.pad_spinbox.insert(0, self.padding)
        self.update_padding_btn = Button(
            self, command=self.update_padding, height=1, width=8, text="Update Padding"
        )

        self.save_button = Button(
            self, command=self.write_images, height=1, width=10, text="Save Images"
        )

        self.rotate_button = Button(
            self, command=self.rotate, height=1, width=10, text="Rotate"
        )

        self.resizable(False, False)

        # if already fed thresholded image, display it
        if self.thresh is not None and self.brs is not None:
            self.show_image(pad=self.padding)

    def update_image_data(self) -> "ImageData":
        """Returns ImageData object with updated attributes"""
        return ImageData(
            image_id=self.iid,
            thresh=self.thresh,
            brs=self.brs,
            crop_indices=self.crop_indices,
            padding=self.padding,
        )

    def update_widgets(self) -> None:
        """Called once image is processed, places the rest of the UI"""
        self.pad_label.grid(row=1, column=4)
        self.pad_spinbox.grid(row=1, column=5)
        self.update_padding_btn.grid(row=1, column=6)

        self.crop_indices_label.grid(row=3, column=4)
        self.crop_indices_entry.grid(row=3, column=5)
        if self.crop_indices:
            self.crop_indices_entry.delete(0, "end")
            self.crop_indices_entry.insert(0, ",".join([str(i) for i in self.crop_indices]))
        self.crop_button.grid(row=3, column=6)

    def update_widgets_post_crop(self) -> None:
        """Shows the rotate button"""
        self.rotate_button.grid(row=5, column=4)
        self.save_button.grid(row=5, column=5)

    # function to process (threshold, display indices) passed image to init
    def show_image(self, pad: int = 50) -> None:
        """Processes the image -- threshold, bounding rects + indices"""
        if self.image is not None and self.thresh is None and len(self.brs) == 0:
            self.thresh, self.brs = generate_thresholded_image(
                image=self.image,
                pad=pad,
                k=self.config["k"],
                erosion=self.config["erosion"],
                erosion_iterations=self.config["erosion_iterations"],
                clahe_clip_limit=self.config["clahe_clip_limit"],
                clahe_tile_grid_size=self.config["clahe_tile_grid_size"],
            )

        fig = Figure()
        plot = fig.add_subplot()

        # pass thresh and brs to update function
        self.update_callable(image_data=self.update_image_data())

        # show on plot widget
        plot.imshow(self.thresh)

        for n, rect in enumerate(self.brs):
            x, y, w, h = rect
            plot.text(x=x, y=y - (0.2 * y), s=f"idx={n}", color="w")

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

        canvas.get_tk_widget().grid(row=2, column=0)
        self.update_widgets()

    def update_padding(self) -> None:
        """Called to update the padding"""
        self.padding = int(self.pad_spinbox.get())
        self.thresh, self.brs = generate_thresholded_image(
            image=self.image, k=self.config['k'], pad=self.padding
        )
        self.show_image(pad=self.padding)  # update callable is called here

    def crop_rects(self) -> None:
        """code to crop the image according to the defined boundingRects"""
        try:
            # try to parse indices entry
            self.crop_indices = self.entered_crop_indices.get().split(",")
            self.crop_indices = [int(i.strip()) for i in self.crop_indices]
        except Exception:
            print("unable to parse input {}".format(self.crop_indices.get()))
            return 0

        if self.image is not None and self.brs is not None:
            print(
                "will attempt to crop image of size {} into {} rects.".format(
                    self.image.shape, len(self.brs)
                )
            )
            # crop the images and save to self.cropped_images list
            self.cropped_images = get_cropped_images(
                source_image=self.image, crop_indices=self.crop_indices, brs=self.brs
            )
            print("{} images cropped".format(len(self.cropped_images)))

            self.update_widgets_post_crop()

            # call update function
            self.update_callable(image_data=self.update_image_data())

        if len(self.cropped_images) != 0:
            fig = Figure()
            plot = fig.subplots(1, len(self.crop_indices))
            if len(self.cropped_images) > 1:
                for i, cropped_img in enumerate(self.cropped_images):
                    plot[i].imshow(cropped_img)
                    plot[i].set_title(f"_s{str(i+1).zfill(3)}")

                    # hide axes
                    plot[i].axis("off")
            else:
                plot.imshow(self.cropped_images[0])
                plot.set_title(f"_s{str(1).zfill(3)}")

                # hide axes
                plot.axis("off")

            fig.tight_layout(pad=0)

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()

            canvas.get_tk_widget().grid(row=2, column=0)
            self.rotate_button.grid(row=5, column=0)

    # rotate button will perform a 90 degree clockwise rotation
    def rotate(self) -> None:
        if len(self.cropped_images) != 0:
            self.cropped_images = [
                cv.rotate(img, cv.ROTATE_90_CLOCKWISE) for img in self.cropped_images
            ]

            fig = Figure()
            plot = fig.subplots(1, len(self.crop_indices))
            if len(self.cropped_images) > 1:
                for i, cropped_img in enumerate(self.cropped_images):
                    plot[i].imshow(cropped_img)
                    plot[i].set_title(f"_s{str(i+1).zfill(3)}")

                    # hide axes
                    plot[i].axis("off")
            else:
                plot.imshow(self.cropped_images[0])
                plot.set_title(f"_s{str(1).zfill(3)}")
                # hide axes
                plot.axis("off")

            fig.tight_layout(pad=0)

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()

            canvas.get_tk_widget().grid(row=2, column=0)
            self.rotate_button.grid(row=5, column=0)

    def write_images(self) -> None:
        if len(self.cropped_images) != 0:
            root = Tk()
            root.withdraw()
            save_path = askdirectory()

            for crop_indices, o in enumerate(self.cropped_images):
                out_img = PILImage.fromarray(o)
                out_name = "{}_s{}".format(self.iid, str(crop_indices + 1).zfill(3))
                out_path = os.path.join(save_path, out_name)
                out_img.save(out_path + ".png")

            messagebox.showinfo("Saved", "Saved Images to {}".format(out_path))
