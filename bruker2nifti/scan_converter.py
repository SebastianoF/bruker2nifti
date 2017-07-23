import os

from ._cores import scan2struct, write_struct


def convert_a_scan(pfo_input_scan,
                   pfo_output,
                   create_output_folder_if_not_exists=True,
                   nifti_version=1,
                   qform_code=1,
                   sform_code=2,
                   correct_slope=True,
                   nifti_file_name=None,
                   save_b0_if_dwi=True,
                   save_human_readable=True,
                   verbose=1,
                   get_acqp=False,
                   get_method=False,
                   get_reco=False,
                   ):
    """
    Put together all the components of the bridge: scan2struct and write_struct.
    The bridge goes FROM the path where the bruker scan is stored TO where the output will be saved.
    :param pfo_input_scan: path to folder containing a scan from Bruker.
    :param pfo_output: path to folder where the nifti and all the additional informations will be stored.
    :param create_output_folder_if_not_exists: [True]
    :param nifti_file_name: [None] filename of the nifti image that will be saved into the pfo_output folder.
    :param nifti_version: [1]
    :param qform_code: [1] see nibabel documentation
    :param sform_code: [2] see nibabel documentation
    :param correct_slope:
    :param save_human_readable:
    :param save_b0_if_dwi:
    :param verbose: 0 no, 1 yes, 2 yes for debug
    :param get_acqp: parse also the parameter file acqp
    :param get_method: parse also the parameter file method
    :param get_reco: parse also the parameter file reco
    :return: [None] save the data parsed from the raw Bruker scan into a folder, including the nifti image.
    """
    if not os.path.isdir(pfo_input_scan):
        raise IOError('Input folder does not exist.')

    if create_output_folder_if_not_exists:
        os.system('mkdir -p {}'.format(pfo_output))

    struct_scan = scan2struct(pfo_input_scan,
                              correct_slope=correct_slope,
                              nifti_version=nifti_version,
                              qform_code=qform_code,
                              sform_code=sform_code,
                              get_acqp=get_acqp,
                              get_method=get_method,
                              get_reco=get_reco,
                              )

    if not struct_scan == 'no data':
        write_struct(struct_scan,
                     pfo_output,
                     fin_scan=nifti_file_name,
                     save_human_readable=save_human_readable,
                     save_b0_if_dwi=save_b0_if_dwi,
                     verbose=verbose,
                     )
