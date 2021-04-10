from pathlib import Path
from setuptools import setup

long_description = Path("README.md").read_text()
reqs = Path("requirements.txt").read_text().strip().splitlines()

pkg = "reorder_editable"
setup(
    name=pkg,
    version="0.1.0",
    url="https://github.com/seanbreckenridge/reorder_editable",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=("""naive implementation to reorder my easy-install.pth file"""),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=["reorder_editable"],
    install_requires=reqs,
    package_data={pkg: ["py.typed"]},
    zip_safe=False,
    keywords="",
    entry_points={
        "console_scripts": ["reorder_editable = reorder_editable.__main__:main"]
    },
    extras_require={
        "testing": [
            "pytest",
            "mypy",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
