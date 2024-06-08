# The sub-window for processing and cropping slides

from tkinter import *
from tkinter.filedialog import askdirectory

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PIL import Image as PILImage
import cv2 as cv

import os

from shortcuts.imgutil import load_img_array
from autocrop import generate_thresholded_image, get_cropped_images

class CropWindow(Toplevel):
    def __init__(self, master, img_path):
        super().__init__(master)

        self.image_path = img_path

        # parse title from file path
        self.image_title = img_path.split('/')[-1].split('.')[0] # title of image
        self.title(self.image_title)

        # load image_path into array self.image
        self.image = load_img_array(self.image_path)
        print(self.image.shape)

        self.idx = [] # indices of bounding rects to crop by
        self.brs = [] # list of boundingRects (tuple[x,y,w,h])

        self.cropped_images = [] # list of ndarrays corresponding to each cropped section
        self.is_cropped = False

        # valid indices input entry
        self.valid_idx = StringVar()

        # initialize UI
        self.init_ui()

    def init_ui(self): # initialize UI elements
        self.show_image_button = Button(self, command=self.show_image,
                                        height=1, width=8, text = 'Process')
        self.show_image_button.grid(row=1, column=0)

        self.valid_idx_label = Label(self, text='Valid Indices')
        self.valid_idx_entry = Entry(self, textvariable=self.valid_idx)
        self.crop_button = Button(self, command=self.crop_rects,
                                        height=1, width=5, text='Crop')

        self.valid_idx_label.grid(row=4, column=0)
        self.valid_idx_entry.grid(row=4, column=1)
        self.crop_button.grid(row=4, column=2)

        self.save_button = Button(self, command=self.write_images,
                                  height=1, width=10, text='Save Images')
        self.save_button.grid(row=6, column=0)

        self.rotate_button = Button(self, command=self.rotate,
                                    height=1, width=10, text='Rotate')

        self.resizable(False, False)


    # function to process (threshold, display indices) passed image to init
    def show_image(self):
        # self.image
        if self.image is not None:
            self.is_cropped = False # use this to keep tabs on whether the image is cropped

            fig = Figure()
            plot = fig.add_subplot()

            thresh, self.brs = generate_thresholded_image(self.image)
            plot.imshow(thresh)

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

            canvas.get_tk_widget().grid(row=2, column=0)
            self.rotate_button.grid(row=5, column=0)

        else:
            print('No Images to crop!')


    # code to crop the image according to the defined boundingRects
    def crop_rects(self):
        try:
            # try to parse indices entry
            self.idx = self.valid_idx.get().split(',')
            self.idx = [int(i.strip()) for i in self.idx]
            print(self.idx)
        except Exception:
            print("Enter indices as integer values, separated by columns.")

        if (self.image is not None and len(self.brs) != 0):
            print('will attempt to crop.')
            # crop the images and save to self.cropped_images list
            self.cropped_images = get_cropped_images(source_image=self.image,
                                                      valid_idx=self.idx,
                                                      brs=self.brs)
            print("{} images cropped".format(len(self.cropped_images)))
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
    def rotate(self):
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

    def write_images(self):
        if len(self.cropped_images) != 0:
            root = Tk()
            root.withdraw()
            save_path = askdirectory()

            for idx, o in enumerate(self.cropped_images):
                out_img = PILImage.fromarray(o)
                out_name = "{}_s{}".format(self.image_title, str(idx+1).zfill(3))
                out_path = os.path.join(save_path, out_name)
                out_img.save(out_path + '.png')

from shortcuts.file_io import choose_file
if __name__ == "__main__":
    root = Tk()
    app = CropWindow(root, img_path='/Users/applelaptop/QUINT_WD/PawtyAnimal5/MC/stitched/slide17.tif')
    root.mainloop()

