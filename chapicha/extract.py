import itertools
import pprint
import sys
from operator import itemgetter


import cv2 as cv
import numpy as np
import pytesseract


from chapicha.util import TextShade, TextFlow, GroupDict


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


# TODO: Implement color extraction function


def range_key(val, increment=10):
    if val < 0:
        return 0
    else:
        xs = itertools.dropwhile(
            lambda x: x < val, itertools.count(0, increment)
        )
        return list(xs)[0]


def filterDivergent(iterable, factor=0.9):
    avg = sum([x[2] * x[3] for x in iterable]) / len(iterable)

    def filterfunc(val):
        val_avg = val[2] * val[3]
        return avg * (1 + factor) >= val_avg >= avg * (1 - factor)

    return filter(filterfunc, iterable)


def mergeBoundingBoxes(img, contours, flow=TextFlow.HORIZONTAL):
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


def extractText(
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


if __name__ == "__main__":
    print = pprint.pprint
    img = cv.imread(sys.argv[1])
    print(extractText(img))
    #  contours = findTextRegions(img, TextShade.DARK)
    #  merged = mergeBoundingBoxes(img, contours)
    #  showTextRegions(img, merged)
    #  boundingBoxes = [cv.boundingRect(c) for c in contours]
    #  d = GroupDict(filterDivergent(boundingBoxes))
    #  showGrouped(img, d)
