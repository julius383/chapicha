from enum import Enum
from pathlib import Path
from datetime import datetime
import cv2 as cv


class TextShade(Enum):
    LIGHT = 1
    DARK = 2


class TextFlow(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class GroupDict(dict):
    def __init__(self, iterable, increment=20, key=lambda x: x[1] + x[3]):
        self._dict = {}
        self.increment = increment
        for i in iterable:
            if key(i) in self._dict:
                self._dict[key(i)] = self._dict[key(i)] + [i]
            else:
                for k, _ in self._dict.items():
                    if abs(k - key(i)) <= self.increment:
                        self._dict[k] = self._dict[k] + [i]
                        break
                else:
                    self._dict[key(i)] = [i]

    def __setitem__(self, key, item):
        for k, _ in self._dict.items():
            if abs(k - key) <= self.increment:
                self._dict[k] = self._dict[k] + [item]
                break
        else:
            self._dict[key] = [item]

    def __getitem__(self, key):
        for k, _ in self._dict.items():
            if abs(k - key) <= self.increment:
                return self._dict[k]
        else:
            raise KeyError

    def __repr__(self):
        return repr(self._dict)

    def __len__(self):
        return len(self._dict)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()


def getTimestamp():
    return int(datetime.utcnow().timestamp())


def saveImage(image, base="out.jpg", prefix=getTimestamp()):
    if image is not None:
        path = Path(base)
        outfile = f"{path.stem}{'-' if prefix else ''}{prefix}{path.suffix}"
        cv.imwrite(outfile, image)
        return outfile
    return ""
