from dataclasses import dataclass, field
from collections import OrderedDict
from typing import Any, List, Optional
import numpy as np

@dataclass
class ImageData:
    """Container class to store image metadata"""

    image_id: str = ""
    thresh: Optional[np.ndarray] = None
    brs: List[Any] = field(default_factory=list)
    crop_indices: List[Any] = field(default_factory=list)
    padding: int = 50

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
