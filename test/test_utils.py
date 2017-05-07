import os
import numpy as np
import nibabel as nib

from nose.tools import assert_equal, assert_true, assert_raises, assert_almost_equals
from numpy.testing import assert_array_equal
import warnings
import subprocess
import platform


from definitions import root_dir
from bruker2nifti._utils import indian_file_parser, normalise_b_vect, slope_corrector, \
    eliminate_consecutive_duplicates, compute_resolution_from_visu_pars, compute_affine_from_visu_pars, \
    apply_reorientation_to_b_vects


# --- TEST text-files utils ---


def test_indian_file_parser_A():

    indian_file_test_1 = "('<VisuCoreOrientation>, 0') ('<VisuCorePosition>, 0')"
    indian_file_test_2 = "(EPI (pmv))"
    indian_file_test_3 = "(5, <FG_SLICE>, <>, 0, 2)"
    indian_file_test_4 = "( SPAM )"

    a1 = indian_file_parser(indian_file_test_1)
    a2 = indian_file_parser(indian_file_test_2)
    a3 = indian_file_parser(indian_file_test_3)
    a4 = indian_file_parser(indian_file_test_4)

    assert_equal(a1, ["('<VisuCoreOrientation>, 0')", "('<VisuCorePosition>, 0')"])
    assert_equal(a2, indian_file_test_2)
    assert_equal(a3, indian_file_test_3)
    assert_equal(a4, indian_file_test_4)


def test_indian_file_parser_B():

    indian_file_test_1 = "4.24"
    indian_file_test_2 = "  4.24  "
    indian_file_test_3 = "1"
    indian_file_test_4 = "80 64e2"
    indian_file_test_5 = "22.3 5.3e12 4.4 5.62e-5 3.9 42.42"

    a1 = indian_file_parser(indian_file_test_1)
    a2 = indian_file_parser(indian_file_test_2)
    a3 = indian_file_parser(indian_file_test_3)
    a4 = indian_file_parser(indian_file_test_4, sh=[2])
    a5 = indian_file_parser(indian_file_test_5, sh=[2, 3])
    a6 = indian_file_parser(indian_file_test_5)

    assert_equal(a1, 4.24)
    assert_equal(a2, 4.24)
    assert_equal(a3, 1)
    np.testing.assert_array_equal(a4, np.array([80, 6400]))
    np.testing.assert_array_equal(a5, np.array([[22.3, 5.3e12, 4.4], [5.62e-05, 3.9, 42.42]]))
    np.testing.assert_array_equal(a6, np.array([22.3, 5.3e12, 4.4, 5.62e-05, 3.9, 42.42]))


def test_indian_file_parser_C():

    indian_file_test_1 = "<123.321.123>"
    indian_file_test_2 = "<123.321.123> <123.321.123>"
    indian_file_test_3 = "<20:19:47  1 Sep 2016>"

    a1 = indian_file_parser(indian_file_test_1)
    a2 = indian_file_parser(indian_file_test_2)
    a3 = indian_file_parser(indian_file_test_3)

    assert_equal(a1, '123.321.123')
    assert_equal(a2, ['123.321.123', '123.321.123'])
    assert_equal(a3, '20:19:47  1 Sep 2016')


def test_indian_file_parser_D():

    indian_file_test_1 = "Ultra-Spam"
    indian_file_test_2 = "OtherAnimal"
    indian_file_test_3 = "Prone_Supine"

    a1 = indian_file_parser(indian_file_test_1)
    a2 = indian_file_parser(indian_file_test_2)
    a3 = indian_file_parser(indian_file_test_3)

    assert_equal(a1, indian_file_test_1)
    assert_equal(a2, indian_file_test_2)
    assert_equal(a3, indian_file_test_3)


# --- TEST slope correction utils ---


def test_slope_corrector():
    pass  # In progress...


# -- TSET nifti affine matrix utils --


def test_compute_resolution_from_visu_pars():
    pass


def test_compute_affine_from_visu_pars():
    pass


# --- TEST b-vectors utils ---


def test_normalise_b_vect():
    num_vects = 30
    v = np.random.normal(5, 10, [num_vects, 3])
    v[5, :] = np.array([np.nan, ] * 3)
    v_normalised = normalise_b_vect(v)

    for k in list(set(range(num_vects)) - {5}):
        assert_almost_equals(np.linalg.norm(v_normalised[k, :]), 1.0)
    assert_equal(np.linalg.norm(v_normalised[5, :]), .0)


def test_apply_reorientation_to_b_vects():
    pass


# -- TEST housekeeping utils --


def test_eliminate_consecutive_duplicates():
    pass


def test_set_new_data():
    pass
