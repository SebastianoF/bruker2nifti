import os
import shutil

import warnings
import subprocess
import platform

from nose.tools import assert_raises

from bruker2nifti.converter import Bruker2Nifti


here = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.dirname(here)


def test_convert_the_banana(open_converted=False):

    pfo_study_in = os.path.join(root_dir, 'test_data', 'bru banana')
    pfo_study_out = os.path.join(root_dir, 'test_data', 'nifti banana')

    # delete study if already exists:
    target_folder = os.path.join(pfo_study_out, 'banana')
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)

    # instantiate the converter:
    bru = Bruker2Nifti(pfo_study_in, pfo_study_out, study_name='banana')

    bru.verbose = 2
    bru.correct_slope = True
    bru.get_acqp = False
    bru.get_method = False
    bru.get_reco = False

    bru.convert()

    if open_converted:

        if platform.system() == "Windows":
            os.startfile(pfo_study_out.encode('string-escape'))
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", pfo_study_out])
        else:
            subprocess.Popen(["xdg-open", pfo_study_out])

    for ex in ['1', '2', '3']:
        experiment_folder = os.path.join(pfo_study_out, 'banana', 'banana_{}'.format(ex))
        assert os.path.exists(experiment_folder)
        assert os.path.exists(os.path.join(experiment_folder, 'banana_{}.nii.gz'.format(ex)))


def test_convert_the_banana_no_name(open_converted=False):

    pfo_study_in = os.path.join(root_dir, 'test_data', 'bru banana')
    pfo_study_out = os.path.join(root_dir, 'test_data', 'nifti banana')

    # delete study if already exists:
    target_folder = os.path.join(pfo_study_out, 'APMFruits20111130')
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)

    bru = Bruker2Nifti(pfo_study_in, pfo_study_out)

    bru.verbose       = 2,
    bru.correct_slope = True,
    bru.get_acqp      = False,
    bru.get_method    = False,
    bru.get_reco      = False
    bru.convert()

    if open_converted:

        if platform.system() == "Windows":
            os.startfile(pfo_study_out.encode('string-escape'))
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", pfo_study_out])
        else:
            subprocess.Popen(["xdg-open", pfo_study_out])

    for ex in ['1', '2', '3']:
        experiment_folder = os.path.join(pfo_study_out, 'APMFruits20111130', 'APMFruits20111130_{}'.format(ex))
        assert os.path.exists(experiment_folder)
        assert os.path.exists(os.path.join(experiment_folder, 'APMFruits20111130_{}.nii.gz'.format(ex)))
