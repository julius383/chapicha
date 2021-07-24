from math import floor, ceil

import numpy as np
import cv2


def crop(
    img: np.ndarray, x: int = 0, y: int = 0, width: int = 50, height: int = 50
) -> np.ndarray:
    (image_height, image_width) = img.shape[:2]
    print(f"{image_height=} {image_width=}")
    if width == height == 0:
        return img
    if (x + width <= image_width) and (y + height <= image_height):
        return img[y: y + height, x : x + width, :].copy()


# TODO: Implement stitch function


def scale(img: np.ndarray, factor=None, width=None, height=None) -> np.ndarray:
    if factor is not None and factor <= 0:
        return img
    (image_height, image_width) = img.shape[:2]
    if factor is None:
        if width is None:
            factor = height / float(image_height)
            dimensions = (int(image_width * factor), height)
        else:
            factor = width / float(image_width)
            dimensions = (width, int(height * factor))
    else:
        dimensions = int(image_width // factor), int(image_height // factor)
    scaled = cv2.resize(img, dimensions, interpolation=cv2.INTER_CUBIC)
    return scaled


# TODO: validate input width and height greater than image width and height
def pad(img, color=(0, 0, 0), aspect_ratio=None, width=None, height=None):
    (image_height, image_width, depth) = img.shape
    color = tuple(reversed(color))

    # https://stackoverflow.com/a/53737420
    # fill transparent areas with chosen color
    print(depth)
    if depth > 3:
        trans_mask = img[:, :, 3] == 0
        img[trans_mask] = [*color, 255]
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    width_padding = (0, 0)
    height_padding = (0, 0)
    if width is not None:
        padding = (width - image_width) / 2
        print(padding, image_width, width)
        width_padding = (floor(padding), ceil(padding))
    if height is not None:
        padding = (height - image_height) / 2
        height_padding = (floor(padding), ceil(padding))
    if color is None:
        layers = []
        for i in range(depth):
            arr = np.pad(
                img[:, :, i],
                (height_padding, width_padding),
                "constant",
                constant_values=color[i])
            layers.append(arr)
        return np.dstack(tuple(layers))
    else:
        return np.pad(img, (height_padding, width_padding, (0, 0)), 'edge')
