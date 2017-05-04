import os
import numpy as np

from nose.tools import assert_equal, assert_true, assert_raises
from numpy.testing import assert_array_equal
import warnings
import subprocess
import platform


from definitions import root_dir
from bruker2nifti._utils import indian_file_parser, var_name_clean, bruker_read_files, normalise_b_vect, \
    slope_corrector, elim_consecutive_duplicates, compute_resolution_from_visu_pars, compute_affine_from_visu_pars


# TODO
