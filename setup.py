#!/usr/bin/env python
from setuptools import setup, find_packages

from bruker2nifti._utils import version_bruker2nifti


infos = {
         'name': 'bruker2nifti',
         'version': version_bruker2nifti,
         'description': 'From raw Bruker to nifti, home-made converter.',
         'web_infos' : '',
         'repository': {
                        'type': 'git',
                        'url': 'https://github.com/SebastianoF/bruker2nifti'
                       },
         'author': 'sebastiano ferraris',
         'author_email': 'sebastiano.ferraris@gmail.com',
         'dependencies': {
                          # requirements.txt file automatically generated using pipreqs.
                          'python' : 'requirements.txt'
                          }
         }

setup(name=infos['name'],
      version=infos['version'],
      description=infos['description'],
      author=infos['author'],
      author_email=infos['author_email'],
      url=infos['repository']['url'],
      packages=find_packages()
      )
