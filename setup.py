from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="graphcat",
    version="1.0.0",
    author="zblurx, nevasec",
    description="Generate graphs and charts on password cracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WodenSec/graphcat-ng",
    license="MIT",
    install_requires=[
        "matplotlib==3.6.2",
        "Jinja2==3.1.2",
        "numpy<2"
    ],
    python_requires='>=3.6',
    py_modules=["graphcat"],
    entry_points={
        "console_scripts": [
            "graphcat=graphcat:main"
        ]
    },
    include_package_data=True,
)
