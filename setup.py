#!/usr/bin/env python

from setuptools import setup, find_packages
from definition import infos


setup(name=infos['name'],
      version=infos['version'],
      description=infos['description'],
      author=infos['author'],
      author_email=infos['author_email'],
      url=infos['repository']['url'],
      packages=find_packages(),
     )
