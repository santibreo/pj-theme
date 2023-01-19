#!/usr/bin/env python

import codecs
from setuptools import setup
from pj_theme import __version__ as version

# README into long description
#with codecs.open("README.rst", encoding="utf-8") as f:
#    readme = f.read()
readme = ""

code_ns = "santibreo/pj-theme"

setup(
    name="pj_theme",
    version=version,
    description="Sphinx theme for personal blogging site",
    long_description=readme,
    author="Santiago B. Pérez Pita",
    author_email="santibreo@gmail.com",
    url="https://santibreo.github.io/pj-site/index.html",
    #project_urls={
    #    "Source": f"https://github.com/{code_ns}",
    #    "Changelog": f"https://github.com/{code_ns}/blob/main/docs/changelog.rst",  # noqa
    #    "CI": f"https://app.circleci.com/pipelines/github/{code_ns}",
    #},
    packages=["pj_theme"],
    include_package_data=True,
    entry_points={"sphinx.html_themes": ["sphinx-pjtheme=pj_theme"]},
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
)
