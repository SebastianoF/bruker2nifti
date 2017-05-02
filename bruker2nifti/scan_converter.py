import os

from _cores import scan2struct, write_struct, scan2struct_test


def convert_a_scan(pfo_input_scan,
                   pfo_output,
                   create_output_folder_if_not_exists=True,
                   nifti_version=1,
                   qform=2,
                   sform=1,
                   correct_slope=True,
                   fin_scan=None,
                   normalise_b_vectors_if_dwi=True,
                   save_b0_if_dwi=True,
                   save_human_readable=True,
                   verbose=1):
    """
    Put together all the components of the bridge: scan2struct and write_struct.
    The bridge goes FROM the path where the bruker scan is stored TO where the output will be saved.
    :param pfo_input_scan: path to folder containing a scan from Bruker.
    :param pfo_output: path to folder where the nifti and all the additional informations will be stored.
    :param create_output_folder_if_not_exists: [True]
    :param fin_scan: [None] filename of the nifti image that will be saved into the pfo_output folder.
    :param nifti_version: [1]
    :param qform:
    :param sform:
    :param correct_slope:
    :param normalise_b_vectors_if_dwi:
    :param save_human_readable:
    :param save_b0_if_dwi:
    :param verbose: 0 no, 1 yes, 2 yes debug
    :return: [None] save the data parsed from the raw Bruker scan into a folder, including the nifti image.
    """

    if create_output_folder_if_not_exists:
        os.system('mkdir -p {}'.format(pfo_output))

    struct_scan = scan2struct(pfo_input_scan,
                              correct_slope=correct_slope,
                              nifti_version=nifti_version,
                              qform=qform,
                              sform=sform)

    if not struct_scan == 'no data':
        write_struct(struct_scan,
                     pfo_output,
                     fin_scan=fin_scan,
                     save_human_readable=save_human_readable,
                     normalise_b_vectors_if_dwi=normalise_b_vectors_if_dwi,
                     save_b0_if_dwi=save_b0_if_dwi,
                     verbose=verbose)
