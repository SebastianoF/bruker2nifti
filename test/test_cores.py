import os
import numpy as np
import warnings
import sys

from numpy.testing import assert_array_equal, assert_equal

from bruker2nifti._cores import scan2struct, write_struct

here = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.dirname(here)


def test_scan2struct_with_banana_data_slope_no_slope():

    pfo_scan_in = os.path.join(root_dir, 'test_data', 'bru_banana', '1')

    struct_no_slope_corrected = scan2struct(pfo_scan_in, correct_slope=False)

    struct_yes_slope_corrected = scan2struct(pfo_scan_in, correct_slope=True)

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


def test_write_struct():

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Trigger a warning
        pfo_study_in = os.path.join(root_dir, 'test_data', 'bru_banana')
        scan2struct(pfo_study_in)
        # manage warning in python 2 or python 3:
        if sys.version_info[0] == 3:
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
        else:
            import exceptions
            assert len(w) == 1
            assert issubclass(w[-1].category, exceptions.UserWarning)

    pfo_scan_in = os.path.join(root_dir, 'test_data', 'bru_banana', '1')
    banana_struct = scan2struct(pfo_scan_in)

    pfo_output = os.path.join(root_dir, 'test_data', 'nifti_banana', 'write_struct_here')
    if not os.path.exists(pfo_output):
        os.system('mkdir {}'.format(pfo_output))

    write_struct(banana_struct, pfo_output, fin_scan='test')

    assert os.path.exists(os.path.join(pfo_output, 'acquisition_method.txt'))
    assert os.path.exists(os.path.join(pfo_output, 'test.nii.gz'))
