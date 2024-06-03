"""
GUI for autocrop?

https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/
https://www.geeksforgeeks.org/python-tkinter-entry-widget/

 ／l、                KP❤️
（ﾟ､ ｡ ７
  l  ~ヽ
  じしf_,)ノ

"""

from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tkinter.filedialog import askopenfilename, askdirectory

from shortcuts.imgutil import load_img_array
from autocrop import generate_thresholded_image, save_cropped_images

import os

from PIL import Image as PILImage
import cv2 as cv

image = None
image_shown = False
idx = []
brs = []

cropped_images = None
cropped_images_shown = False

image_title = None  # Global this... use this to save images


# image_title.split('.')[0]

def choose_image() -> None:
    global image
    root = Tk()
    root.withdraw()
    img_path = askopenfilename()
    
    # set image_title variable
    global image_title
    image_title = img_path.split('/')[-1].split('.')[0]
    print(image_title)

    image = load_img_array(img_path)
    global image_shown
    global brs
    global cropped_images_shown

    if image is not None and not image_shown:
        cropped_images_shown = False
        fig = Figure()
        # y = [i**2 for i in range(101)]
        plot1 = fig.add_subplot(111)

        thresh, brs = generate_thresholded_image(image)
        plot1.imshow(thresh)

        for n, rect in enumerate(brs):
            x, y, w, h = rect
            plot1.text(x=x, y=y - (0.2 * y), s=f'idx {n}', color='w')

        # HIDE AXES: https://www.tutorialspoint.com/how-to-turn-off-the-ticks-and-marks-of-a-matlibplot-axes
        # Hide X and Y axes label marks
        plot1.xaxis.set_tick_params(labelbottom=False)
        plot1.yaxis.set_tick_params(labelleft=False)

        # Hide X and Y axes tick marks
        plot1.set_xticks([])
        plot1.set_yticks([])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()

        canvas.get_tk_widget().grid(row=2, column=0)
        canvas.get_tk_widget().grid(row=2, column=0)

        image_shown = True

    else:
        print("no!!!")  # TODO: messagebox


def crop_rects():
    global idx
    # get indices from entry
    try:
        idx = valid_idx.get().split(',')
        idx = [int(i.strip()) for i in idx]
    except Exception:
        print('Enter indices as integer values here, separated by commas.')  # TODO: messagebox
    print(idx)

    # crop the rectangles according to indices
    global cropped_images
    global image
    global brs

    if image is not None and brs is not None:
        # save cropped images to a list of arrays
        cropped_images = save_cropped_images(source_image=image, valid_idx=idx, brs=brs)
        print("{} images cropped".format(len(cropped_images)))

    global cropped_images_shown
    global image_shown
    global image_title

    if cropped_images is not None and not cropped_images_shown:
        image_shown = False
        print("attempting to plot")
        fig = Figure()
        # y = [i**2 for i in range(101)]
        plot1 = fig.subplots(1, len(idx))
        for i, cropped_img in enumerate(cropped_images):
            plot1[i].imshow(cropped_img)
            plot1[i].set_title(f'_s{str(i + 1).zfill(3)}')

            # HIDE AXES: https://www.tutorialspoint.com/how-to-turn-off-the-ticks-and-marks-of-a-matlibplot-axes
            # Hide X and Y axes label marks
            plot1[i].xaxis.set_tick_params(labelbottom=False)
            plot1[i].yaxis.set_tick_params(labelleft=False)

            # Hide X and Y axes tick marks
            plot1[i].set_xticks([])
            plot1[i].set_yticks([])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()

        canvas.get_tk_widget().grid(row=2, column=0)
        canvas.get_tk_widget().grid(row=2, column=0)

        cropped_images_shown = True
        rotate_button.grid(row=5, column=0)

    else:
        print("no!!!")  # TODO: messagebox


def rotate():
    global cropped_images
    if cropped_images is not None:
        cropped_images = [cv.rotate(img, cv.ROTATE_90_CLOCKWISE) for img in cropped_images]
        fig = Figure()
        # y = [i**2 for i in range(101)]
        plot1 = fig.subplots(1, len(idx))
        for i, cropped_img in enumerate(cropped_images):
            plot1[i].imshow(cropped_img)
            plot1[i].set_title(f'_s{str(i + 1).zfill(3)}')

            # HIDE AXES: https://www.tutorialspoint.com/how-to-turn-off-the-ticks-and-marks-of-a-matlibplot-axes
            # Hide X and Y axes label marks
            plot1[i].xaxis.set_tick_params(labelbottom=False)
            plot1[i].yaxis.set_tick_params(labelleft=False)

            # Hide X and Y axes tick marks
            plot1[i].set_xticks([])
            plot1[i].set_yticks([])

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()

        canvas.get_tk_widget().grid(row=2, column=0)
        canvas.get_tk_widget().grid(row=2, column=0)

        cropped_images_shown = True
        rotate_button.grid(row=5, column=0)


def write_images():
    global cropped_images
    global image_title

    # get directory to write images to
    root = Tk()
    root.withdraw()
    save_path = askdirectory()
    print(save_path)

    for idx, o in enumerate(cropped_images):
        out_img = PILImage.fromarray(o)
        out_name = f"{image_title}_s{str(idx + 1).zfill(3)}.png"
        out_img.save(os.path.join(save_path, out_name))


window = Tk()
window.title('hello bro')

valid_idx = StringVar()

choose_image_button = Button(master=window,
                             command=choose_image,
                             height=1, width=10,
                             text='choose image')

valid_idx_label = Label(master=window,
                        text='valid indices')
valid_idx_entry = Entry(master=window,
                        textvariable=valid_idx)
submit_idx_button = Button(master=window,
                           command=crop_rects,
                           height=1, width=5,
                           text='crop')

save_button = Button(master=window,
                     command=write_images,
                     height=1, width=5,
                     text='save images')

rotate_button = Button(master=window,
                       command=rotate,
                       height=1, width=5,
                       text='rotate')

choose_image_button.grid(row=0, column=0)
valid_idx_label.grid(row=4, column=0)
valid_idx_entry.grid(row=4, column=1)
submit_idx_button.grid(row=4, column=2)
save_button.grid(row=6, column=0)

window.resizable(False, False)
window.mainloop()
