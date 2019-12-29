from distutils.core import setup

from setuptools import find_packages

setup(
    name="TsingSpider",
    version=1.2,
    install_requires=[
        "requests",
        "BeautifulSoup4",
        "lxml"
    ],
    packages=find_packages(
        exclude=(
            "tsing_spider.test"
        )
    )
)
