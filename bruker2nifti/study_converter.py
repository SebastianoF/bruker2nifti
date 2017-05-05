import os

from _utils import bruker_read_files
from _getters import get_list_scans, get_subject_name
from scan_converter import convert_a_scan


def show_study_structure(pfo_study):
    """
    Print to console the structure of the study.
    :param pfo_study: path to folder study.
    :return: [None] only print to console information.
    """

    if not os.path.isdir(pfo_study):
        raise IOError('Input folder does not exists.')

    print('Study folder structure: ')
    scans_list = get_list_scans(pfo_study)
    print('\n')
    print('List of scans: {}'.format(scans_list))
    pfi_first_scan = os.path.join(pfo_study, scans_list[0])
    acqp = bruker_read_files('acqp', pfi_first_scan)
    print('Version: {}'.format(acqp['ACQ_sw_version'][0]))


def convert_a_study(pfo_study_bruker_input,
                    pfo_study_nifti_output,
                    study_name=None,
                    scans_list=None,
                    list_new_name_each_scan=None,
                    list_new_nifti_file_names=None,
                    nifti_version=1,
                    qform=2,
                    sform=1,
                    save_human_readable=True,
                    save_b0_if_dwi=True,
                    correct_slope=False,
                    verbose=1,
                    get_acqp=False,
                    get_method=False,
                    get_reco=False,
                    ):
    """
    Core method of the module from a study Bruker folder structure to the homologous folder structure containing
     all the scans in nifti format and the additional information as python dictionaries and readable and ordered .txt
     files.
    :param pfo_study_bruker_input: path to folder Bruker study.
    :param pfo_study_nifti_output: path to folder where the converted study will be stored (as a sub-folder).
    :param study_name: [None] study name, that will be the name of the main output folder with the new structure.
    :param scans_list: [None] scans of the study that will be converted.
        E.g. scans_list=('3', '4')
    If default None, all the study will be converted
    :param list_new_name_each_scan: [None] list of the name of the folder corresponding to each acquisition in the
     same order of the parameter scan_list
        E.g, list_new_name_each_scan=('Patient supine', 'Patient prone')
        -> the scan '3' will be stored in the folder 'Patient supine' once converted and
         the scan '4' will be stored in the folder 'Patient prone'.
    :param list_new_nifti_file_names: [None] list of the name of the files inside each acquisition.
        E.g. list_new_nifti_file_names=('pat123_sup', 'pat123_pro')
        -> in the folder 'Patient supine' the nifti scan(s) will be (or start with) 'pat123_sup'.
         in the folder 'Patient prone' the nifti scan(s) will be (or start with) 'pat123_pro'.
    :param nifti_version: see convert_a_scan.__doc__
    :param qform: [2] qform of the header
    :param sform: [1] sform of the ehader
    :param save_human_readable: [True] other than .pyc, additional .txt will be saved.
    :param save_b0_if_dwi: save the first timepoint of the dwi if the scan is acquired with DtiEpi modality
    :param correct_slope: [False] there is no correction for the slope parameters
    :param verbose: 0 no, 1 yes, 2 yes for debug
    :return: [None]
    """
    if not os.path.isdir(pfo_study_bruker_input):
        raise IOError('Input folder does not exist.')
    if not os.path.isdir(pfo_study_nifti_output):
        raise IOError('Output folder does not exist.')

    if scans_list is None:
        scans_list = get_list_scans(pfo_study_bruker_input)

    if study_name is None:
        study_name = get_subject_name(pfo_study_bruker_input)
    if list_new_name_each_scan is None:
        list_new_name_each_scan = [study_name + '_' + ls for ls in scans_list]
    if list_new_nifti_file_names is None:
        list_new_nifti_file_names = list_new_name_each_scan
    else:
        if not len(scans_list) == len(list_new_name_each_scan):
            msg = 'list_name_each_scan {0} does not have the same amount of scans in the ' \
                  'study: {1}'.format(list_new_name_each_scan, scans_list)
            raise IOError(msg)

    pfo_nifti_study = os.path.join(pfo_study_nifti_output, study_name)
    os.system('mkdir -p {0}'.format(pfo_nifti_study))

    print('\nStudy conversion \n{}\nstarted:\n'.format(pfo_study_bruker_input))

    for bruker_scan_name, scan_name, nifti_file_name in zip(scans_list, list_new_name_each_scan,
                                                             list_new_nifti_file_names):

        pfo_scan_bruker = os.path.join(pfo_study_bruker_input, bruker_scan_name)
        pfo_scan_nifti = os.path.join(pfo_nifti_study, scan_name)

        print('\nConverting experiment {}:\n'.format(bruker_scan_name))

        convert_a_scan(pfo_scan_bruker,
                       pfo_scan_nifti,
                       create_output_folder_if_not_exists=True,
                       fin_scan=nifti_file_name,
                       nifti_version=nifti_version,
                       qform=qform,
                       sform=sform,
                       save_human_readable=save_human_readable,
                       save_b0_if_dwi=save_b0_if_dwi,
                       correct_slope=correct_slope,
                       verbose=verbose,
                       get_acqp=get_acqp,
                       get_method=get_method,
                       get_reco=get_reco,
                       )

    print('\nStudy converted and saved in \n{}'.format(pfo_study_nifti_output))
