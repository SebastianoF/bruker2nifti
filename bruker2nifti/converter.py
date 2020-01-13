import os

from bruker2nifti._utils import bruker_read_files
from bruker2nifti._getters import get_list_scans, get_subject_name
from bruker2nifti._cores import scan2struct, write_struct


class Bruker2Nifti(object):
    """
    Facade to collect users preferences on the conversion and accessing the core methods for the conversion
    (scan_to_struct, write_struct).

    Nomenclature:

    study: a series of acquisition related to the same subject, acquired in the same scanning session and usually
    containing multiple scans. It is provided as a folder structure containing the scans produced with paravision (PV)
    software. Patient/subject information are embedded in the study (opposed hierarchy as in the DICOM files).

    scan or experiment, sub-scans and sub-volumes: individual folder image acquired with various protocols. To a scan
    can belong more than one processed image, or reconstruction. Each processed image can be a single volume or can
    contain more than one sub-volume embedded in the same processed image.

    header: header of the nifti format.

    img_data: data of the nifti format, stored in a 2d or 3d matrix.

    struct: intermediate structure (python dictionary) proposed in this code, aimed at collecting the information from
    the raw Bruker and to progressively creating the nifti images.
    """

    def __init__(self, pfo_study_bruker_input, pfo_study_nifti_output, study_name=None):
        """
        Initialise the Facade class to the converter.
        :param pfo_study_bruker_input: path to folder (pfo) to the Bruker input data folder.
        :param pfo_study_nifti_output: path to folder (pfo) where the converted study will be stored.
        :param study_name: optional name of the study. If None, the name parsed from the Bruker study will be used.
        """
        self.pfo_study_bruker_input = pfo_study_bruker_input
        self.pfo_study_nifti_output = pfo_study_nifti_output
        self.study_name = study_name
        # converter settings for the nifti values
        self.nifti_version = 1
        self.qform_code = 1
        self.sform_code = 2
        self.save_human_readable = True
        self.save_b0_if_dwi = (
            True
        )  # if DWI, it saves the first layer as a single nfti image.
        self.correct_slope = True
        self.correct_offset = True
        # advanced sample positioning
        self.sample_upside_down = False
        self.frame_body_as_frame_head = False
        # chose to convert extra files:
        self.get_acqp = False
        self.get_method = False
        self.get_reco = False
        # advanced selections:
        self.scans_list = (
            None
        )  # you can select a subset of scans in the study to be converted.
        self.list_new_name_each_scan = (
            None
        )  # you can select specific names for the subset self.scans_list.
        self.verbose = 1
        # automatic filling of advanced selections class attributes
        self.explore_study()

    def explore_study(self):
        """
        Automatic filling of the advanced selections class attributes.
        It also checks if the given attributes are meaningful.
        :return:
        """

        if not os.path.isdir(self.pfo_study_bruker_input):
            raise IOError("Input folder does not exist.")
        if not os.path.isdir(self.pfo_study_nifti_output):
            raise IOError("Output folder does not exist.")
        if self.scans_list is None:
            self.scans_list = get_list_scans(
                self.pfo_study_bruker_input, print_structure=False
            )
            assert isinstance(self.scans_list, list)
            msg = (
                "No scans found, are you sure the input folder contains a Bruker study?"
            )
            if not len(self.scans_list) > 0:
                raise IOError(msg)
        if self.study_name is None or self.study_name is "":
            _study_name = get_subject_name(self.pfo_study_bruker_input).replace(
                " ", "_"
            )
            self.study_name = "".join(e for e in _study_name if e.isalnum())
        if self.list_new_name_each_scan is None:
            list_new_name_each_scan = [
                self.study_name + "_" + ls for ls in self.scans_list
            ]
            self.list_new_name_each_scan = list_new_name_each_scan
            assert isinstance(self.list_new_name_each_scan, list)
        # if self.list_new_nifti_file_names is None:
        #     self.list_new_nifti_file_names = self.list_new_name_each_scan
        else:
            if not len(self.scans_list) == len(self.list_new_name_each_scan):
                msg = (
                    "list_name_each_scan {0} does not have the same amount of scans in the "
                    "study: {1}".format(self.list_new_name_each_scan, self.scans_list)
                )
                raise IOError(msg)

    def show_study_structure(self):
        """
        Print to console the structure of the selected study.
        :return: [None] only print to console information.
        """
        if not os.path.isdir(self.pfo_study_bruker_input):
            raise IOError("Input folder does not exist.")

        print("Study folder structure: ")
        scans_list = get_list_scans(self.pfo_study_bruker_input)
        print("\n")
        print("List of scans: {}".format(scans_list))
        pfi_first_scan = os.path.join(self.pfo_study_bruker_input, scans_list[0])
        acqp = bruker_read_files("acqp", pfi_first_scan)
        print("Version: {}".format(acqp["ACQ_sw_version"][0]))

    def convert_scan(
        self,
        pfo_input_scan,
        pfo_output_converted,
        nifti_file_name=None,
        create_output_folder_if_not_exists=True,
    ):
        """
        :param pfo_input_scan: path to folder (pfo) containing a scan from Bruker, see documentation for the difference
         between Bruker 'scan' and Bruker 'study'.
        :param pfo_output_converted: path to the folder where the converted scan will be stored.
        :param create_output_folder_if_not_exists: [True] if the output folder does not exist will be created.
        :param nifti_file_name: [None] filename of the nifti image that will be saved into the pfo_output folder.
         If None, the filename will be obtained from the parameter file of the study.
        :return: [None] save the data parsed from the raw Bruker scan into a folder, including the nifti image.
        """

        if not os.path.isdir(pfo_input_scan):
            raise IOError("Input folder does not exist.")

        if create_output_folder_if_not_exists:
            os.makedirs(pfo_output_converted)

        struct_scan = scan2struct(
            pfo_input_scan,
            correct_slope=self.correct_slope,
            correct_offset=self.correct_offset,
            sample_upside_down=self.sample_upside_down,
            nifti_version=self.nifti_version,
            qform_code=self.qform_code,
            sform_code=self.sform_code,
            get_acqp=self.get_acqp,
            get_method=self.get_method,
            get_reco=self.get_reco,
            frame_body_as_frame_head=self.frame_body_as_frame_head,
        )

        if struct_scan is not None:
            write_struct(
                struct_scan,
                pfo_output_converted,
                fin_scan=nifti_file_name,
                save_human_readable=self.save_human_readable,
                save_b0_if_dwi=self.save_b0_if_dwi,
                verbose=self.verbose,
            )

    def convert(self):
        """
        To call the converter, once all the settings of the converter are selected and modified by the user.
        :return: Convert the Bruker study, whose path is stored in the class variable self.pfo_study_bruker_input
        in the specified folder stored in self.pfo_study_nifti_output, and according to the other class attributes.

        Example:

        >> bru = Bruker2Nifti('/path/to/my/study', '/path/output', study_name='study1')

        >> bru.show_study_structure

        >> bru.verbose = 2
        >> bru.correct_slope = True
        >> bru.get_acqp = False
        >> bru.get_method = True  # I want to see the method parameter file converted as well.
        >> bru.get_reco = False

        >> # Convert the study:
        >> bru.convert()

        """
        pfo_nifti_study = os.path.join(self.pfo_study_nifti_output, self.study_name)
        os.makedirs(pfo_nifti_study)

        print("\nStudy conversion \n{}\nstarted:\n".format(self.pfo_study_bruker_input))

        for bruker_scan_name, scan_name in zip(
            self.scans_list, self.list_new_name_each_scan
        ):
            pfo_scan_bruker = os.path.join(
                self.pfo_study_bruker_input, bruker_scan_name
            )
            pfo_scan_nifti = os.path.join(pfo_nifti_study, scan_name)

            print("\nConverting experiment {}:\n".format(bruker_scan_name))

            self.convert_scan(
                pfo_scan_bruker,
                pfo_scan_nifti,
                create_output_folder_if_not_exists=True,
                nifti_file_name=scan_name,
            )

        print("\nStudy converted and saved in \n{}".format(self.pfo_study_nifti_output))
