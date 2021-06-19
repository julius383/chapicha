import pathlib
import re

import click
import cv2 as cv

from chapicha.util import save_image, separate_files, print_color
import chapicha.transform as transform
import chapicha.extract as extract


@click.group()
@click.version_option()
@click.pass_context
@click.option("--verbose", default=False)
def cli(ctx, verbose):
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


# TODO: implement box select option
@cli.command()
@click.pass_context
@click.option("-d", "--dimensions", required=True)
@click.option(
    "-o", "--out-file", required=False, default=None, type=pathlib.Path
)
@click.argument(
    "files",
    nargs=-1,
    type=pathlib.Path,
    required=True,
)
def crop(ctx, dimensions, out_file, files):
    """Crop images to given dimensions"""
    pat = re.compile(r"(?:(\d+)x(\d+)\+)?(\d+)x(\d+)")
    try:
        match = re.match(pat, dimensions)
        x, y, w, h = match.groups(default="0")
        if out_file is None:
            in_files, out_file = separate_files(files)
        else:
            in_files = files
        for path in in_files:
            img = cv.imread(str(path))
            output = transform.crop(img, int(x), int(y), int(w), int(h))
            if out_file is None:
                save_image(output, base=path, prefix="cropped")
            else:
                save_image(output, base=out_file, prefix="")

    except (ValueError, AttributeError):
        click.echo("Invalid dimension specification")
        return


@cli.command()
@click.pass_context
@click.option("-f", "--factor", required=True, type=float)
@click.option(
    "-o", "--out-file", required=False, default=None, type=pathlib.Path
)
@click.argument(
    "files",
    nargs=-1,
    required=True,
    type=pathlib.Path,
)
def scale(ctx, factor, out_file, files):
    """Scale down an image by a given factor"""
    if out_file is None:
        in_files, out_file = separate_files(files)
    else:
        in_files = files
    for path in in_files:
        img = cv.imread(str(path))
        output = transform.scale(img, factor)
        if out_file is None:
            save_image(output, base=path, prefix="scaled")
        else:
            save_image(output, base=out_file, prefix="")


@cli.command()
@click.pass_context
@click.option("-o", "--out-file", required=False)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def ocr(ctx, out_file, files):
    """Try and recognize text present in an image"""
    for file in files:
        img = cv.imread(file)
        result = extract.extract_text(img)
        print(file)
        for i in result:
            print(i)
    print("\n")


@cli.command()
@click.pass_context
@click.option("-c", "--count", required=True)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def color(ctx, count, files):
    for file in files:
        img = cv.imread(file)
        colors = extract.median_cut(img)
        print(file)
        for i in colors:
            print_color(i)
    print("\n")


def main():
    cli(obj={})
