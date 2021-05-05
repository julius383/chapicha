import numpy as np
import cv2 as cv


def crop(
    img: np.ndarray, x: int = 0, y: int = 0, width: int = 50, height: int = 50
) -> np.ndarray:
    (image_height, image_width) = img.shape[:2]
    print(f"{image_height=} {image_width=}")
    if width == height == 0:
        return img
    if (x + width <= image_width) and (y + height <= image_height):
        return img[y:y+height, x:x+width, :].copy()


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
    scaled = cv.resize(img, dimensions, interpolation=cv.INTER_CUBIC)
    return scaled
