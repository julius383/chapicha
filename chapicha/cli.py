from pathlib import Path
from typing import List
import re

import click
import cv2 as cv

from chapicha.util import saveImage
import chapicha.transform
import chapicha.extract


@click.group()
@click.pass_context
@click.option("--verbose", default=False)
def cli(ctx, verbose):
    ctx.ensure_object(dict)

    ctx.obj["verbose"] = verbose


# FIXME: swap out PIL file handling for OpenCV
# TODO: implement box select option
@cli.command()
@click.pass_context
@click.option("-d", "--dimensions", required=True)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def crop(ctx, dimensions, files):
    """Crop images to given dimensions"""
    pat = re.compile(r"(?:(\d+)x(\d+)\+)?(\d+)x(\d+)")
    try:
        match = re.match(pat, dimensions)
        x, y, w, h = match.groups(default='0')
        paths: List[Path] = [Path(x) for x in files]
        for path in paths:
            img = cv.imread(str(path))
            output = transform.crop(img, int(x), int(y), int(w), int(h))
            saveImage(output, base=path, prefix='cropped')

    except (ValueError, AttributeError):
        click.echo("Invalid dimension specification")
        return


@cli.command()
@click.pass_context
@click.option("-f", "--factor", required=True, type=float)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def scale(ctx, factor, files):
    """Scale down an image by a given factor"""
    paths: List[Path] = [Path(x) for x in files]
    for path in paths:
        img = cv.imread(str(path))
        output = transform.scale(img, factor)
        saveImage(output, base=path, prefix='cropped')


@cli.command()
@click.pass_context
@click.option("-o", "--out-file", required=False)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def ocr(ctx, out_file, files):
    """Try and recognize text present in an image"""
    for file in files:
        img = cv.imread(file)
        result = extract.extractText(img)
        print(file)
        for i in result:
            print(i)
    print("\n")


def main():
    cli(obj={})
