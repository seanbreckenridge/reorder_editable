import site
from pathlib import Path
from typing import Optional, List, Tuple


class ReorderEditableError(FileNotFoundError):
    pass


class Editable:
    def __init__(self, location: Optional[str] = None):
        if location is None:
            ei = self.__class__.locate_editable()
            if ei is not None:
                self.location = Path(ei)
            else:
                raise ReorderEditableError("Could not locate easy-install.pth")
        else:
            self.location = Path(location)

        assert (
            self.location.exists()
        ), f"The easy-install.pth file at '{self.location}' doesn't exist"
        self.lines: List[str] = self.read_lines()

    def read_lines(self) -> List[str]:
        self.lines = self.location.read_text().splitlines()
        return self.lines

    # returns None on success, an Error if the file is not ordered correctly
    def assert_ordered(self, expected: List[str]) -> None:
        # iterated through all the items in the easy-install.pth file
        # but 'i' didn't reach the end of the list of expected items
        left = self.find_unordered(expected)
        if left:
            raise ReorderEditableError(
                f"Reached the end of the easy-install.pth, but did not encounter '{left}' in the correct order"
            )

    def find_unordered(self, expected: List[str]) -> List[str]:
        """
        Given a list of files in an expected order, compares that against
        the read order from the easy-install.pth file

        Returns any items not found in the correct order by the
        time it reaches the end of the easy-install.pth

        expected should be the absolute path of directories
        provided by the user
        """
        return self.__class__.find_unordered_pure(self.lines, expected)

    @staticmethod
    def find_unordered_pure(lines: List[str], expected: List[str]) -> List[str]:
        """
        Pure function encapsulating all the logic for find_unordered
        """

        if len(expected) == 0:
            return expected
        i = 0  # current index of the expected items
        for path in lines:
            # use os.stat instead?
            if path == expected[i]:
                i += 1
                if len(expected) == i:
                    break

        return expected[i:]

    def reorder(self, expected: List[str]) -> bool:
        """
        If needed, reorder the easy-install.pth

        If the user specifies an item which doesn't exist in the
        easy-install.pth, this throws an error, since it has
        no way to determine where that value should go

        Return value is True if the file was edited, False
        if it didn't need to be edited.
        """
        do_reorder, new_lines = self.reorder_mem(expected)
        if do_reorder is False:
            return False
        # write new_lines to file
        with open(self.location, "w") as ef:
            for line in new_lines:
                ef.write(f"{line}\n")
        return True

    def reorder_mem(self, expected: List[str]) -> Tuple[bool, List[str]]:
        return self.__class__.reorder_mem_pure(self.lines, expected)

    @classmethod
    def reorder_mem_pure(
        cls, lines: List[str], expected: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Pure function encapsulating all the logic for reordering
        Returns (whether or not to edit the file, resulting changes)
        """
        unordered: List[str] = cls.find_unordered_pure(lines, expected)
        # everything is ordered right, dont need to do anything!
        if len(unordered) == 0:
            return False, lines

        # check that expected is a subset of lines
        expected_set = set(expected)
        lines_set = set(lines)
        if not expected_set.issubset(lines_set):
            raise ReorderEditableError(
                f"Provided one or more value(s) which don't appear in the easy-install.pth: {expected_set - lines_set}"
            )

        result: List[str] = []

        # add anything in lines but not in expected
        for path in lines:
            if path not in expected_set:
                result.append(path)

        # add anything in expected, in the order the user specified
        for path in expected:
            assert path in lines_set
            result.append(path)

        # sanity check
        assert len(result) == len(lines)

        # if an item isn't mentioned in expected, leave it in the same
        # order -- extract all items not mentioned

        return True, result

    @staticmethod
    def locate_editable() -> Optional[Path]:
        # try to find an editable install path in the user site-packages
        site_packages_dir = site.getusersitepackages()
        editable_packages = Path(site_packages_dir) / "easy-install.pth"
        if not editable_packages.exists():
            return None
        return editable_packages
