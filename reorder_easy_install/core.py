import warnings
from pathlib import Path
from typing import Optional, List


class ReorderEasyInstallError(FileNotFoundError):
    pass


class EasyInstallFile:
    def __init__(self, location: Optional[str] = None):
        if location is None:
            ei = self.__class__.locate_easy_install()
            if ei is not None:
                self.location = Path(ei)
            else:
                raise ReorderEasyInstallError(
                    "Could not locate the easy-install.pth file"
                )
        else:
            self.location = Path(location)

        assert (
            self.location.exists()
        ), f"The easy-install.pth file at '{self.location}' doesn't exist"
        self.lines: List[str] = self.location.read_text().splitlines()

    # returns None on success, an Error if the file is not ordered correctly
    def is_ordered(self, expected: List[str]) -> Optional[Exception]:
        # iterated through all the items in the easy-install.pth file
        # but 'i' didn't reach the end of the list of expected items
        left = self.find_unordered(expected)
        if left:
            emsg = f"Reached the end of the easy-install.pth, but did not encounter '{left}' in the correct order"
            raise ReorderEasyInstallError(emsg)
        return None

    def find_unordered(self, expected: List[str]) -> List[str]:
        """
        Given a list of files in an expected order, compares that against
        the read order from the easy-install.pth file

        expected should be the absolute path of directories
        provided by the user
        """
        if len(expected) == 0:
            return expected
        i = 0  # current index of the expected items
        for path in self.lines:
            # use os.stat instead?
            if path == expected[i]:
                i += 1
                if len(expected) == i:
                    break

        return expected[i:]

    # Hmm.. is there some reason to use the 'site' module to try
    # and inspect the globally defined site-packages directories
    # for a possible easy-install.pth file?
    # you probably wouldn't have installed a package there nor
    # have permission to edit that without sudo, which is not
    # what this is for
    # see https://stackoverflow.com/a/46071447/9348376

    @staticmethod
    def locate_easy_install() -> Optional[Path]:
        """"""
        # try to find an easy install path or the user site-packages
        p = Path(__file__)
        site_packages_dir = p.parent.parent
        if site_packages_dir.name != "site-packages":
            warnings.warn(
                f"Warning: expected '{site_packages_dir}' to be named 'site-packages'",
            )
        easy_install = site_packages_dir / "easy-install.pth"
        if not easy_install.exists():
            return None
        return easy_install
