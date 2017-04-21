import os
import nibabel as nib
import sys
import numpy as np
import pprint

from os.path import join as jph

from _getters import get_list_scans, get_separate_shells_b_vals_b_vect_from_method
from _utils import compute_affine, bruker_read_files, slope_corrector, normalise_b_vect, \
    from_dict_to_txt_sorted


def scan2struct(pfo_scan,
                correct_slope=True,
                separate_shells_if_dwi=False,
                num_shells=3,
                num_initial_dir_to_skip=7,
                nifti_version=1,
                qform=2,
                sform=1
                ):
    """
    First part of the bridge. Info required to fill nifti header are entangled in a non-linear way.
    Therefore it is necessarily to parse them in an intermediate structure, called here struct.
    Struct has the final product as a nibable image, with the additional informations.
    Parse a scan into a structure called struct, collecting the nifti conversion(s) if more than one
    sub-scan is included in the same scan, other than the additional information.

    Version in progress that takes into account all the information
    :param pfo_scan:
    :param correct_slope:
    :param separate_shells_if_dwi:
    :param num_shells:
    :param num_initial_dir_to_skip:
    :param nifti_version:
    :param qform:
    :param sform:
    :return: output_data data structure containing the nibabel image(s) {nib, acqp, method, reco, visu_pars}
    """
    # Note to the programmer: It can be very complicated to divide this function in indepnended sub-functions.
    # num_volumes_per_scan = len(list(visu_pars['VisuCoreSlicePacksSlices']))
    if not os.path.isdir(pfo_scan):
        raise IOError('Input folder does not exists.')

    # Get information from relevant files in the folder structure
    acqp = bruker_read_files('acqp', pfo_scan)
    method = bruker_read_files('method', pfo_scan)
    reco = bruker_read_files('reco', pfo_scan)

    # Get data endian_nes - default big!!
    if reco['RECO_byte_order'] == 'littleEndian':
        data_endian_ness = 'little'
    elif reco['RECO_byte_order'] == 'bigEndian':
        data_endian_ness = 'big'
    else:
        data_endian_ness = 'big'

    # Get datatype
    if reco['RECO_wordtype'] == '_32BIT_SGN_INT':
        dt = np.int32
    elif reco['RECO_wordtype'] == '_16BIT_SGN_INT':
        dt = np.int16
    elif reco['RECO_wordtype'] == '_8BIT_UNSGN_INT':
        dt = np.uint8
    elif reco['RECO_wordtype'] == '_32BIT_FLOAT':
        dt = np.float32
    else:
        raise IOError('Unknown data type.')

    # Get system endian_nes
    system_endian_nes = sys.byteorder

    # Get sub-scans series in the same scan. Typically there is only one.
    list_sub_scans = get_list_scans(jph(pfo_scan, 'pdata'))

    nib_scans_list = []
    visu_pars_list = []

    for id_sub_scan in list_sub_scans:

        if separate_shells_if_dwi:
            print(num_shells)
            print(num_initial_dir_to_skip)
            # TODO dvide here in subvolume with a nested for-loop, integrating the 'natural' sub-volumes.
            pass

        visu_pars = bruker_read_files('visu_pars', pfo_scan, sub_scan_num=id_sub_scan)

        # GET IMAGE DATA

        if os.path.exists(jph(pfo_scan, 'pdata', id_sub_scan, '2dseq')):
            img_data_vol = np.copy(np.fromfile(jph(pfo_scan, 'pdata', id_sub_scan, '2dseq'), dtype=dt))
        else:
            return 'no data'

        # -- GET PRE DIMENSION, DIMENSION AND RESOLUTION
        # when 2D
        if method['SpatDimEnum'] == '2D':

            if int(acqp['NR']) == 1:
                pre_shape_scan = list(method['Matrix'].astype(np.int)) + [int(acqp['NI']), ]
                if int(acqp['NI']) % int(acqp['ACQ_n_echo_images']) != 0:
                    raise IOError
                shape_scan = list(method['Matrix'].astype(np.int)) + \
                             [int(int(acqp['NI'])/int(acqp['ACQ_n_echo_images'])), int(acqp['ACQ_n_echo_images'])]

            elif int(acqp['NR']) > 1:
                assert int(acqp['ACQ_n_echo_images']) == 1
                pre_shape_scan = list(method['Matrix'].astype(np.int)) + [int(acqp['NI']) * int(acqp['NR']), ]
                shape_scan = list(method['Matrix'].astype(np.int)) + [int(acqp['NI']), int(acqp['NR'])]
            else:
                raise IOError

            # Another test has to be done, yet.
            # Check the compatibility with the data slope. If not compatible update, with the
            # structure (x_dim, ydim, slope_dim, remainder)
            # where reminder = tot_dim / (x_dim * ydim * slope_dim)
            if isinstance(visu_pars['VisuCoreDataSlope'], int) or isinstance(visu_pars['VisuCoreDataSlope'], float):
                num_slopes = 1
            else:
                num_slopes = visu_pars['VisuCoreDataSlope'].shape[0]

            if len(pre_shape_scan) > 2:
                if not pre_shape_scan[2] == num_slopes:

                    tot_dim = int(np.prod(img_data_vol.shape))
                    slope_dim = int(visu_pars['VisuCoreDataSlope'].shape[0])
                    reminder = int(tot_dim / np.prod(list(method['Matrix'].astype(np.int)) + [slope_dim, ])
                                   )

                    pre_shape_scan = list(method['Matrix'].astype(np.int)) + [slope_dim, reminder]
                    shape_scan = pre_shape_scan[:]

            shape_scan = [m for m in shape_scan if m is not 1]
            pre_shape_scan = [m for m in pre_shape_scan if m is not 1]

            # -- GET RESOLUTION WHEN 2D
            sp_resolution = list(method['SpatResol'])
            assert len(sp_resolution) == 2
            slice_thick = acqp['ACQ_slice_thick']
            if slice_thick > 0:
                sp_resolution += [slice_thick, ]

        # when 3D
        elif method['SpatDimEnum'] == '3D':

            assert int(acqp['ACQ_n_echo_images']) == int(acqp['NI'])

            if int(acqp['NI']) > 1:
                pre_shape_scan = list(method['Matrix'].astype(np.int)) + [int(acqp['NI']), ]
                shape_scan = pre_shape_scan[:]

            elif int(acqp['NR']) > 1:
                pre_shape_scan = list(method['Matrix'].astype(np.int)) + [int(acqp['NR']), ]
                shape_scan = pre_shape_scan[:]

            elif int(acqp['NI']) == 1 and int(acqp['NR']) == 1:
                pre_shape_scan = list(method['Matrix'].astype(np.int))
                shape_scan = pre_shape_scan[:]
            else:
                raise IOError

            # Check the compatiblity with the dataSlope as in the previous case.

            if isinstance(visu_pars['VisuCoreDataSlope'], int) or isinstance(visu_pars['VisuCoreDataSlope'], float):
                num_slopes = 1
            else:
                num_slopes = int(visu_pars['VisuCoreDataSlope'].shape[0])

            if len(pre_shape_scan) > 3:
                if not pre_shape_scan[3] == num_slopes:

                    tot_dim = int(np.prod(img_data_vol.shape))
                    reminder = int(tot_dim / np.prod(list(method['Matrix'].astype(np.int)) + [num_slopes, ]))

                    pre_shape_scan = list(method['Matrix'].astype(np.int)) + [num_slopes, reminder]
                    shape_scan = pre_shape_scan[:]

            shape_scan = [m for m in shape_scan if m is not 1]
            pre_shape_scan = [m for m in pre_shape_scan if m is not 1]

            # -- GET RESOLUTION WHEN 3D
            sp_resolution = list(method['SpatResol'])
            assert len(sp_resolution) == 3

        else:
            raise IOError("method['SpatDimEnum'] known are '2D' or '3D' ")

        if reco['RECO_inp_order'] == 'NO_REORDERING':
            pre_shape_scan[0], pre_shape_scan[1] = pre_shape_scan[1], pre_shape_scan[0]
            shape_scan[0], shape_scan[1] = shape_scan[1], shape_scan[0]
            sp_resolution[0], sp_resolution[1] = sp_resolution[1], sp_resolution[0]

        # -- GET ORIENTATION DIRECTIONS:

        # TODO: look at visu_pars['VisuCoreOrientation'] as a 3x3 matrix with some meaning to be established.
        affine_directions = np.eye(3).dot(np.diag([-1, -1, 1]))

        # -- GET TRANSLATIONS:

        translations = visu_pars['VisuCorePosition'][0]

        # -- GET AFFINE

        affine_transf = compute_affine(affine_directions, sp_resolution, translations)

        # -- PROCESS IMG_DATA

        if not data_endian_ness == system_endian_nes:
            img_data_vol.byteswap(True)

        img_data_vol = img_data_vol.reshape(pre_shape_scan, order='F')

        if correct_slope:
            img_data_vol = slope_corrector(img_data_vol, visu_pars['VisuCoreDataSlope'])

        if int(acqp['ACQ_n_echo_images']) > 1:
            img_data_vol = img_data_vol.reshape(shape_scan)
        else:
            img_data_vol = img_data_vol.reshape(shape_scan, order='F')

        # -- BUILD NIB IMAGE

        if nifti_version == 1:
            nib_im = nib.Nifti1Image(img_data_vol, affine=affine_transf)
        elif nifti_version == 2:
            nib_im = nib.Nifti2Image(img_data_vol, affine=affine_transf)
        else:
            raise IOError('Nifti versions allowed are 1 or 2.')

        hdr = nib_im.header
        hdr.set_qform(affine_transf, qform)
        hdr.set_sform(affine_transf, sform)
        nib_im.update_header()

        # UPDATE VARIABLES:

        visu_pars_list.append(visu_pars)
        nib_scans_list.append(nib_im)

    # -- RETURN DATA STRUCTURE

    struct_scan = {'nib_scans_list' : nib_scans_list,
                   'visu_pars_list' : visu_pars_list,
                   'acqp'           : acqp,
                   'reco'           : reco,
                   'method'         : method}

    return struct_scan


def write_struct(struct,
                 pfo_output,
                 fin_scan='',
                 save_human_readable=True,
                 separate_shells_if_dwi=False,
                 num_shells=3,
                 num_initial_dir_to_skip=None,
                 normalise_b_vectors_if_dwi=True,
                 verbose=1):

    if not os.path.isdir(pfo_output):
            raise IOError('Output folder does not exists.')
    if fin_scan is None:
        fin_scan = ''
    # print ordered dictionaries values to console (logorrheic rather than verbose!)
    if verbose > 2:
        print('\n\n -------------- acqp --------------')
        print(pprint.pprint(struct['acqp']))
        print('\n\n -------------- method --------------')
        print(pprint.pprint(struct['method']))
        print('\n\n -------------- reco --------------')
        print(pprint.pprint(struct['reco']))
        print('\n\n -----------------------------------')

    if not len(struct['nib_scans_list']) == len(struct['visu_pars_list']):
        raise IOError

    # -- WRITE Additional data shared by all the sub-scans:

    # if the modality is a DtiEpi or Dwimage then save the DW directions, b values and b vectors in separate csv .txt.
    if 'dtiepi' in struct['method']['Method'].lower() or 'dwi' in struct['method']['Method'].lower():  # modality information

        dw_dir = struct['method']['DwDir']
        if normalise_b_vectors_if_dwi:
            dw_dir = normalise_b_vect(dw_dir)

        np.savetxt(jph(pfo_output, fin_scan + 'DwDir.txt'), dw_dir, fmt='%.14f')

        if verbose > 0:
            msg = 'Diffusion weighted directions saved in ' + jph(pfo_output, fin_scan + 'DwDir.txt')
            print(msg)

        # DwEffBval and DwGradVec are divided by shells
        if separate_shells_if_dwi:

            # save DwEffBval DwGradVec
            [list_b_vals, list_b_vects] = get_separate_shells_b_vals_b_vect_from_method(
                struct['method'],
                num_shells=num_shells,
                num_initial_dir_to_skip=num_initial_dir_to_skip)
            for i in range(num_shells):
                modality = struct['method']['Method'].split(':')[-1]
                path_b_vals_shell_i = jph(pfo_output,
                                                   fin_scan + modality + '_DwEffBval_shell' + str(i) + '.txt')
                path_b_vect_shell_i = jph(pfo_output,
                                                   fin_scan + modality + '_DwGradVec_shell' + str(i) + '.txt')

                np.savetxt(path_b_vals_shell_i, list_b_vals[i], fmt='%.14f')
                np.savetxt(path_b_vect_shell_i, list_b_vects[i], fmt='%.14f')

                if verbose > 0:
                    print('B-vectors for shell {0} saved in {1}'.format(str(i), path_b_vals_shell_i))
                    print('B-values for shell {0} saved in {1}'.format(str(i), path_b_vect_shell_i))

        else:

            b_vals = struct['method']['DwEffBval']
            b_vects = struct['method']['DwGradVec']

            np.savetxt(jph(pfo_output, fin_scan + 'DwEffBval.txt'), b_vals, fmt='%.14f')
            np.savetxt(jph(pfo_output, fin_scan + 'DwGradVec.txt'), b_vects, fmt='%.14f')

            if verbose > 0:
                print('B-vectors saved in {}'.format(jph(pfo_output, fin_scan + 'DwEffBval.txt')))
                print('B-values  saved in {}'.format(jph(pfo_output, fin_scan + 'DwGradVec.txt')))

    # save the dictionary as numpy array containing the corresponding dictionaries
    np.save(jph(pfo_output, fin_scan + '_acqp.npy'),      struct['acqp'])
    np.save(jph(pfo_output, fin_scan + '_method.npy'),    struct['method'])
    np.save(jph(pfo_output, fin_scan + '_reco.npy'),      struct['reco'])

    # save in ordered readable txt files.
    if save_human_readable:
        from_dict_to_txt_sorted(struct['acqp'],   jph(pfo_output,   fin_scan + '_acqp.txt'))
        from_dict_to_txt_sorted(struct['method'], jph(pfo_output,   fin_scan + '_method.txt'))
        from_dict_to_txt_sorted(struct['reco'],   jph(pfo_output,   fin_scan + '_reco.txt'))

    summary_info = {"info['acqp']['ACQ_sw_version']"    : struct['acqp']['ACQ_sw_version'],
                    "info['method']['SpatDimEnum']"     : struct['method']['SpatDimEnum'],
                    "info['method']['Matrix']"          : struct['method']['Matrix'],
                    "info['method']['SpatResol']"       : struct['method']['SpatResol'],
                    "info['reco']['RECO_size']"         : struct['reco']['RECO_size'],
                    "info['reco']['RECO_inp_order']"    : struct['reco']['RECO_inp_order'],
                    "info['acqp']['NR']"                : struct['acqp']['NR'],
                    "info['acqp']['NI']"                : struct['acqp']['NI'],
                    "info['acqp']['ACQ_n_echo_images']" : struct['acqp']['ACQ_n_echo_images'],
                    "info['acqp']['ACQ_slice_thick']"   : struct['acqp']['ACQ_slice_thick']
                    }

    # WRITE DATA SPECIFIC FOR EACH Sub-scan:

    for i in range(len(struct['nib_scans_list'])):

        if len(struct['nib_scans_list']) > 1:
            i_label = str(i)
        else:
            i_label = '0'

        np.save(jph(pfo_output, fin_scan + '_subscan_' + i_label + '_reco.npy'), struct['visu_pars_list'][i])
        if save_human_readable:
            from_dict_to_txt_sorted(struct['reco'], jph(pfo_output, fin_scan + '_subscan_' + i_label + '_reco.txt'))

        summary_info_i = {i_label + "_info['visu_pars']['VisuCoreDataSlope']"   :
                              struct['visu_pars_list'][i]['VisuCoreDataSlope'],
                          i_label + "_info['visu_pars']['VisuCoreSize']"        :
                              struct['visu_pars_list'][i]['VisuCoreSize'],
                          i_label + "_info['visu_pars']['VisuCoreOrientation']" :
                              struct['visu_pars_list'][i]['VisuCoreOrientation'],
                          i_label + "_info['visu_pars']['VisuCorePosition']"    :
                              struct['visu_pars_list'][i]['VisuCorePosition']}

        if struct['method']['SpatDimEnum'] == '2D':
            if 'VisuCoreSlicePacksSlices' in struct['visu_pars_list'][i].keys():
                summary_info_i.update({i_label + "visu_pars['VisuCoreSlicePacksSlices']":
                                         struct['visu_pars_list'][i]['VisuCoreSlicePacksSlices']})

        summary_info.update(summary_info_i)
        from_dict_to_txt_sorted(summary_info, jph(pfo_output, fin_scan + 'summary.txt'))

        # WRITE INFO SUB-SCANNER

        if fin_scan == '':
            pfi_scan = jph(pfo_output, 'scan_' + i_label + '.nii.gz')
        else:
            pfi_scan = jph(pfo_output, fin_scan + i_label + '.nii.gz')

        nib.save(struct['nib_scans_list'][i], pfi_scan)
