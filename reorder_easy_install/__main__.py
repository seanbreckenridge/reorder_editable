import os
import sys
from typing import Sequence, List, Callable, Optional
from types import FunctionType

import click

from .core import EasyInstallFile, ReorderEasyInstallError


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
    pass


def _print_easy_install_contents(stderr: bool = False) -> None:
    click.echo(EasyInstallFile().location.read_text(), nl=False, err=stderr)


@main.command()
def cat() -> None:
    """
    Locate and print the contents of your easy-install.pth
    """
    try:
        _print_easy_install_contents()
    except ReorderEasyInstallError as e:
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
    reorder_easy_install ./path/to/repo /another/path/to/repo

    In this case, ./path/to/repo should be above ./another/path/to/repo
    in your easy-install.pth file
    """
    dirs = _validate_positionals(directory)
    try:
        EasyInstallFile(ei).is_ordered(_validate_positionals(directory))
    except ReorderEasyInstallError as exc:
        click.echo("Error: " + str(exc))
        _print_easy_install_contents(stderr=True)
        sys.exit(1)


@main.command()
@shared
def reorder(ei: Optional[str], directory: Sequence[str]) -> None:
    dirs = _validate_positionals(directory)
    exc = EasyInstallFile(ei).is_ordered(_validate_positionals(directory))


if __name__ == "__main__":
    main(prog_name="reorder_easy_install")
