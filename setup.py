#!/usr/bin/env python
import os
from setuptools import setup, find_packages

from bruker2nifti.__init__ import __version__ as version


def requirements2list(pfi_txt="requirements.txt"):
    here = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(here, pfi_txt), "r")
    l = []
    for line in f.readlines():
        l.append(line.replace("\n", ""))
    return l


infos = {
    "name": "bruker2nifti",
    "version": version,
    "description": "From raw Bruker to nifti, home-made converter.",
    "web_infos": "",
    "repository": {"type": "git", "url": "https://github.com/SebastianoF/bruker2nifti"},
    "author": "sebastiano ferraris",
    "author_email": "sebastiano.ferraris@gmail.com",
    "dependencies": {
        # requirements.txt file automatically generated using pipreqs.
        "python": "requirements.txt"
    },
}

setup(
    name=infos["name"],
    version=infos["version"],
    description=infos["description"],
    author=infos["author"],
    author_email=infos["author_email"],
    url=infos["repository"]["url"],
    packages=find_packages(),
    install_requires=requirements2list(),
    entry_points={
        "console_scripts": [
            "bruker2nifti=bruker2nifti.cli.bruker2nii:main",
            "bruker2nifti_scan=bruker2nifti.cli.bruker2nii_scan:main_scan",
        ],
        "gui_scripts": ["bruker2nifti_gui=bruker2nifti.gui.open:open_gui"],
    },
)
