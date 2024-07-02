from collections import OrderedDict
from typing import Any
import numpy as np

class ImageData(object):
    """Container class to store image metadata"""
    def __init__(self, thresh: np.ndarray = None, brs: list[Any] = None, idx: list[Any] = None, padding: int = 50):
        self.thresh = thresh
        self.brs = brs
        self.idx = idx
        self.padding = padding

    @property
    def _dict(self):
        return OrderedDict(
            [('thresholded_image', self.thresh),
             ('bounding_rects', self.brs),
             ('valid_indices', self.idx)]
        )