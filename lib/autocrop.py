from .ImageSegmenter import ImageSegmenter
import numpy as np
import cv2 as cv
import scipy.ndimage as ndimage
from PIL import Image

def load_img_array(ipath: str) -> np.ndarray:
    """Load image as a numpy ndarray"""
    return np.asarray(Image.open(ipath)) # use PIL to open, then return the array 

def split_channels(img: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """returns red, green, blue channels from given RGB image array"""
    r, g, b = img[:,:,0], img[:,:,1], img[:,:,2] # split channels, output grayscale
    # return RGB images
    zero = np.zeros(img.shape[0:2], np.uint8)  # zero array w same shape as image, must be 8-bit unsigned int
    red_ch = cv.merge([r, zero, zero])
    green_ch = cv.merge([zero, g, zero])
    blue_ch = cv.merge([zero, zero, b])
    return red_ch, green_ch, blue_ch

def erode(img: np.ndarray, iterations: int = 2, kernel_size: int = 3) -> np.ndarray:
    """applies erosion according to the specified parameters"""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    img = cv.erode(img, kernel, iterations = iterations, anchor = (1, 1))
    return img

def dilate(img: np.ndarray, iterations: int = 2, kernel_size: int = 3) -> np.ndarray:
    """applies erosion according to the specified parameters"""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    img = cv.dilate(img, kernel, iterations = iterations, anchor = (1, 1))
    return img 

def generate_thresholded_image(image: np.ndarray, k: int = 4, pad: int = 50) -> tuple[np.ndarray, list]:
    """takes args image: the image to be thresholded,
    k: modulates threshold intensity for calculation of contours,
    pad: padding to add to the rectangles"""
    iseg = ImageSegmenter()
    r, g, b = split_channels(image)

    # b = erode(b, iterations = 2) # run on blue channel; erode to reduce noise
    clahe = cv.createCLAHE(clipLimit=1.0, tileGridSize=(4,4)) # enhance contrast
    b = clahe.apply(b[:,:,2])

    t = iseg._threshold_image(b, k = k, lightbg = 'auto', darkbg = 'auto')
    t = ImageSegmenter._image_dilation(t)
    t = ImageSegmenter._noise_reduction(t)
    t = ndimage.binary_fill_holes(t.astype(int))


    # get contours:
    contours, hierarchy = cv.findContours(
        image=t.astype(np.uint8),
        mode=cv.RETR_TREE,
        method=cv.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv.contourArea, reverse=True)[:10]
    approx_ctrs = []
    for cnt in contours:
        hull = cv.convexHull(cnt)
        approx_ctrs.append(hull)

    # draw bounding rectangles using cv.boundingRect around the convex hulls
    brs = []
    for contour in approx_ctrs:
        x, y, w, h = cv.boundingRect(contour)
        brs.append((x-pad, y-pad, x+w+pad, y+h+pad))

    blank = image.copy()
    for n, rect in enumerate(brs):
        x1, y1, x2, y2 = rect
        cv.rectangle(blank, (x1, y1), (x2, y2), (255, 255, 0), 2)

    return blank, brs


def crop_rect(img: np.ndarray, rect: tuple[int, int, int, int]) -> np.ndarray:
    """simple function to return an image cropped according to a rectangle. padding is in pixels"""
    x1, y1, x2, y2 = rect
    img_crop = img[y1:y2,
                   x1:x2]
    return img_crop

def get_cropped_images(source_image: np.ndarray, valid_idx: list[int], brs: list[tuple[int, int, int, int]], pad: int = 50) -> list[np.ndarray]:
    """Crops image according to valid indices of bounding rects"""
    valid_rects = [brs[n] for n in valid_idx]
    return [crop_rect(source_image, rect) for rect in valid_rects]


