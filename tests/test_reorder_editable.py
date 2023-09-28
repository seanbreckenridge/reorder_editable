import os
from pathlib import Path
import tempfile

import pytest
from reorder_editable.core import Editable, ReorderEditableError

this_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(this_dir)

broken = os.path.join(this_dir, "broken.pth")
fixed = os.path.join(this_dir, "fixed.pth")

broken_contents = Path(broken).read_text()
fixed_contents = Path(fixed).read_text()


def test_reorder() -> None:
    # test using pure function
    e = Editable(location=broken)
    lines = e.find_unordered(["fixed.pth", "broken.pth"])
    assert lines == ["broken.pth"]

    # write to a temporary file, reorder it
    with tempfile.NamedTemporaryFile() as tf:
        Path(tf.name).write_text(broken_contents)
        e = Editable(location=tf.name)
        did_reorder = e.reorder(["fixed.pth", "broken.pth"])
        assert did_reorder is True
        assert Path(tf.name).read_text().strip() == fixed_contents.strip()


def test_editable_works_with_no_argss() -> None:
    # regression test
    # is fine if this raises a ReorderEditableError,
    # just dont want it to TypeError
    try:
        Editable()
    except ReorderEditableError:
        pass


if __name__ == "__main__":
    pytest.main()
