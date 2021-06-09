"""
CLI code, which allows the user to pass relative or absolute paths
"""

import os
import sys
from typing import Sequence, List, Callable, Optional

import click

from .core import Editable, ReorderEditableError


def absdirs(positionals: Sequence[str]) -> List[str]:
    """
    Convert all paths to abolsute paths, and make sure they all exist
    """
    res = []
    for pos in positionals:
        absfile = os.path.abspath(os.path.expanduser(pos))
        if not os.path.exists(absfile):
            click.echo(f"{absfile} does not exist", err=True)
            sys.exit(1)
        res.append(absfile)
    return res


@click.group()
def main() -> None:
    """
    Manage your editable packages - your easy-install.pth file
    """


def _resolve_editable() -> str:
    """
    Find the default easy-install.pth. Exits if a file couldn't be found
    """
    editable_pth: Optional[str] = Editable.locate_editable()
    if editable_pth is None:
        raise ReorderEditableError("Could not locate easy-install.pth")
    return editable_pth


def _print_editable_contents(
    stderr: bool = False, chosen_editable: Optional[str] = None
) -> None:
    """
    Opens the editable file directly and prints its contents
    """
    editable_pth: str
    if chosen_editable is not None:
        editable_pth = chosen_editable
    else:
        editable_pth = _resolve_editable()
    with open(editable_pth, "r") as src:
        click.echo(src.read(), nl=False, err=stderr)


@main.command(short_help="print easy-install.pth contents")
def cat() -> None:
    """
    Locate and print the contents of your easy-install.pth
    """
    try:
        _print_editable_contents()
    except ReorderEditableError as err:
        click.echo(str(err), err=True)
        sys.exit(1)


@main.command(short_help="print easy-install.pth file location")
def locate() -> None:
    """
    Try to find the easy-install.pth file, and print the location
    """
    try:
        click.echo(_resolve_editable())
    except ReorderEditableError as err:
        click.echo(str(err), err=True)
        sys.exit(1)


# shared click options/args between check/reorder
SHARED = [
    click.option(
        "-e",
        "--easy-install-location",
        "editable_pth",
        default=None,
        help="Manually provide path to easy-install.pth",
    ),
    click.argument("DIRECTORY", nargs=-1, required=True),
]


def shared(func: Callable[..., None]) -> Callable[..., None]:
    """
    Decorator to apply shared arguments to reorder/check
    """
    for decorator in SHARED:
        func = decorator(func)
    return func


@main.command(short_help="check easy-install.pth")
@shared
def check(editable_pth: Optional[str], directory: Sequence[str]) -> None:
    """
    If the order specified in your easy-install.pth doesn't match
    the order of the directories specified as positional arguments,
    exit with a non-zero exit code

    Also fails if one of the paths you provide doesn't exist

    \b
    e.g.
    reorder_editable check ./path/to/repo /another/path/to/repo

    In this case, ./path/to/repo should be above ./another/path/to/repo
    in your easy-install.pth file
    """
    dirs = absdirs(directory)
    try:
        Editable(location=editable_pth).assert_ordered(dirs)
    except ReorderEditableError as exc:
        click.echo("Error: " + str(exc))
        _print_editable_contents(stderr=True, chosen_editable=editable_pth)
        sys.exit(1)


@main.command(short_help="reorder easy-install.pth")
@shared
def reorder(editable_pth: Optional[str], directory: Sequence[str]) -> None:
    """
    If the order specified in your easy-install.pth doesn't match
    the order of the directories specified as positional arguments,
    reorder them so that it does. This always places items
    you're reordering at the end of your easy-install.pth so
    make sure to include all items you care about the order of

    Also fails if one of the paths you provide doesn't exist, or
    it isn't already in you easy-install.pth

    \b
    e.g.
    reorder_editable reorder ./path/to/repo /another/path/to/repo

    If ./path/to/repo was below /another/path/to/repo, this would
    reorder items in your config file to fix it so that ./path/to/repo
    is above /another/path/to/repo
    """
    dirs = absdirs(directory)
    try:
        Editable(location=editable_pth).reorder(dirs)
    except ReorderEditableError as exc:
        click.echo("Error: " + str(exc))
        _print_editable_contents(stderr=True, chosen_editable=editable_pth)
        sys.exit(1)


if __name__ == "__main__":
    main(prog_name="reorder_editable")
