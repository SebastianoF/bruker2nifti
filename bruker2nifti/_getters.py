import os
import nibabel as nib
import numpy as np

from _utils import bruker_read_files, elim_consecutive_duplicates, slope_corrector, compute_affine_from_visu_pars, \
    compute_resolution_from_visu_pars


def get_separate_shells_b_vals_b_vect_from_method(method, num_shells=3, num_initial_dir_to_skip=None, verbose=0):
    """
    From info structure returns the b-vals and b-vect separated by shells.
    :param method: info structure, output of get_info_and_img_data.
    :param num_shells: [3] number of shells of the dwi
    :param num_initial_dir_to_skip: [None] some of the initial directions may be all b0. This information can be
    inserted manually, or it is automatically. If None the values is estimated from the b-values (all the first
    b-values lower than 10 are considered to be skipped).
    :param verbose: 0 no, 1 yes, 2 yes for debug.
    :return [[bvals splitted per shell], [bvect splitted per shell]]: list of lists of b-values and b-vectors per shell.
     a different list for each shell for b-vals and b-vect
    """
    if num_initial_dir_to_skip is None:
        num_initial_dir_to_skip = len([b for b in method['DwEffBval'] if b < 10])

    b_vals = method['DwEffBval'][num_initial_dir_to_skip:]
    b_vects = method['DwGradVec'][num_initial_dir_to_skip:]
    if verbose > 1:
        print(b_vals)
        print(b_vects)

    b_vals_per_shell = []
    b_vect_per_shell = []

    for k in range(num_shells):
        b_vals_per_shell.append(b_vals[k::num_shells])
        b_vect_per_shell.append(b_vects[k::num_shells])

    # sanity check
    num_directions = len(b_vals_per_shell[0])
    for k in range(num_shells):
        if not len(b_vals_per_shell[k]) == len(b_vect_per_shell[k]) == num_directions:
            raise IOError

    return [b_vals_per_shell, b_vect_per_shell]


def get_list_scans(start_path):

    scans_list = []

    for dirpath, dirnames, filenames in os.walk(start_path):

        if dirpath == start_path:
            scans_list = [d for d in dirnames if d.isdigit()]

        level = dirpath.replace(start_path, '').count(os.sep)
        indent = (' ' * 4) * level
        print('{}{}/'.format(indent, os.path.basename(dirpath)))

        sub_indent = (' ' * 4) * (level + 1)
        for f in filenames:
            print('{}{}'.format(sub_indent, f))

    if not scans_list:  # if scan_list is []
        msg = 'Input study does not have scans stored in sub-folders named with progressive positive integers.'
        msg += '\nIs it a paravision study?'
        raise IOError(msg)

    return scans_list


def get_info_sj(pfo_study):
    """
    :param pfo_study: path to study folder.
    :return: get the information of the subject as a dictionary.
    """

    if not os.path.isdir(pfo_study):
        raise IOError('Input folder does not exists.')

    return bruker_read_files('subject', pfo_study)


def get_subject_name(pfo_study):
    """
    :param pfo_study: path to study folder.
    :return: name of the subject in the study. See get_subject_id.
    """
    info_sj = get_info_sj(pfo_study)
    return info_sj['SUBJECT_name']


def get_subject_id(pfo_study):
    """
    :param pfo_study: path to study folder.
    :return: id of the subject. See get_subject_name
    """
    info_sj = get_info_sj(pfo_study)
    return info_sj['SUBJECT_id'][0]


def nifti_getter(img_data_vol, visu_pars, correct_slope, nifti_version, qform, sform):
    # obtaining the nifti using only the information in visu_pars.

    # Check units of measurements:
    if not ['mm', ] * len(visu_pars['VisuCoreSize']) == visu_pars['VisuCoreUnits']:
        print('Warning, measurement not in mm. This version of the converter deals with data in mm only.')

    # get pre-shape and re-shape volume: (pre-shape is the shape compatible with the slope).
    vol_pre_shape = [int(i) for i in visu_pars['VisuCoreSize']]
    if int(visu_pars['VisuCoreFrameCount']) > 1:
        vol_pre_shape += [int(visu_pars['VisuCoreFrameCount'])]

    if np.prod(vol_pre_shape) == img_data_vol.shape[0]:
        vol_data = img_data_vol.reshape(vol_pre_shape, order='F')
    else:
        echo = img_data_vol.shape[0] / np.prod(vol_pre_shape)
        vol_pre_shape += [echo]
        vol_data = img_data_vol.reshape(vol_pre_shape, order='F')

    # correct slope if required
    if correct_slope:
        vol_data = slope_corrector(vol_data, visu_pars['VisuCoreDataSlope'])

    # get number sub-volumes
    num_vols = len(elim_consecutive_duplicates(list(visu_pars['VisuCoreOrientation'])))

    if 'VisuCoreTransposition' not in visu_pars.keys():
        visu_core_transposition = [0, ] * vol_pre_shape[2]
    else:
        visu_core_transposition = visu_pars['VisuCoreTransposition']

    if num_vols > 1:

        output_nifti = []

        assert vol_pre_shape[2] % num_vols == 0
        vol_shape = vol_pre_shape[0], vol_pre_shape[1], int(vol_pre_shape[2] / num_vols)

        # get resolution - same for all sub-volumes.
        resolution = compute_resolution_from_visu_pars(visu_pars['VisuCoreExtent'],
                                                       visu_pars['VisuCoreSize'],
                                                       visu_pars['VisuCoreFrameThickness'],
                                                       visu_pars['VisuCoreFrameCount'])

        for id_sub_vol in range(num_vols):

            # compute affine
            affine_transf = compute_affine_from_visu_pars(
                                   list(visu_pars['VisuCoreOrientation'])[id_sub_vol * vol_shape[2]],
                                   list(visu_pars['VisuCorePosition'])[id_sub_vol * vol_shape[2]],
                                   visu_core_transposition[id_sub_vol * vol_shape[2]],
                                   visu_pars['VisuCoreDim'],
                                   resolution)

            # get sub volume in the correct shape
            img_data_sub_vol = vol_data[..., id_sub_vol * vol_shape[2] : (id_sub_vol + 1) * vol_shape[2]]

            if nifti_version == 1:
                nib_im_sub_vol = nib.Nifti1Image(img_data_sub_vol, affine=affine_transf)
            elif nifti_version == 2:
                nib_im_sub_vol = nib.Nifti2Image(img_data_sub_vol, affine=affine_transf)
            else:
                raise IOError('Nifti versions allowed are 1 or 2.')

            hdr_sub_vol = nib_im_sub_vol.header
            hdr_sub_vol.set_qform(affine_transf, qform)
            hdr_sub_vol.set_sform(affine_transf, sform)
            nib_im_sub_vol.update_header()

            output_nifti.append(nib_im_sub_vol)

    else:

        # get shape
        sh = vol_pre_shape

        # check for frame groups:

        if 'VisuFGOrderDescDim' in visu_pars.keys():  # see D-2-73
            if visu_pars['VisuFGOrderDescDim'] > 0:
                if isinstance(visu_pars['VisuFGOrderDesc'], list):
                    if len(visu_pars['VisuFGOrderDesc']) > 1:
                        dims = []
                        for descr in visu_pars['VisuFGOrderDesc'][::-1]:
                            dims.append(int(descr.replace('(', '').replace(')', '').split(',')[0]))
                        if np.prod(dims) == sh[-1]:
                            sh = vol_pre_shape[:-1] + dims

                            stack_data = np.zeros(sh, dtype=np.float64)
                            for t in range(sh[3]):
                                for z in range(sh[2]):
                                    stack_data[:, :, z, t] = vol_data[:, :, z * sh[3] + t]

                            vol_data = np.copy(stack_data)

        # get resolution
        resolution = compute_resolution_from_visu_pars(visu_pars['VisuCoreExtent'],
                                                       visu_pars['VisuCoreSize'],
                                                       visu_pars['VisuCoreFrameThickness'],
                                                       visu_pars['VisuCoreFrameCount'],
                                                       visu_pars['VisuFGOrderDesc'])

        if 'VisuAcqSequenceName' in visu_pars.keys():
            seq_name = visu_pars['VisuAcqSequenceName']
        else:
            seq_name = ''

        # compute affine
        affine_transf = compute_affine_from_visu_pars(
            seq_name,
            list(visu_pars['VisuCoreOrientation'])[0],
            list(visu_pars['VisuCorePosition'])[0],
            visu_core_transposition[0],
            visu_pars['VisuCoreDim'],
            resolution)

        if nifti_version == 1:
            output_nifti = nib.Nifti1Image(vol_data, affine=affine_transf)
        elif nifti_version == 2:
            output_nifti = nib.Nifti2Image(vol_data, affine=affine_transf)
        else:
            raise IOError('Nifti versions allowed are 1 or 2.')

        hdr_sub_vol = output_nifti.header
        hdr_sub_vol.set_qform(affine_transf, qform)
        hdr_sub_vol.set_sform(affine_transf, sform)
        output_nifti.update_header()

    return output_nifti
