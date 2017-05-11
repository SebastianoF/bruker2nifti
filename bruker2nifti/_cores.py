import os
import nibabel as nib
import sys
import numpy as np
import warnings

from os.path import join as jph

from ._getters import get_list_scans, nifti_getter
from ._utils import bruker_read_files, normalise_b_vect, from_dict_to_txt_sorted, set_new_data, \
    apply_reorientation_to_b_vects, obtain_b_vectors_orient_matrix


def scan2struct(pfo_scan,
                correct_slope=True,
                nifti_version=1,
                qform=2,
                sform=1,
                get_acqp=False,
                get_method=False,
                get_reco=False,
                frame_body_as_frame_head=False,
                keep_same_det=True,
                consider_translation=False,
                consider_subject_position=False
                ):
    """
    First part of the bridge. Info required to fill nifti header are in the visu_pars file.
    The user may want to parse as well acqp, method (must when EpiDti) and reco parameter files.
    Data are parsed in the intermediate dictionary struct containing the final scan(s) converted in nibabel
    image, with additional infos.
    :param pfo_scan: path to folder containing the scan
    :param correct_slope: [True] if you want to correct the slope of the values.
    :param nifti_version: [1] output nifti version can be version 1 or version 2
    :param qform: [2] qform of the final nifti image
    :param sform: [1] sform of the final nifti image
    :param get_acqp: [False] if you want to parse the information in the acqp parameter file of the bruker raw data
    :param get_method: [False] if you want to parse the information in the method file. Forced to True when
    dealing with diffusion weighted images.
    :param get_reco: [False] if you want to parse the information in the reco parameter file.
    :param frame_body_as_frame_head: e.g. true if monkey, false if rat.
    :param keep_same_det: impose to have in the nifti affine matrix, the same determinat as in the bruker parameter.
    :param consider_translation: to have the translation information in the final nifti affine matrix. Can be set to
    the origin in most cases, set False if you want to have it as the origin.
    :param consider_subject_position : visu_pars SubjPosition can be 'Head_Prone' or 'Head_Supine'. While it may
    make sense in most cases to take this value into account, in some other it may not, as when it is
    tuned to voluntarily switch from radiological to neurological coordinate systems.
    If the subject is Prone and the technician wants to have the coordinates
    in neurological it can consciously set the variable vc_subject_position to 'Head_Supine'.
    :return: output_data data structure containing the nibabel image(s) {nib_list, visu_pars_list, acqp, method, reco}
    """

    if not os.path.isdir(pfo_scan):
        raise IOError('Input folder does not exists.')

    # Get system endian_nes
    system_endian_nes = sys.byteorder

    # Get sub-scans series in the same experiment.
    list_sub_scans = get_list_scans(jph(pfo_scan, 'pdata'))

    if not list_sub_scans:
        warn_msg = "\nNo sub scan in the folder structure: \n{}. \nAre you sure the input folder contains a " \
                   "proper Bruker scan?\n".format(jph(pfo_scan, 'pdata'))
        warnings.warn(warn_msg)
        return None

    nib_scans_list = []
    visu_pars_list = []

    for id_sub_scan in list_sub_scans:

        visu_pars = bruker_read_files('visu_pars', pfo_scan, sub_scan_num=id_sub_scan)

        if visu_pars == {}:
            warn_msg = "\nNo 'visu_pars' data found here: \n{}. \nAre you sure the input folder contains a " \
                       "proper Bruker scan?\n".format(jph(pfo_scan, 'pdata', id_sub_scan))
            warnings.warn(warn_msg)
            return None

        # Get data endian_nes - default big!!
        if visu_pars['VisuCoreByteOrder'] == 'littleEndian':
            data_endian_ness = 'little'
        elif visu_pars['VisuCoreByteOrder'] == 'bigEndian':
            data_endian_ness = 'big'
        else:
            data_endian_ness = 'big'

        # Get datatype
        if visu_pars['VisuCoreWordType'] == '_32BIT_SGN_INT':
            dt = np.int32
        elif visu_pars['VisuCoreWordType'] == '_16BIT_SGN_INT':
            dt = np.int16
        elif visu_pars['VisuCoreWordType'] == '_8BIT_UNSGN_INT':
            dt = np.uint8
        elif visu_pars['VisuCoreWordType'] == '_32BIT_FLOAT':
            dt = np.float32
        else:
            raise IOError('Unknown data type.')

        # GET IMAGE VOLUME
        if os.path.exists(jph(pfo_scan, 'pdata', id_sub_scan, '2dseq')):
            img_data_vol = np.copy(np.fromfile(jph(pfo_scan, 'pdata', id_sub_scan, '2dseq'), dtype=dt))
        else:
            warn_msg = "\nNo '2dseq' data found here: \n{}. \nAre you sure the input folder contains a " \
                       "proper Bruker scan?\n".format(jph(pfo_scan, 'pdata', id_sub_scan))
            warnings.warn(warn_msg)
            return None

        if not data_endian_ness == system_endian_nes:
            img_data_vol.byteswap(True)

        if 'VisuAcqSequenceName' in visu_pars.keys():
            visu_pars_acq_sequence_name = visu_pars['VisuAcqSequenceName']
        else:
            visu_pars_acq_sequence_name = ''

        is_dwi = 'dtiepi' in visu_pars_acq_sequence_name.lower()

        if is_dwi:
            # Force to not correcting the slope, if true. Diffusion weighted images must be slope corrected before the
            # DTI analysis. They will be to heavy otherwise.
            correct_slope = False
            # Force method to be parsed. Useful infos in this file to process the DWI.
            get_method = True

        # ------------------------------------------------------ #
        # ------ Generate the nifti image using visu_pars. ----- #
        # ------------------------------------------------------ #
        nib_im = nifti_getter(img_data_vol,
                              visu_pars,
                              correct_slope,
                              nifti_version,
                              qform,
                              sform,
                              frame_body_as_frame_head=frame_body_as_frame_head,
                              keep_same_det=keep_same_det,
                              consider_translation=consider_translation,
                              consider_subject_position=consider_subject_position
                              )
        # ------------------------------------------------------ #
        # ------------------------------------------------------ #

        nib_scans_list.append(nib_im)
        visu_pars_list.append(visu_pars)

    # -- Get additional data

    # Get information from method, if it exists. Parse Method parameter and erase the dictionary if unwanted
    method = bruker_read_files('method', pfo_scan)

    if method == {}:
        print("Warning: No 'method' file to parse.")
    if 'Method' in method.keys():
        name_method = method['Method'].replace('<', '').replace('>', '').split(':')[-1]
    else:
        name_method = ''

    if not get_method:
        method = {}

    # Get information from acqp, reco, if they exist.
    acqp   = {}
    reco   = {}

    if get_acqp:
        acqp = bruker_read_files('acqp', pfo_scan)
        if acqp == {}:
            print("Warning: No 'acqp' file to parse.")

    if get_reco:
        reco = bruker_read_files('reco', pfo_scan)
        if reco == {}:
            print("Warning: No 'method' file to parse.")

    # -- Return data structure
    struct_scan = {'nib_scans_list' : nib_scans_list,
                   'visu_pars_list' : visu_pars_list,
                   'acqp'           : acqp,
                   'reco'           : reco,
                   'method'         : method,
                   'name_method'    : name_method}

    return struct_scan


def write_struct(struct,
                 pfo_output,
                 fin_scan='',
                 save_human_readable=True,
                 save_b0_if_dwi=True,
                 verbose=1,
                 frame_body_as_frame_head=False,
                 keep_same_det=True,
                 consider_subject_position=False,
                 ):
    """

    :param struct:
    :param pfo_output:
    :param fin_scan:
    :param save_human_readable:
    :param save_b0_if_dwi:
    :param verbose:
    :param frame_body_as_frame_head:
    :param keep_same_det:
    :param consider_subject_position:
    :return:
    """

    if not os.path.isdir(pfo_output):
        raise IOError('Output folder does not exists.')

    if struct is None:
        return

    if not len(struct['visu_pars_list']) == len(struct['nib_scans_list']):
        raise IOError('Visu pars list and scans list have a different number of elements.')

    if fin_scan is None:
        fin_scan = ''

    # -- WRITE Additional data shared by all the sub-scans:
    # if the modality is a DtiEpi or Dwimage then save the DW directions, b values and b vectors in separate csv .txt.

    is_dwi = 'dtiepi' in struct['visu_pars_list'][0]['VisuAcqSequenceName'].lower() or \
                  'dwi' in struct['visu_pars_list'][0]['VisuAcqSequenceName'].lower()

    if is_dwi:  # File method is the same for each sub-scan. Cannot embed this in the next for cycle.

        # -- Deals with b-vector: normalise, reorient and save in external .npy/txt.
        dw_grad_vec = struct['method']['DwGradVec']

        assert dw_grad_vec.shape[0] == struct['method']['DwNDiffExp']

        # get b-vectors re-orientation matrix from visu-pars
        reorientation_matrix = obtain_b_vectors_orient_matrix(struct['visu_pars_list'][0]['VisuCoreOrientation'],
                                                              struct['visu_pars_list'][0]['VisuSubjectPosition'],
                                                              frame_body_as_frame_head=frame_body_as_frame_head,
                                                              keep_same_det=keep_same_det,
                                                              consider_subject_position=consider_subject_position)

        # apply reorientation
        dw_grad_vec = apply_reorientation_to_b_vects(reorientation_matrix, dw_grad_vec)
        # normalise:
        dw_grad_vec = normalise_b_vect(dw_grad_vec)

        np.save(jph(pfo_output, fin_scan + '_DwGradVec.npy'), dw_grad_vec)

        if save_human_readable:
            np.savetxt(jph(pfo_output, fin_scan + '_DwGradVec.txt'), dw_grad_vec, fmt='%.14f')

        if verbose > 0:
            msg = 'Diffusion weighted directions saved in ' + jph(pfo_output, fin_scan + '_DwDir.npy')
            print(msg)

        b_vals = struct['method']['DwEffBval']
        b_vects = struct['method']['DwDir']

        np.save(jph(pfo_output, fin_scan + '_DwEffBval.npy'), b_vals)
        np.save(jph(pfo_output, fin_scan + '_DwDir.npy'), b_vects)

        if save_human_readable:
            np.savetxt(jph(pfo_output, fin_scan + '_DwEffBval.txt'), b_vals, fmt='%.14f')
            np.savetxt(jph(pfo_output, fin_scan + '_DwDir.txt'), b_vects, fmt='%.14f')

        if verbose > 0:
            print('B-vectors saved in {}'.format(jph(pfo_output, fin_scan + '_DwEffBval.npy')))
            print('B-values  saved in {}'.format(jph(pfo_output, fin_scan + '_DwGradVec.npy')))

    # save the dictionary as numpy array containing the corresponding dictionaries

    if not struct['acqp'] == {}:
        np.save(jph(pfo_output, fin_scan + '_acqp.npy'), struct['acqp'])
        if save_human_readable:
            from_dict_to_txt_sorted(struct['acqp'], jph(pfo_output, fin_scan + '_acqp.txt'))
    if not struct['method'] == {}:
        np.save(jph(pfo_output, fin_scan + '_method.npy'), struct['method'])
        if save_human_readable:
            from_dict_to_txt_sorted(struct['method'], jph(pfo_output, fin_scan + '_method.txt'))
    if not struct['reco'] == {}:
        np.save(jph(pfo_output, fin_scan + '_reco.npy'), struct['reco'])
        if save_human_readable:
            from_dict_to_txt_sorted(struct['reco'], jph(pfo_output, fin_scan + '_reco.txt'))

    # Visu_pars and summary info for each sub-scan:
    summary_info = {}

    for i in range(len(struct['visu_pars_list'])):

        if len(struct['nib_scans_list']) > 1:
            i_label = '_subscan_' + str(i) + '_'
        else:
            i_label = '_'

        # A) Save visu_pars for each sub-scan:
        np.save(jph(pfo_output, fin_scan + i_label + 'visu_pars.npy'), struct['visu_pars_list'][i])

        # B) Save single slope data for each sub-scan (from visu_pars):
        np.save(jph(pfo_output, fin_scan + i_label + 'slope.npy'), struct['visu_pars_list'][i]['VisuCoreDataSlope'])

        # A and B) save them both in .txt if human readable version of data is required.
        if save_human_readable:
            from_dict_to_txt_sorted(struct['visu_pars_list'][i], jph(pfo_output, fin_scan + i_label + 'visu_pars.txt'))

            slope = struct['visu_pars_list'][i]['VisuCoreDataSlope']
            if not isinstance(slope, np.ndarray):
                slope = np.atleast_2d(slope)
            np.savetxt(jph(pfo_output, fin_scan + i_label + 'slope.txt'), slope, fmt='%.14f')

        # Update summary dictionary:
        summary_info_i = {i_label[1:] + "visu_pars['VisuUid']"
                                    : struct['visu_pars_list'][i]['VisuUid'],
                          i_label[1:] + "visu_pars['VisuCoreDataSlope']"
                                    : struct['visu_pars_list'][i]['VisuCoreDataSlope'],
                          i_label[1:] + "visu_pars['VisuCoreSize']"
                                    : struct['visu_pars_list'][i]['VisuCoreSize'],
                          i_label[1:] + "visu_pars['VisuCoreOrientation']"
                                    : struct['visu_pars_list'][i]['VisuCoreOrientation'],
                          i_label[1:] + "visu_pars['VisuCorePosition']"
                                    : struct['visu_pars_list'][i]['VisuCorePosition']}

        if len(list(struct['visu_pars_list'][i]['VisuCoreExtent'])) == 2:
            # equivalent to struct['method']['SpatDimEnum'] == '2D':
            if 'VisuCoreSlicePacksSlices' in struct['visu_pars_list'][i].keys():
                summary_info_i.update({i_label[1:] + "visu_pars['VisuCoreSlicePacksSlices']"
                                                : struct['visu_pars_list'][i]['VisuCoreSlicePacksSlices']})

        if len(list(struct['visu_pars_list'][i]['VisuCoreExtent'])) == 3 and \
                        'VisuCoreDiskSliceOrder' in struct['visu_pars_list'][i].keys():
            # first part equivalent to struct['method']['SpatDimEnum'] == '3D':
            summary_info_i.update({i_label[1:] + "visu_pars['VisuCoreDiskSliceOrder']"
                                            : struct['visu_pars_list'][i]['VisuCoreDiskSliceOrder']})

        if 'VisuCreatorVersion' in struct['visu_pars_list'][i].keys():
            summary_info_i.update({i_label[1:] + "visu_pars['VisuCreatorVersion']"
                                            : struct['visu_pars_list'][i]['VisuCreatorVersion']})

        summary_info.update(summary_info_i)

        # WRITE NIFTI IMAGES:

        if isinstance(struct['nib_scans_list'][i], list):
            # the scan had sub-volumes embedded. they are saved separately
            for sub_vol_id, subvol in enumerate(struct['nib_scans_list'][i]):

                if fin_scan == '':
                    pfi_scan = jph(pfo_output, 'scan' + i_label[:-1] + '_subvol_' + str(sub_vol_id) + '.nii.gz')
                else:
                    pfi_scan = jph(pfo_output, fin_scan + i_label[:-1] + '_subvol_' + str(sub_vol_id) + '.nii.gz')

                nib.save(subvol, pfi_scan)

        else:

            if fin_scan == '':
                pfi_scan = jph(pfo_output, 'scan' + i_label[:-1] + '.nii.gz')
            else:
                pfi_scan = jph(pfo_output, fin_scan + i_label[:-1] + '.nii.gz')

            nib.save(struct['nib_scans_list'][i], pfi_scan)

            if save_b0_if_dwi and is_dwi:

                if fin_scan == '':
                    pfi_scan = jph(pfo_output, 'scan' + i_label[:-1] + '_b0.nii.gz')
                else:
                    pfi_scan = jph(pfo_output, fin_scan + i_label[:-1] + '_b0.nii.gz')
                nib.save(set_new_data(struct['nib_scans_list'][i], struct['nib_scans_list'][i].get_data()[..., 0]),
                         pfi_scan)
                if verbose > 0:
                    msg = 'b0 scan saved alone in ' + pfi_scan
                    print(msg)

    # complete the summary info with additional information from other parameter files, if required:

    if not struct['acqp'] == {}:

        summary_info_acqp = {"acqp['ACQ_sw_version']"     : struct['acqp']['ACQ_sw_version'],
                             "acqp['NR']"                 : struct['acqp']['NR'],
                             "acqp['NI']"                 : struct['acqp']['NI'],
                             "acqp['ACQ_n_echo_images']"  : struct['acqp']['ACQ_n_echo_images'],
                             "acqp['ACQ_slice_thick']"    : struct['acqp']['ACQ_slice_thick']}
        summary_info.update(summary_info_acqp)

    if not struct['method'] == {}:

        summary_info_method = {"method['SpatDimEnum']"         : struct['method']['SpatDimEnum'],
                               "method['Matrix']"              : struct['method']['Matrix'],
                               "method['SpatResol']"           : struct['method']['SpatResol'],
                               "method['Method']"              : struct['method']['Method'],
                               "method['SPackArrSliceOrient']" : struct['method']['SPackArrSliceOrient'],
                               "method['SPackArrReadOrient']"  : struct['method']['SPackArrReadOrient']}
        summary_info.update(summary_info_method)

    if not struct['reco'] == {}:

        summary_info_reco = {"reco['RECO_size']"       : struct['reco']['RECO_size'],
                             "reco['RECO_inp_order']"  : struct['reco']['RECO_inp_order']}
        summary_info.update(summary_info_reco)

    # Finally summary info with the updated information.
    from_dict_to_txt_sorted(summary_info, jph(pfo_output, fin_scan + '_summary.txt'))

    # Get the method name in a single .txt file:
    if struct['name_method'] is not '':
        text_file = open(jph(pfo_output, 'name_method.txt'), "w+")
        text_file.write(struct['name_method'])
        text_file.close()


# TODO: OO structure in a future refactoring?
