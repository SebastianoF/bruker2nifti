#!/usr/bin/env python
from setuptools import setup, find_packages
from definitions import root_dir


infos = {
         'name': 'bruker2nifti',
         'version': '0.0.1',
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
                          'python' : '{0}/requirements.txt'.format(root_dir)
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
