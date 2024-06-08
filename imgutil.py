'''
imgutil: set of wrapper functions to deal with images as arrays.

 ／l、               KP
（ﾟ､ ｡ ７
  l  ~ヽ
  じしf_,)ノ
'''
from typing import Sequence, Any
from PIL import Image, UnidentifiedImageError
import numpy as np
from numpy import ndarray
from cv2 import Mat
import cv2 as cv
import os

def load_img_array(ipath: str) -> np.ndarray:
    '''load image path as ndarray'''
    return np.asarray(Image.open(ipath)) # use PIL to open, then return the array

def invert(img: np.ndarray) -> np.ndarray:
    '''simple invert colors functino'''
    return (255 - img)

def bin_thresh(img: np.ndarray, pix_thresh: int = 100) -> np.ndarray:
    _, thresh = cv.threshold(img, pix_thresh, 255, cv.THRESH_BINARY) # apply threshold according to specified value
    return thresh

def split_channels(img: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """returns red, green, blue channels from given RGB image array"""
    r, g, b = img[:,:,0], img[:,:,1], img[:,:,2] # split channels, output grayscale
    # return RGB images
    zero = np.zeros(img.shape[0:2], np.uint8)  # zero array w same shape as image, must be 8-bit unsigned int
    red_ch = cv.merge([r, zero, zero])
    green_ch = cv.merge([zero, g, zero])
    blue_ch = cv.merge([zero, zero, b])
    return red_ch, green_ch, blue_ch

def reconstruct_splits(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
    '''undo the split_channels fxn'''
    return cv.merge([r[:,:,0], g[:,:,1], b[:,:,2]])

def erode(img: np.ndarray, iterations: int = 2, kernel_size: int = 3) -> np.ndarray:
    '''applies erosion according to the specified parameters'''
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    img = cv.erode(img, kernel, iterations = iterations, anchor = (1, 1))
    return img

def dilate(img: np.ndarray, iterations: int = 2, kernel_size: int = 3) -> np.ndarray:
    '''applies erosion according to the specified parameters'''
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    img = cv.dilate(img, kernel, iterations = iterations, anchor = (1, 1))
    return img
    
def get_all_contours(img: np.ndarray) -> tuple[Sequence[Mat | ndarray | ndarray], Mat | ndarray | ndarray]:
    """will return all contours for given (processed - eroded or grayscale) image"""
    contours, hierarchy = cv.findContours(
        image=img,
        mode=cv.RETR_TREE,
        method=cv.CHAIN_APPROX_NONE
    )  # find contours using openCV
    return contours, hierarchy

def get_largest_contours(img: np.ndarray, n_contours: int = 1, min_area: int = 0) -> list[Mat | ndarray | ndarray]:
    """returns n largest contours for a given processed image"""
    contours, hierarchy = cv.findContours(
        image=img,
        mode=cv.RETR_TREE,
        method=cv.CHAIN_APPROX_NONE
    )
    sorted_contours = sorted(contours, key=lambda x: cv.contourArea(x), reverse=True)
    largest_contours = sorted_contours[:n_contours]
    return [contour for contour in largest_contours if cv.contourArea(contour) >= min_area]

def approx_contours(contours: Any, ep: float = 0.015) -> list[Mat | ndarray | ndarray]:
    """returns list of approximate contours for a given set of contours -- smaller epsilon values represent a sharper approximation. given by Ramer-Douglas-Peucker algorithm."""
    approx_rois = []
    for contour in contours:
        perimeter = ep * cv.arcLength(contour, True)
        dp = cv.approxPolyDP(contour, perimeter, True)
        approx_rois.append(dp)
    return approx_rois

def crop_rect(img: np.ndarray, rect: tuple[int, int, int, int], pad: int = 50) -> np.ndarray:
    '''simple function to return an image cropped according to a rectangle. padding is in pixels'''
    x, y, w, h = rect
    # for whatever dumbass reason, if x or y < 50, it gives an error. took me forever to figure this out
    x = max(x, 50)
    y = max(y, 50)
    img_crop = img[y - pad:y + h + pad, 
                   x - pad:x + w + pad]
    return img_crop

def save_img_array(img: np.ndarray, dst: str) -> None:
    '''useless code lmao, ima fix later, align args and pass'''
    out_img = Image.fromarray(img)
    out_img.save(dst)

def batch_transform(idir: str, func, *args, **kwargs) -> None:
    '''apply a function across a directory of images. not the most robust function ever mb'''
    ipaths = os.listdir(idir)
    ipaths = [os.path.join(idir, ipath) for ipath in ipaths]
    newdir = os.path.join(idir, func.__name__)
    os.makedirs(newdir, exist_ok = True)
    for ipath in ipaths:
        try:
            img = load_img_array(ipath)
            img = func(img, *args, **kwargs)
            outimg = Image.fromarray(img)
            outimg.save(os.path.join(newdir, ipath.split('/')[-1]))
        except UnidentifiedImageError:
            print(f'{ipath} not valid')
        except IsADirectoryError:
            pass

# https://rockyshikoku.medium.com/opencv-is-a-great-way-to-enhance-underexposed-overexposed-too-dark-and-too-bright-images-f79c57441a8a
def adjust_gamma(img: np.array, gamma: float = 1.0) -> np.array:
    # build lookup table mapping pixel values (0, 255) to adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array(
        [((i/255.0) ** invGamma) * 255 for i in np.arange(0, 256)]
    ).astype("uint8")
    
    return cv.LUT(img, table)



