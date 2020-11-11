from distutils.core import setup

from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tsingspider",
    version="1.4.0",
    author="Tsing Jyujing",
    author_email="nigel434@gmail.com",
    description="A spider library of several data sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TsingJyujing/DataSpider",
    packages=find_packages(
        exclude=(
            "tsing_spider.test"
        )
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests",
        "BeautifulSoup4",
        "lxml",
        "pytz",
        "m3u8"
    ],
)
