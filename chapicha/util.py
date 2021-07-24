from enum import Enum
from pathlib import Path
from datetime import datetime
import re
from typing import List, Tuple, Optional
from itertools import repeat

import cv2
from rich.console import Console
import numpy as np

console = Console(color_system="truecolor")


class TextShade(Enum):
    LIGHT = 1
    DARK = 2


class TextFlow(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class MergeStrategy(Enum):
    NAIVE = 1
    INTELLIGENT = 2


class GroupDict(dict):
    """Custom dictionary that uses a user specified function to compute the
    key of values. The default function requires values to be iterables of
    a length of at least 2. increment is the distance between which values
    would hash to the same key.
    """
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


def get_timestamp():
    return int(datetime.utcnow().timestamp())


def read_image(path):
    """Read an image from a path including alpha channel if present"""
    if isinstance(path, Path):
        path = str(path)
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img.shape[-1] > 3:
        return img
    else:
        return cv2.imread(path, cv2.IMREAD_COLOR)


def save_image(image, base="out.jpg", prefix=get_timestamp()):
    """Write image to file using opencv to guess the correct format"""
    if image is not None:
        path = Path(base)
        outfile = f"{path.stem}{'-' if prefix else ''}{prefix}{path.suffix}"
        cv2.imwrite(outfile, image)
        return outfile
    return ""


def print_color(arr: np.ndarray) -> None:
    color = f"rgb({int(arr[0])},{int(arr[1])},{int(arr[2])})"
    console.print(
        "\u2588" * 5 + f" rgb({int(arr[0])},{int(arr[1])},{int(arr[2])})",
        style=color,
    )
    return


def separate_files(files: List[Path]) -> Tuple[List[Path], Optional[Path]]:
    maybe_input = files[:-1]
    maybe_output = files[-1]
    for f in maybe_input:
        if not f.exists():
            raise FileNotFoundError(f"{f} could not be found")
    else:
        if not maybe_output.exists():
            return (maybe_input, maybe_output)
        else:
            return (list(maybe_input) + [maybe_output], None)


def hex2rgb(hex_str):
    """Convert hex string to R, G, tuple"""
    h = re.compile(r"#?([a-f0-9]{2})([a-f0-9]{2})([a-f0-9]{2})")
    m = re.fullmatch(h, hex_str)
    def to_int(x): return int(x, 16)
    if m:
        colors = m.groups()
        if len(colors) == 3:
            return tuple(map(to_int, colors))
        elif len(colors) == 1:
            return tuple(map(to_int, repeat(colors[0], 3)))
    raise ValueError(f"Invalid string passed for hex color {hex_str}")
