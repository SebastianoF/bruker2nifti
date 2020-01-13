import os
from subprocess import check_output


__author__ = "Sebastiano Ferraris UCL"
__licence__ = "MIT"
__repository__ = "https://github.com/SebastianoF/bruker2nifti"
__all__ = ["_cores", "_getters", "_metadata", "_utils", "converter"]

# here = os.path.abspath(os.path.dirname(__file__))
# git_dir = os.path.dirname(here)

# Describe the version relative to last tag
# command_git = ['git', 'describe', '--match', 'v[0-9]*']
# version_buf = check_output(command_git, cwd=git_dir).rstrip()

# Exclude the 'v' for PEP440 conformity, see
# https://www.python.org/dev/peps/pep-0440/#public-version-identifiers
__version__ = "1.0.4"  # version_buf[1:].decode("utf-8")
