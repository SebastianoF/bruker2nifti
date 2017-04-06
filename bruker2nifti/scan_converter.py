import os
import numpy as np
import nibabel as nib
import pprint

from _utils import normalise_b_vect
from _getters import get_modality_from_info, get_separate_shells_b_vals_b_vect_from_info, \
    get_spatial_resolution_from_info, get_info_and_img_data


def from_dict_to_txt_sorted(dict_input, pfi_output):
    """
    Save the information contained in a dictionary into a txt file at the specified path.
    :param dict_input: input structure dictionary
    :param pfi_output: path to file.
    :return:
    """
    sorted_keys = sorted(dict_input.keys())

    with open(pfi_output, 'w') as f:
        f.writelines('{0} = {1} \n'.format(k, dict_input[k]) for k in sorted_keys)


def read_info(pfo_input):
    """
    From the path to the folder where the info are stored individually, it return the dictionary that
    contains them.
    :param pfo_input: path to folder where  'acqp.npy', 'method.npy', reco.npy', 'visu_pars.npy'
    :return: info data structure where data from 'acqp', 'method', 'reco' and 'visu_pars' of the raw Bruker are stored.
    """
    acqp      = np.load(os.path.join(pfo_input, 'acqp.npy'))
    method    = np.load(os.path.join(pfo_input, 'method.npy'))
    reco      = np.load(os.path.join(pfo_input, 'reco.npy'))
    visu_pars = np.load(os.path.join(pfo_input, 'visu_pars.npy'))

    info = {'acqp': acqp[()], 'method': method[()], 'reco': reco[()], 'visu_pars': visu_pars[()]}

    return info


def write_info(info,
               pfo_output,
               save_human_readable=True,
               separate_shells_if_dwi=False,
               num_shells=3,
               num_initial_dir_to_skip=None,
               normalise_b_vectors_if_dwi=True,
               verbose=1):
    """
    write the info data structure (dictionary containing informations from 'acqp', 'method', 'reco' and 'visu_pars')
    in files. It can divide the b-vals and b-vect by shells (if dwi) and store them in individual files.
    By default data are stored in numpy files (.npy).

    :param info: info data structure.
    :param pfo_output: path to folder where the data will be stored.
    :param save_human_readable: [True] additional .txt will be saved with the raw data provided in alpahabetical order.
    :param separate_shells_if_dwi: [False] to have shells separated in different files.
    See get_separate_shells_b_vals_b_vect_from_info.__doc__ .
    :param num_shells: number of shells of the dwi acquisition.
    :param num_initial_dir_to_skip: [None] initial direction to skip.
    See get_separate_shells_b_vals_b_vect_from_info.__doc__ .
    :param normalise_b_vectors_if_dwi: normalise b-vectors to have them of norm 1.
    :param verbose: 0 no, 1 yes, 2 yes for debug.
    :return: [None] write files in pfo_input folder.

    .. note :: To load the saved structure back in the info dictionary, use the function read_info, with pfo_output
    as input.
    """
    if not os.path.isdir(pfo_output):
        raise IOError('Output folder does not exists.')

    # print ordered dictionaries values to console. very very verbose!
    if verbose > 2:
        print('\n\n -------------- acqp --------------')
        print(pprint.pprint(info['acqp']))
        print('\n\n -------------- method --------------')
        print(pprint.pprint(info['method']))
        print('\n\n -------------- reco --------------')
        print(pprint.pprint(info['reco']))
        print('\n\n -------------- visu_pars --------------')
        print(pprint.pprint(info['visu_pars']))
        print('\n\n -----------------------------------')

    # if the modality is a DtiEpi or Dwimage then save the DW directions, b values and b vectors in separate csv .txt.
    modality = get_modality_from_info(info)

    if modality == 'DtiEpi' or 'dw' in modality.lower():

        if normalise_b_vectors_if_dwi:
            info['method']['DwGradVec'] = normalise_b_vect(info['method']['DwGradVec'])

        # Save DwDir:
        dw_dir = info['method']['DwDir']
        np.savetxt(os.path.join(pfo_output, 'DwDir.txt'), dw_dir, fmt='%.14f')

        if verbose > 0:
            msg = 'Diffusion weighted directions saved in ' + os.path.join(pfo_output, 'DwDir.txt')
            print(msg)

        # DwEffBval and DwGradVec are divided by shells
        if separate_shells_if_dwi:

            # save DwEffBval DwGradVec
            [list_b_vals, list_b_vects] = get_separate_shells_b_vals_b_vect_from_info(
                info,
                num_shells=num_shells,
                num_initial_dir_to_skip=num_initial_dir_to_skip)
            for i in range(num_shells):
                path_b_vals_shell_i = os.path.join(pfo_output, modality + '_DwEffBval_shell' + str(i) + '.txt')
                path_b_vect_shell_i = os.path.join(pfo_output, modality + '_DwGradVec_shell' + str(i) + '.txt')

                np.savetxt(path_b_vals_shell_i, list_b_vals[i], fmt='%.14f')
                np.savetxt(path_b_vect_shell_i, list_b_vects[i], fmt='%.14f')

                if verbose > 0:
                    print('B-vectors for shell {0} saved in {1}'.format(str(i), path_b_vals_shell_i))
                    print('B-values for shell {0} saved in {1}'.format(str(i), path_b_vect_shell_i))

        else:

            b_vals = info['method']['DwEffBval']
            b_vects = info['method']['DwGradVec']

            np.savetxt(os.path.join(pfo_output, 'DwEffBval.txt'), b_vals, fmt='%.14f')
            np.savetxt(os.path.join(pfo_output, 'DwGradVec.txt'), b_vects, fmt='%.14f')

            if verbose > 0:
                print('B-vectors saved in {}'.format(os.path.join(pfo_output, 'DwEffBval.txt')))
                print('B-values  saved in {}'.format(os.path.join(pfo_output, 'DwGradVec.txt')))

    # save the dictionary as numpy array containing the corresponding dictionaries
    np.save(os.path.join(pfo_output, 'acqp.npy'), info['acqp'])
    np.save(os.path.join(pfo_output, 'method.npy'), info['method'])
    np.save(os.path.join(pfo_output, 'reco.npy'), info['reco'])
    np.save(os.path.join(pfo_output, 'visu_pars.npy'), info['visu_pars'])

    # save in ordered readable txt files.
    if save_human_readable:
        from_dict_to_txt_sorted(info['acqp'], os.path.join(pfo_output, 'acqp.txt'))
        from_dict_to_txt_sorted(info['method'], os.path.join(pfo_output, 'method.txt'))
        from_dict_to_txt_sorted(info['reco'], os.path.join(pfo_output, 'reco.txt'))
        from_dict_to_txt_sorted(info['visu_pars'], os.path.join(pfo_output, 'visu_pars.txt'))


def write_to_nifti(info,
                   img_data,
                   pfi_output,
                   separate_shells_if_dwi=False,
                   num_shells=3,
                   num_initial_dir_to_skip=7,
                   nifti_version=1,
                   qform=2,
                   sform=1,
                   axis_direction=(-1, -1, 1),
                   verbose=1):
    """
    Second main component of the bridge and core method.
    From the info and img_data, as data structure obtained as output of the method get_info_and_img_data it saves
    the nifti image in the specified file.
    :param info: info data structure as provided by get_info_and_img_data.
    :param img_data: image data structure as provided by get_info_and_img_data. See get_info_and_img_data.__doc__ .
    :param pfi_output: path to file output. Here the nifti will be stored.
    :param separate_shells_if_dwi: [False] TODO
    :param num_shells:
    :param num_initial_dir_to_skip:
    :param nifti_version: nifti file can be 1 or 2. The values of the nifti attributes are filled in the same way
    (as nifti1 even when nifti2 is selected).
    :param qform:
    :param sform:
    :param axis_direction: [(-1, -,1, 1)] the signs of the diagonal of the affine transformation
    (otherwise providing the positive spatial resolution in the diagonal of the affine transformation. By default
    the affine matrix is a diagonal matrix).
    axis_direction=(1,1,1) means in the header L S I (left-superior-inferior). (-1, -,1, -1) means RAS
    :param verbose: 0 no, 1 yes, 2 yes for debug.
    :return: [None] write the corresponding nifti image.
    """
    # qform 2, sform 1, axis direction (-1,-1,1) to reproduce output of Leuven matlab script.
    # axis_direction=(1,1,1) means in the header L S I (left-superior-inferior).
    if not pfi_output.endswith('.nii') and not pfi_output.endswith('.nii.gz'):
        pfi_output += '.nii.gz'
        print('Output file not ending with .nii or .nii.gz. Default .nii.gz added')

    if separate_shells_if_dwi:
        # TODO
        print(num_shells)
        print(num_initial_dir_to_skip)

    else:

        sp_res = list(get_spatial_resolution_from_info(info))
        sp_res = np.array(sp_res + [1, ] * (3 - len(sp_res)) + [1])
        axis_direction = list(axis_direction)
        axis_direction = np.array(axis_direction + [1, ] * (3 - len(axis_direction)) + [1])

        affine = np.diag(sp_res * axis_direction).astype(np.float64)

        if verbose > 1:
            print(affine)

        if nifti_version == 1:
            nib_im = nib.Nifti1Image(img_data, affine=affine)
        elif nifti_version == 2:
            nib_im = nib.Nifti2Image(img_data, affine=affine)
        else:
            raise IOError('Nifti versions allowed are 1 or 2.')

        hdr = nib_im.header
        hdr.set_qform(affine, qform)
        hdr.set_sform(affine, sform)
        nib_im.update_header()

        # sanity check image dimension from header to shape:
        shape_from_info = list(info['reco']['RECO_size'])

        if info['acqp']['ACQ_sw_version'] == 'PV 5.1' or info['acqp']['ACQ_sw_version'] == '5.1':
            shape_from_info[1], shape_from_info[0] = shape_from_info[0], shape_from_info[1]

        if info['acqp']['NR'] > 1:
            shape_from_info = shape_from_info + [info['acqp']['NR'], ]

        if info['method']['SpatDimEnum'] == '3D':
            if info['method']['Method'] == 'FieldMap' or info['method']['Method'] == 'Bruker:FieldMap':
                np.testing.assert_array_equal(shape_from_info[:2], nib_im.shape[:2])
            else:
                np.testing.assert_array_equal(shape_from_info, nib_im.shape)
        elif info['method']['SpatDimEnum'] == '2D':
            np.testing.assert_array_equal(shape_from_info[:2], nib_im.shape[:2])
        else:
            print("method['SpatDimEnum'] is " + info['method']['SpatDimEnum'] +
                  " [not '2D' or '3D']-> no sanity check on dimensions.")

        if verbose > 0:
            print('Saving image to nifti (may take a while)...\n')

        # saving with nibabel:
        nib.save(nib_im, pfi_output)

        if verbose > 0:
            print('Scan saved in nifti format version {0} at: \n{1}'.format(nifti_version, pfi_output))
            print('Shape : \n {0}\n affine: \n{1}\n'.format(nib_im.shape, nib_im.affine))


def convert_a_scan(pfo_input_scan,
                   pfo_output,
                   create_output_folder_if_not_esists=True,
                   fin_output=None,
                   nifti_version=1,
                   qform=2,
                   sform=1,
                   axis_direction=(-1, -1, 1),
                   save_human_readable=True,
                   normalise_b_vectors_if_dwi=True,
                   correct_slope=True,
                   verbose=1):
    """
    Put together all the components of the bridge: get_info_and_img_data, write_info and write_to_nifti.
    The bridge goes FROM the path where the bruker scan is stored TO where the output will be saved.
    :param pfo_input_scan: path to folder containing a scan from Bruker.
    :param pfo_output: path to folder where the nifti and all the additional informations will be stored.
    :param create_output_folder_if_not_esists: [True]
    :param fin_output: [None] filename of the nifti image that will be saved into the pfo_output folder.
    :param nifti_version: [1]
    :param qform:
    :param sform:
    :param axis_direction: see write_to_nifti.__doc__
    :param save_human_readable:
    :param normalise_b_vectors_if_dwi:
    :param correct_slope:
    :param verbose: 0 no, 1 yes, 2 yes debug
    :return: [None] save the data parsed from the raw Bruker scan into a folder, including the nifti image.
    """
    if create_output_folder_if_not_esists:
        os.system('mkdir -p {}'.format(pfo_output))

    info, img_data = get_info_and_img_data(pfo_input_scan,
                                           correct_slope=correct_slope,
                                           verbose=verbose)

    if fin_output is None:  # filename output
        fin_output = info['method']['Method'].lower() + \
                     info['acqp']['ACQ_time'].split(',')[0]
        fin_output = fin_output.replace(' ', '_').replace(':', '_').replace('T', '_')
        fin_output += '.nii.gz'

    write_info(info,
               pfo_output,
               save_human_readable=save_human_readable,
               verbose=verbose,
               normalise_b_vectors_if_dwi=normalise_b_vectors_if_dwi)

    write_to_nifti(info,
                   img_data,
                   os.path.join(pfo_output, fin_output),
                   qform=qform,
                   sform=sform,
                   axis_direction=axis_direction,
                   nifti_version=nifti_version)
