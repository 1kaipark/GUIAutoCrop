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
            [('thresh', self.thresh),
             ('brs', self.brs),
             ('idx', self.idx),
             ('padding', self.padding)]
        )
    def __getitem__(self, item):
        return self._dict[item]
    
    def __setitem__(self, *args, **kwargs):
        raise Exception('Assign to attributes instead of item assignment.')
    
    def __str__(self):
        return f"ImageData({[item for item in self._dict.items()]})"
    
    def __repr__(self):
        return f"ImageData({[item for item in self._dict.items()]})"