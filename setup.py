from distutils.core import setup

from setuptools import find_packages

setup(
    name="TsingSpider",
    version="1.3",
    python_requires='>=3.7',
    install_requires=[
        "requests[socks]",
        "BeautifulSoup4",
        "lxml",
        "pytz",
    ],
    packages=find_packages(
        exclude=(
            "tsing_spider.test"
        )
    )
)
