import os
import sys
from typing import Sequence, List, Callable, Optional
from types import FunctionType

import click

from .core import Editable, ReorderEditableError


def _validate_positionals(pos: Sequence[str]) -> List[str]:
    """
    Convert all paths to abolsute paths, and make sure they all exist
    """
    res = []
    for p in pos:
        absfile = os.path.abspath(os.path.expanduser(p))
        if not os.path.exists(absfile):
            click.echo(f"{absfile} does not exist", err=True)
            sys.exit(1)
        res.append(absfile)
    return res


@click.group()
def main() -> None:
    """
    Manage your editable namespace packages - your easy-install.pth file
    """
    pass


def _print_editable_contents(stderr: bool = False) -> None:
    click.echo(Editable().location.read_text(), nl=False, err=stderr)


@main.command(short_help="print easy-install.pth contents")
def cat() -> None:
    """
    Locate and print the contents of your easy-install.pth
    """
    try:
        _print_editable_contents()
    except ReorderEditableError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


# shared click options/args between check/reorder
SHARED = [
    click.option(
        "-e",
        "--easy-install-location",
        "ei",
        default=None,
        help="Manually provide path to easy-install.pth",
    ),
    click.argument("DIRECTORY", nargs=-1, required=True),
]


# decorator to apply arguments
def shared(func: Callable[..., None]) -> Callable[..., None]:
    for s in SHARED:
        func = s(func)
    return func


@main.command(short_help="check easy-install.pth")
@shared
def check(ei: Optional[str], directory: Sequence[str]) -> None:
    """
    If the order specified in your easy-install.pth doesn't match
    the location of the directories specified as positional arguments,
    exit with a non-zero exit code

    Also fails if one of the paths you provide doesn't exist

    \b
    e.g.
    reorder_editable ./path/to/repo /another/path/to/repo

    In this case, ./path/to/repo should be above ./another/path/to/repo
    in your easy-install.pth file
    """
    dirs = _validate_positionals(directory)
    try:
        Editable(ei).assert_ordered(dirs)
    except ReorderEditableError as exc:
        click.echo("Error: " + str(exc))
        _print_editable_contents(stderr=True)
        sys.exit(1)


@main.command()
@shared
def reorder(ei: Optional[str], directory: Sequence[str]) -> None:
    dirs = _validate_positionals(directory)
    try:
        Editable(ei).reorder(dirs)
    except ReorderEditableError as exc:
        click.echo("Error: " + str(exc))
        _print_editable_contents(stderr=True)
        sys.exit(1)


if __name__ == "__main__":
    main(prog_name="reorder_editable")
