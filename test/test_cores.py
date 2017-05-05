import os
import numpy as np

from nose.tools import assert_equal
from numpy.testing import assert_array_equal

from definitions import root_dir
from bruker2nifti._cores import scan2struct


def test_scan2struct_with_banana_data_slope_no_slope():

    pfo_study_in = os.path.join(root_dir, 'test_data', 'bru_banana', '1')

    struct_no_slope_corrected = scan2struct(pfo_study_in, correct_slope=False)

    struct_yes_slope_corrected = scan2struct(pfo_study_in, correct_slope=True)

    parsed_slope_from_no = struct_no_slope_corrected['visu_pars_list'][0]['VisuCoreDataSlope']
    parsed_slope_from_yes = struct_yes_slope_corrected['visu_pars_list'][0]['VisuCoreDataSlope']
    ground_slope = np.array([11.02701887, ] * 5)

    # check general structure:
    assert_equal(struct_no_slope_corrected['nib_scans_list'][0].shape,
                 struct_yes_slope_corrected['nib_scans_list'][0].shape)
    assert_array_equal(parsed_slope_from_no, parsed_slope_from_yes)
    np.testing.assert_array_almost_equal(parsed_slope_from_no, ground_slope)

    assert_equal(struct_no_slope_corrected['acqp'], {})
    assert_equal(struct_no_slope_corrected['reco'], {})
    assert_equal(struct_no_slope_corrected['method'], {})

    # check data of the nibabel images:
    np.testing.assert_array_almost_equal(ground_slope[0] * struct_no_slope_corrected['nib_scans_list'][0].get_data(),
                                         struct_yes_slope_corrected['nib_scans_list'][0].get_data(), decimal=4)
