from ImageSegmenter import ImageSegmenter
import numpy as np
import cv2 as cv
import scipy.ndimage as ndimage

from shortcuts.imgutil import split_channels, erode

def generate_thresholded_image(image: np.ndarray) -> tuple[np.ndarray, list]:
    iseg = ImageSegmenter()
    r, g, b = split_channels(image)

    b = erode(b, iterations = 2) # run on blue channel; erode to reduce noise
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(4,4)) # enhance contrast
    b = clahe.apply(b[:,:,2])

    t = iseg._threshold_image(b, k = 4, lightbg = 'auto', darkbg = 'auto')
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
        brs.append((x, y, w, h))

    blank = image.copy()
    for n, rect in enumerate(brs):
        x, y, w, h = rect
        cv.rectangle(blank, (x, y), (x + w, y + h), (255, 255, 0), 2)

    return blank, brs


def crop_rect(img: np.ndarray, rect: tuple[int, int, int, int], pad: int = 50) -> np.ndarray:
    '''simple function to return an image cropped according to a rectangle. padding is in pixels'''
    x, y, w, h = rect
    img_crop = img[y - pad:y + h + pad,
                   x - pad:x + w + pad]
    return img_crop

def get_cropped_images(source_image: np.ndarray, valid_idx: list[int], brs: list[tuple[int, int, int, int]]) -> list[np.ndarray]:
    # this function here should take args:
    # source_image: the un-processed image that should be cropped
    # valid_idx: list of valid indices
    # brs: list[tuple[int, int, int, int]] aka the bounding rectangles to crop by, same index
    # this should return out_rects

    valid_rects = [brs[n] for n in valid_idx]
    return [crop_rect(source_image, rect) for rect in valid_rects]


class INeedToMakeThisIntoAFunctionAndThisIsSoIDontGetErrors:
    img = np.ndarray([1])
    VALID_INDICES = []
    brs = [(1,1,1,1)]
    img_name = None

    # this image will be cropped
    blank2 = img.copy()
    valid_rects = [brs[n] for n in VALID_INDICES]  # only take the indices that are confirmed valid

    # make a list of all the cropped sections
    out_rects = [crop_rect(blank2, rect) for rect in valid_rects]


    # DO NOT INCLUDE THE PLOTTING CODE: idk how i can implement this into GUI
    # plot them. images should be in order from left to right as long as the indices specified above are in the same order as on the picture.
    # f, ax = plt.subplots(1, len(VALID_INDICES), figsize=(40, 10))
    # for i, o in enumerate(out_rects):
    #     o = cv.rotate(o, cv.ROTATE_90_CLOCKWISE)
    #     ax[i].imshow(o)
    #
    # f.suptitle(img_name)
    # don't know why the spacing is so annoying and i don't feel like fixing it

    # TODO:
    # this will be more complex for 2 row slide conventions. i'm not sure how to best handle that.
    # f.savefig() into directory named after the original image.
    # ipath.split('/')[-1].split('.')[0] -- get the filename and take out the extension and use this as folder nmae?