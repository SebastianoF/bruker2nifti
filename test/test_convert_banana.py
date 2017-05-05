import os

import warnings
import subprocess
import platform


from definitions import root_dir
from bruker2nifti.study_converter import convert_a_study


def test_convert_the_banana(open_converted=True):

    pfo_study_in = os.path.join(root_dir, 'test_data', 'bru_banana')
    pfo_study_out = os.path.join(root_dir, 'test_data', 'nifti_banana')

    convert_a_study(pfo_study_in,
                    pfo_study_out,
                    verbose=2,
                    correct_slope=True,
                    study_name='banana',
                    get_acqp=False,
                    get_method=False,
                    get_reco=False,
    )

    if open_converted:

        if platform.system() == "Windows":
            os.startfile(pfo_study_out.encode('string-escape'))
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", pfo_study_out])
        else:
            subprocess.Popen(["xdg-open", pfo_study_out])


def test_warning_banana_bad_n():

    for n in ['1', '2', '3']:

        pfo_study_in = os.path.join(root_dir, 'test_data', 'bru_banana_bad_' + n)
        pfo_study_out = os.path.join(root_dir, 'test_data', 'nifti_banana')

        with warnings.catch_warnings(record=True) as wa:

            warnings.simplefilter('always')

            convert_a_study(pfo_study_in, pfo_study_out, verbose=2, correct_slope=True, study_name='banana')

            assert len(wa) == 1
            assert issubclass(wa[-1].category, Warning)


test_convert_the_banana()