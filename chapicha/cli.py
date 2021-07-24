import pathlib
import re

import click

from chapicha.util import (
    save_image,
    separate_files,
    print_color,
    hex2rgb,
    read_image,
)
import chapicha.transform as transform
import chapicha.extract as extract


@click.group()
@click.version_option()
@click.pass_context
@click.option("--verbose", default=False)
def cli(ctx, verbose):
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


def validate_dimensions(ctx, param, value):
    try:
        pat = re.compile(r"(?:(\d+)x(\d+)\+)?(\d+)x(\d+)")
        match = re.match(pat, value)
        return tuple(map(int, match.groups(default="0")))
    except ValueError:
        click.BadParameter("Invalid format for dimension specification")


# TODO: implement box select option
@cli.command()
@click.pass_context
@click.option(
    "-d",
    "--dimensions",
    required=True,
    type=click.UNPROCESSED,
    callback=validate_dimensions,
)
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
    if out_file is None:
        in_files, out_file = separate_files(files)
    else:
        in_files = files
    for path in in_files:
        img = read_image(path)
        x, y, w, h = dimensions
        output = transform.crop(img, x, y, w, h)
        if out_file is None:
            save_image(output, base=path, prefix="cropped")
        else:
            save_image(output, base=out_file, prefix="")


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
        img = read_image(path)
        output = transform.scale(img, factor)
        if out_file is None:
            save_image(output, base=path, prefix="scaled")
        else:
            save_image(output, base=out_file, prefix="")


@cli.command()
@click.pass_context
@click.option("-o", "--out-file", required=False)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
# TODO: add special output file handling code
def ocr(ctx, out_file, files):
    """Try and recognize text present in an image"""
    for file in files:
        img = read_image(file)
        result = extract.extract_text(img)
        print(file)
        for i in result:
            print(i)
    print("\n")


@cli.command()
@click.pass_context
@click.option("-n", "--number", required=True, type=int)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
# TODO: add special output file handling code
def color(ctx, count, files):
    """Find the most dominant colors in image"""
    for file in files:
        img = read_image(file)
        colors = extract.extract_colors(img, count)
        print(file)
        for i in colors:
            print_color(i)
    print("\n")


def validate_hex(ctx, param, value):
    try:
        v = hex2rgb(value)
        return v
    except ValueError:
        click.BadParameter("Invalid format")


@cli.command()
@click.pass_context
@click.option(
    "-c",
    "--color",
    required=False,
    type=click.UNPROCESSED,
    callback=validate_hex,
    default=None,
)
@click.option("-w", "--width", required=True, type=int, default=None)
@click.option("-h", "--height", required=True, type=int, default=None)
@click.option(
    "-o", "--out-file", required=False, default=None, type=pathlib.Path
)
@click.argument(
    "files",
    nargs=-1,
    required=True,
    type=pathlib.Path,
)
def pad(ctx, color, width, height, out_file, files):
    """Pad an image with a color to the given width and height"""
    if out_file is None:
        in_files, out_file = separate_files(files)
    else:
        in_files = files
    for path in in_files:
        img = read_image(path)
        output = transform.pad(img, color, width=width, height=height)
        if out_file is None:
            save_image(output, base=path, prefix="padded")
        else:
            save_image(output, base=out_file, prefix="")


def main():
    cli(obj={})
