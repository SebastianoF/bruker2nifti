import os
import nibabel as nib
import numpy as np

from ._utils import bruker_read_files, eliminate_consecutive_duplicates, slope_corrector, \
    compute_affine_from_visu_pars, compute_resolution_from_visu_pars


def get_list_scans(start_path, print_structure=True):

    scans_list = []

    for dirpath, dirnames, filenames in os.walk(start_path):

        if dirpath == start_path:
            scans_list = [d for d in dirnames if d.isdigit()]

        level = dirpath.replace(start_path, '').count(os.sep)
        indent = (' ' * 4) * level
        if print_structure:
            print('{}{}/'.format(indent, os.path.basename(dirpath)))

        sub_indent = (' ' * 4) * (level + 1)

        if print_structure:
            for f in filenames:
                print('{}{}'.format(sub_indent, f))

    scans_list.sort(key=float)
    return scans_list


def get_subject_name(pfo_study):
    """
    :param pfo_study: path to study folder.
    :return: name of the subject in the study. See get_subject_id.
    """
    # (1) 'subject' at the study level is present
    if os.path.exists(os.path.join(pfo_study, 'subject')):
        subject = bruker_read_files('subject', pfo_study)
        return subject['SUBJECT_study_name']
    # (2) 'subject' at the study level is not present, we use 'VisuSubjectId' from visu_pars of the first scan.
    else:
        list_scans = get_list_scans(pfo_study)
        visu_pars = bruker_read_files('visu_pars', pfo_study, sub_scan_num=list_scans[0])
        return visu_pars['VisuSubjectId']


def nifti_getter(img_data_vol,
                 visu_pars,
                 correct_slope,
                 nifti_version,
                 qform_code,
                 sform_code,
                 frame_body_as_frame_head=False,
                 keep_same_det=True,
                 consider_subject_position=False
                 ):
    # obtaining the nifti using only the information in visu_pars.

    # Check units of measurements:
    if not ['mm', ] * len(visu_pars['VisuCoreSize']) == visu_pars['VisuCoreUnits']:
        # if the UoM is not mm, change here. Add other measurements and refer to xyzt_units from nibabel convention.
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
    num_vols = len(eliminate_consecutive_duplicates(list(visu_pars['VisuCoreOrientation'])))

    # get the default parameters when not filled in the parameter files. - Not used but may be useful in future vers.
    # if 'VisuCoreTransposition' not in visu_pars.keys():
    #     visu_core_transposition = [0, ] * vol_pre_shape[2]
    # else:
    #     visu_core_transposition = visu_pars['VisuCoreTransposition']

    if num_vols > 1:

        output_nifti = []

        assert vol_pre_shape[2] % num_vols == 0
        vol_shape = vol_pre_shape[0], vol_pre_shape[1], int(vol_pre_shape[2] / num_vols)

        # get resolution - same for all sub-volumes.
        resolution = compute_resolution_from_visu_pars(visu_pars['VisuCoreExtent'],
                                                       visu_pars['VisuCoreSize'],
                                                       visu_pars['VisuCoreFrameThickness'])

        for id_sub_vol in range(num_vols):

            # compute affine
            affine_transf = compute_affine_from_visu_pars(
                                   list(visu_pars['VisuCoreOrientation'])[id_sub_vol * vol_shape[2]],
                                   list(visu_pars['VisuCorePosition'])[id_sub_vol * vol_shape[2]],
                                   visu_pars['VisuSubjectPosition'],
                                   resolution,
                                   frame_body_as_frame_head=frame_body_as_frame_head,
                                   keep_same_det=keep_same_det,
                                   consider_subject_position=consider_subject_position)

            # get sub volume in the correct shape
            img_data_sub_vol = vol_data[..., id_sub_vol * vol_shape[2] : (id_sub_vol + 1) * vol_shape[2]]

            if nifti_version == 1:
                nib_im_sub_vol = nib.Nifti1Image(img_data_sub_vol, affine=affine_transf)
            elif nifti_version == 2:
                nib_im_sub_vol = nib.Nifti2Image(img_data_sub_vol, affine=affine_transf)
            else:
                raise IOError('Nifti versions allowed are 1 or 2.')

            hdr_sub_vol = nib_im_sub_vol.header
            hdr_sub_vol.set_qform(affine_transf, code=qform_code)
            hdr_sub_vol.set_sform(affine_transf, code=sform_code)
            hdr_sub_vol['xyzt_units'] = 10  # default mm, seconds
            nib_im_sub_vol.update_header()

            output_nifti.append(nib_im_sub_vol)

    else:

        # get shape
        sh = vol_pre_shape

        # check for frame groups:  -- Very convoluted scaffolding. Waiting to have more infos to refactor this part.
        # ideally an external function read VisuFGOrderDesc should provide the sh and the choice between # A and # B
        # while testing for exception.

        if 'VisuFGOrderDescDim' in visu_pars.keys():  # see D-2-73
            if visu_pars['VisuFGOrderDescDim'] > 0:
                if isinstance(visu_pars['VisuFGOrderDesc'], list):
                    if len(visu_pars['VisuFGOrderDesc']) > 1:
                        descr = visu_pars['VisuFGOrderDesc'][:]
                        # sort descr so that FG_SLICE is the first one, all the others came as they are after swapping.
                        fg_slice_pos = -1
                        fg_echo = -1
                        fg_movie = -1
                        for d in range(len(descr)):
                            if '<FG_SLICE>' in descr[d]:
                                fg_slice_pos = d
                            if '<FG_ECHO>' in descr[d]:
                                fg_echo = d
                            if '<FG_MOVIE>' in descr[d]:
                                fg_movie = d
                        if fg_slice_pos == -1:
                            raise IOError('FG_SLICE not found in the order descriptor, dunno the order.')

                        descr[fg_slice_pos], descr[0] = descr[0], descr[fg_slice_pos]

                        dims = []
                        for dd in descr:
                            dims.append(int(dd.replace('(', '').replace(')', '').split(',')[0]))

                        if np.prod(dims) == sh[-1]:
                            sh = vol_pre_shape[:-1] + dims
                            # A
                            if fg_echo > -1:
                                # MSME
                                stack_data = np.zeros(sh, dtype=vol_data.dtype)
                                for t in range(sh[3]):
                                    for z in range(sh[2]):
                                        stack_data[:, :, z, t] = vol_data[:, :, z * sh[3] + t]

                                vol_data = np.copy(stack_data)
                            # B
                            elif fg_movie > -1:
                                # DTI
                                vol_data = img_data_vol.reshape(sh, order='F')
                            else:
                                # Else ?
                                vol_data = img_data_vol.reshape(sh, order='F')

        # get resolution
        resolution = compute_resolution_from_visu_pars(visu_pars['VisuCoreExtent'],
                                                       visu_pars['VisuCoreSize'],
                                                       visu_pars['VisuCoreFrameThickness'])

        # compute affine
        affine_transf = compute_affine_from_visu_pars(list(visu_pars['VisuCoreOrientation'])[0],
                                                      list(visu_pars['VisuCorePosition'])[0],
                                                      visu_pars['VisuSubjectPosition'],
                                                      resolution)

        if nifti_version == 1:
            output_nifti = nib.Nifti1Image(vol_data, affine=affine_transf)
        elif nifti_version == 2:
            output_nifti = nib.Nifti2Image(vol_data, affine=affine_transf)
        else:
            raise IOError('Nifti versions allowed are 1 or 2.')

        hdr_sub_vol = output_nifti.header
        hdr_sub_vol.set_qform(affine_transf, code=qform_code)
        hdr_sub_vol.set_sform(affine_transf, code=sform_code)
        hdr_sub_vol['xyzt_units'] = 10
        output_nifti.update_header()

    return output_nifti
