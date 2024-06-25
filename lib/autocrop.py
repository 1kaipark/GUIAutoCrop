from .ImageSegmenter import ImageSegmenter
import numpy as np
import cv2 as cv
import scipy.ndimage as ndimage

from .imgutil import split_channels, erode

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
    '''simple function to return an image cropped according to a rectangle. padding is in pixels'''
    x1, y1, x2, y2 = rect
    img_crop = img[y1:y2,
                   x1:x2]
    return img_crop

def get_cropped_images(source_image: np.ndarray, valid_idx: list[int], brs: list[tuple[int, int, int, int]], pad: int = 50) -> list[np.ndarray]:
    # this function here should take args:
    # source_image: the un-processed image that should be cropped
    # valid_idx: list of valid indices
    # brs: list[tuple[int, int, int, int]] aka the bounding rectangles to crop by, same index
    # this should return out_rects

    valid_rects = [brs[n] for n in valid_idx]
    return [crop_rect(source_image, rect) for rect in valid_rects]


