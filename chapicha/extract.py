import itertools
from operator import itemgetter


import cv2 as cv
import numpy as np
import pytesseract


from chapicha.util import TextShade, TextFlow, GroupDict
from chapicha.transform import scale


MAX_AREA = 1000000


# FIXME: FInd a bettern way to detect text in image
def findTextRegions(img: np.ndarray, text_color: TextShade = TextShade.DARK):
    if text_color == TextShade.LIGHT:
        thresh = cv.THRESH_BINARY
    else:
        thresh = cv.THRESH_BINARY_INV

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 180, 255, thresh)

    kernel = np.ones((7, 7), np.uint8)
    morph = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)
    morph = cv.morphologyEx(morph, cv.MORPH_OPEN, kernel)

    contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    return contours


def showTextRegions(img, contours):
    disp = img.copy()
    for rect in contours:
        #  rect = cv.boundingRect(c)
        x, y, w, h = rect
        cv.rectangle(disp, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv.imshow("Frame", disp)
    while "q" != chr(cv.waitKey() & 255):
        pass
    cv.destroyAllWindows()


def showGrouped(img, grouped):
    disp = img.copy()
    colors = itertools.cycle([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    for k, group in grouped.items():
        c = next(colors)
        for rect in group:
            #  rect = cv.boundingRect(c)
            x, y, w, h = rect
            cv.rectangle(disp, (x, y), (x + w, y + h), c, 2)
    cv.imshow("Frame", disp)
    while "q" != chr(cv.waitKey() & 255):
        pass
    cv.destroyAllWindows()


def filterDivergent(iterable, factor=0.9):
    """Filter out bounding boxes that are unlikely to contain text."""
    avg = sum([x[2] * x[3] for x in iterable]) / len(iterable)

    def filterfunc(val):
        val_avg = val[2] * val[3]
        return avg * (1 + factor) >= val_avg >= avg * (1 - factor)

    return filter(filterfunc, iterable)


def mergeBoundingBoxes(img, contours, flow=TextFlow.HORIZONTAL):
    """Reduce the number of bounding boxes by merging adjacent ones."""
    CLOSENESS = 20
    boundingBoxes = [cv.boundingRect(c) for c in contours]
    grouped = GroupDict(filterDivergent(boundingBoxes), CLOSENESS)
    merged = []
    #  print(f"{grouped=}")
    for k, v in grouped.items():
        new_x, _, _, _ = min(v, key=itemgetter(0))
        _, new_y, _, _ = min(v, key=itemgetter(1))
        max_x = max(map(lambda x: x[0] + x[2], v))
        max_y = max(map(lambda x: x[1] + x[3], v))
        merged.append((new_x, new_y, max_x - new_x, max_y - new_y))

    #  print(f"{merged=}")
    return merged


def extract_text(
    img, text_color=TextShade.LIGHT, text_flow=TextFlow.HORIZONTAL
):
    contours = findTextRegions(img, TextShade.DARK)
    merged = mergeBoundingBoxes(img, contours)
    config = "-l eng --oem 3 --psm 7"
    text = []
    for rect in merged:
        (x, y, w, h) = rect
        x1, y1 = x + w, y + h
        roi = img[y:y1, x:x1, :]
        maybe_text = pytesseract.image_to_string(roi, config=config)
        if maybe_text:
            text.append(maybe_text)
    return list(reversed(text))


def sort_split(arr):
    """Auxiliary function for median_cut that sorts and splits buckets."""
    _, _, cols = arr.shape
    max_channel = 0
    max_diff = -1
    for c in range(cols):
        diff = np.ptp(arr[:, :, c])
        if diff > max_diff:
            max_diff = diff
            max_channel = c
    # sort 3D array with 'key' being max_channel
    sorted_arr = np.einsum(
        "iijk->ijk", arr[:, arr[:, :, max_channel].argsort()]
    )
    return np.array_split(sorted_arr, 2, axis=1)


def median_cut(img, colors=4):
    """MedianCut algorithm uses average for bucket aggregation."""
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    w, h, _ = img.shape
    if (area := w * h) >= MAX_AREA:  # arbitrary value to trigger image resize
        factor = area // MAX_AREA
        img = scale(img, factor=factor)
    buckets = [img]
    while len(buckets) < colors:
        new_buckets = []
        for b in buckets:
            new_buckets.extend(sort_split(b))
        buckets = new_buckets
    result = []
    for b in buckets:
        w, h, cols = b.shape
        color = np.reshape(b, (w * h, 1, cols))
        avg = np.rint(np.average(color, axis=0))
        result.append(np.reshape(avg, (3, 1)))
    return result
