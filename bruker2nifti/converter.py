import os

from ._utils import bruker_read_files
from ._getters import get_list_scans, get_subject_name
from ._cores import scan2struct, write_struct


class Bruker2Nifti(object):

    def __init__(self, pfo_study_bruker_input, pfo_study_nifti_output, study_name=None):
        self.pfo_study_bruker_input = pfo_study_bruker_input
        self.pfo_study_nifti_output = pfo_study_nifti_output
        self.study_name = study_name
        self.scans_list = None
        self.list_new_name_each_scan = None
        self.list_new_nifti_file_names = None
        self.nifti_version = 1
        self.qform_code = 1
        self.sform_code = 2
        self.save_human_readable = True
        self.save_b0_if_dwi = True
        self.correct_slope = False
        self.verbose = 1
        self.get_acqp = False
        self.get_method = False
        self.get_reco = False

        self._get_scans_attributes()

    def _get_scans_attributes(self):

        if not os.path.isdir(self.pfo_study_bruker_input):
            raise IOError('Input folder does not exist.')
        if not os.path.isdir(self.pfo_study_nifti_output):
            raise IOError('Output folder does not exist.')
        if self.scans_list is None:
            self.scans_list = get_list_scans(self.pfo_study_bruker_input, print_structure=False)
            assert isinstance(self.scans_list, list)
        if self.study_name is None or self.study_name is '':
            _study_name = get_subject_name(self.pfo_study_bruker_input).replace(' ', '_')
            self.study_name = ''.join(e for e in _study_name if e.isalnum())
        if self.list_new_name_each_scan is None:
            list_new_name_each_scan = [self.study_name + '_' + ls for ls in self.scans_list]
            self.list_new_name_each_scan = list_new_name_each_scan
            assert isinstance(self.list_new_name_each_scan, list)
        if self.list_new_nifti_file_names is None:
            self.list_new_nifti_file_names = self.list_new_name_each_scan
        else:
            if not len(self.scans_list) == len(self.list_new_name_each_scan):
                msg = 'list_name_each_scan {0} does not have the same amount of scans in the ' \
                      'study: {1}'.format(self.list_new_name_each_scan, self.scans_list)
                raise IOError(msg)

    def show_study_structure(self):
        """
        Print to console the structure of the selected study.
        :return: [None] only print to console information.
        """
        if not os.path.isdir(self.pfo_study_bruker_input):
            raise IOError('Input folder does not exists.')

        print('Study folder structure: ')
        scans_list = get_list_scans(self.pfo_study_bruker_input)
        print('\n')
        print('List of scans: {}'.format(scans_list))
        pfi_first_scan = os.path.join(self.pfo_study_bruker_input, scans_list[0])
        acqp = bruker_read_files('acqp', pfi_first_scan)
        print('Version: {}'.format(acqp['ACQ_sw_version'][0]))

    def convert_scan(self, pfo_input_scan, pfo_output_converted, nifti_file_name=None,
                     create_output_folder_if_not_exists=True):
        """
        :param pfo_input_scan: path to folder containing a scan from Bruker.
        :param pfo_output_converted: path to the folder where the converted scan will be stored.
        :param create_output_folder_if_not_exists: [True]
        :param nifti_file_name: [None] filename of the nifti image that will be saved into the pfo_output folder.
        :return: [None] save the data parsed from the raw Bruker scan into a folder, including the nifti image.
        """
        if not os.path.isdir(pfo_input_scan):
            raise IOError('Input folder does not exist.')

        if create_output_folder_if_not_exists:
            os.system('mkdir -p {}'.format(pfo_output_converted))

        struct_scan = scan2struct(pfo_input_scan,
                                  correct_slope=self.correct_slope,
                                  nifti_version=self.nifti_version,
                                  qform_code=self.qform_code,
                                  sform_code=self.sform_code,
                                  get_acqp=self.get_acqp,
                                  get_method=self.get_method,
                                  get_reco=self.get_reco,
                                  )

        if not struct_scan == 'no data':
            write_struct(struct_scan,
                         pfo_output_converted,
                         fin_scan=nifti_file_name,
                         save_human_readable=self.save_human_readable,
                         save_b0_if_dwi=self.save_b0_if_dwi,
                         verbose=self.verbose,
                         )

    def convert(self):

        pfo_nifti_study = os.path.join(self.pfo_study_nifti_output, self.study_name)
        os.system('mkdir -p {0}'.format(pfo_nifti_study))

        print('\nStudy conversion \n{}\nstarted:\n'.format(self.pfo_study_bruker_input))

        for bruker_scan_name, scan_name, nifti_file_name in zip(self.scans_list,
                                                                self.list_new_name_each_scan,
                                                                self.list_new_nifti_file_names):
            pfo_scan_bruker = os.path.join(self.pfo_study_bruker_input, bruker_scan_name)
            pfo_scan_nifti = os.path.join(pfo_nifti_study, scan_name)

            print('\nConverting experiment {}:\n'.format(bruker_scan_name))

            self.convert_scan(pfo_scan_bruker,
                               pfo_scan_nifti,
                               create_output_folder_if_not_exists=True,
                               nifti_file_name=nifti_file_name,)

        print('\nStudy converted and saved in \n{}'.format(self.pfo_study_nifti_output))
