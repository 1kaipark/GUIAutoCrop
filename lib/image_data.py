from collections import OrderedDict
from typing import Any
import numpy as np


class ImageData(object):
    """Container class to store image metadata"""

    def __init__(
        self,
        image_id: str = "",
        thresh: np.ndarray = None,
        brs: list[Any] = None,
        crop_indices: list[Any] = None,
        padding: int = 50,
    ):
        self.image_id = image_id
        self.thresh = thresh
        self.brs = brs
        self.crop_indices = crop_indices
        self.padding = padding

    @property
    def _dict(self) -> OrderedDict:
        return OrderedDict(
            [
                ("image_id", self.image_id),
                ("thresh", self.thresh),
                ("brs", self.brs),
                ("crop_indices", self.crop_indices),
                ("padding", self.padding),
            ]
        )

    def __getitem__(self, item) -> Any:
        return self._dict[item]

    def __repr__(self):
        return f"ImageData({[item for item in self._dict.items()]})"

    def __str__(self):
        return self.__repr__
