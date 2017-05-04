import os
import numpy as np

from nose.tools import assert_equal, assert_true, assert_raises
from numpy.testing import assert_array_equal
import warnings
import subprocess
import platform


from definitions import root_dir
from bruker2nifti._getters import get_list_scans, get_info_sj, get_subject_name, nifti_getter


# TODO
