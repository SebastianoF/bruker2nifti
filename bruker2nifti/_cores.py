import os
import nibabel as nib
import sys
import numpy as np
import pprint

from os.path import join as jph

from _getters import get_list_scans, nifti_getter, get_separate_shells_b_vals_b_vect_from_method
from _utils import bruker_read_files, normalise_b_vect, from_dict_to_txt_sorted, set_new_data


def scan2struct(pfo_scan,
                separate_shells_if_dwi=False,
                num_shells=3,
                num_initial_dir_to_skip=7,
                correct_slope=True,
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
    :param nifti_version:
    :param qform:
    :param sform:
    :return: output_data data structure containing the nibabel image(s) {nib, acqp, method, reco, visu_pars}
    """
    # as scan 2 struct with a different strategy. Will see...!

    if not os.path.isdir(pfo_scan):
        raise IOError('Input folder does not exists.')

    # Get information from relevant files in the folder structure
    acqp = bruker_read_files('acqp', pfo_scan)
    method = bruker_read_files('method', pfo_scan)
    reco = bruker_read_files('reco', pfo_scan)

    if acqp == {} and method == {} and reco == {}:
        raise IOError("No 'acqp', 'method' and 'reco' files. \n\nAre you sure the input folder contains a Bruker scan?")

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

        visu_pars = bruker_read_files('visu_pars', pfo_scan, sub_scan_num=id_sub_scan)

        # GET IMAGE VOLUME
        if os.path.exists(jph(pfo_scan, 'pdata', id_sub_scan, '2dseq')):
            img_data_vol = np.copy(np.fromfile(jph(pfo_scan, 'pdata', id_sub_scan, '2dseq'), dtype=dt))
        else:
            return 'No data here {}'.format(jph(pfo_scan, 'pdata', id_sub_scan))

        if not data_endian_ness == system_endian_nes:
            img_data_vol.byteswap(True)

        if 'dtiepi' in method['Method'].lower():
            correct_slope = False

        # Generate the nifti image using visu_pars.
        nib_im = nifti_getter(img_data_vol, visu_pars, correct_slope, nifti_version, qform, sform)

        # If DWI orient b-vector using visu-pars in coherence with the nib_im obtained.
        if 'dtiepi' in method['Method'].lower():
            pass

        nib_scans_list.append(nib_im)
        visu_pars_list.append(visu_pars)

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
                 save_b0_if_dwi=False,
                 num_shells=3,
                 num_initial_dir_to_skip=None,
                 normalise_b_vectors_if_dwi=True,
                 verbose=1):

    if not os.path.isdir(pfo_output):
        raise IOError('Output folder does not exists.')

    if isinstance(struct, str):
        print struct
        return

    if not len(struct['visu_pars_list']) == len(struct['nib_scans_list']):
        raise IOError('Visu pars list and scans list have a different number of elements.')

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

    # -- WRITE Additional data shared by all the sub-scans:

    # if the modality is a DtiEpi or Dwimage then save the DW directions, b values and b vectors in separate csv .txt.
    is_dwi = 'dtiepi' in struct['method']['Method'].lower() or 'dwi' in struct['method']['Method'].lower()
    if is_dwi:  # modality information

        dw_dir = struct['method']['DwDir']
        if normalise_b_vectors_if_dwi:
            dw_dir = normalise_b_vect(dw_dir)

        np.save(jph(pfo_output, fin_scan + '_DwDir.npy'), dw_dir)

        if save_human_readable:
            np.savetxt(jph(pfo_output, fin_scan + '_DwDir.txt'), dw_dir, fmt='%.14f')

        if verbose > 0:
            msg = 'Diffusion weighted directions saved in ' + jph(pfo_output, fin_scan + '_DwDir.npy')
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
                path_b_vals_shell_i_npy = jph(pfo_output,
                                                   fin_scan + modality + '_DwEffBval_shell' + str(i) + '.npy')
                path_b_vect_shell_i_npy = jph(pfo_output,
                                                   fin_scan + modality + '_DwGradVec_shell' + str(i) + '.npy')

                np.save(path_b_vals_shell_i_npy, list_b_vals[i])
                np.save(path_b_vect_shell_i_npy, list_b_vects[i])

                if save_human_readable:

                    path_b_vals_shell_i_txt = jph(pfo_output,
                                                  fin_scan + modality + '_DwEffBval_shell' + str(i) + '.txt')
                    path_b_vect_shell_i_txt = jph(pfo_output,
                                                  fin_scan + modality + '_DwGradVec_shell' + str(i) + '.txt')
                    np.savetxt(path_b_vals_shell_i_txt, list_b_vals[i], fmt='%.14f')
                    np.savetxt(path_b_vect_shell_i_txt, list_b_vects[i], fmt='%.14f')

                if verbose > 0:
                    print('B-vectors for shell {0} saved in {1}'.format(str(i), path_b_vals_shell_i_npy))
                    print('B-values for shell {0} saved in {1}'.format(str(i), path_b_vect_shell_i_npy))

        else:

            b_vals = struct['method']['DwEffBval']
            b_vects = struct['method']['DwGradVec']

            np.save(jph(pfo_output, fin_scan + '_DwEffBval.npy'), b_vals)
            np.save(jph(pfo_output, fin_scan + '_DwGradVec.npy'), b_vects)

            if save_human_readable:
                np.savetxt(jph(pfo_output, fin_scan + '_DwEffBval.txt'), b_vals, fmt='%.14f')
                np.savetxt(jph(pfo_output, fin_scan + '_DwGradVec.txt'), b_vects, fmt='%.14f')

            if verbose > 0:
                print('B-vectors saved in {}'.format(jph(pfo_output, fin_scan + '_DwEffBval.npy')))
                print('B-values  saved in {}'.format(jph(pfo_output, fin_scan + '_DwGradVec.npy')))

    # save the dictionary as numpy array containing the corresponding dictionaries
    np.save(jph(pfo_output, fin_scan + '_acqp.npy'),      struct['acqp'])
    np.save(jph(pfo_output, fin_scan + '_method.npy'),    struct['method'])
    np.save(jph(pfo_output, fin_scan + '_reco.npy'),      struct['reco'])

    # save in ordered readable txt files.
    if save_human_readable:
        from_dict_to_txt_sorted(struct['acqp'],   jph(pfo_output,   fin_scan + '_acqp.txt'))
        from_dict_to_txt_sorted(struct['method'], jph(pfo_output,   fin_scan + '_method.txt'))
        from_dict_to_txt_sorted(struct['reco'],   jph(pfo_output,   fin_scan + '_reco.txt'))

    summary_info = {"acqp['ACQ_sw_version']"            : struct['acqp']['ACQ_sw_version'],
                    "method['SpatDimEnum']"             : struct['method']['SpatDimEnum'],
                    "method['Matrix']"                  : struct['method']['Matrix'],
                    "method['SpatResol']"               : struct['method']['SpatResol'],
                    "method['Method']"                  : struct['method']['Method'],
                    "method['SPackArrSliceOrient']"     : struct['method']['SPackArrSliceOrient'],
                    "method['SPackArrReadOrient']"      : struct['method']['SPackArrReadOrient'],
                    "reco['RECO_size']"                 : struct['reco']['RECO_size'],
                    "reco['RECO_inp_order']"            : struct['reco']['RECO_inp_order'],
                    "acqp['NR']"                        : struct['acqp']['NR'],
                    "acqp['NI']"                        : struct['acqp']['NI'],
                    "acqp['ACQ_n_echo_images']"         : struct['acqp']['ACQ_n_echo_images'],
                    "acqp['ACQ_slice_thick']"           : struct['acqp']['ACQ_slice_thick']
                    }

    # WRITE DATA SPECIFIC FOR EACH Sub-scan:

    for i in range(len(struct['visu_pars_list'])):

        if len(struct['nib_scans_list']) > 1:
            i_label = '_subscan_' + str(i) + '_'
        else:
            i_label = ''

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

        # Update dictionary for the summary:
        summary_info_i = {i_label[1:] + "visu_pars['VisuCoreDataSlope']"   :
                              struct['visu_pars_list'][i]['VisuCoreDataSlope'],
                          i_label[1:] + "visu_pars['VisuCoreSize']"        :
                              struct['visu_pars_list'][i]['VisuCoreSize'],
                          i_label[1:] + "visu_pars['VisuCoreOrientation']" :
                              struct['visu_pars_list'][i]['VisuCoreOrientation'],
                          i_label[1:] + "visu_pars['VisuCorePosition']"    :
                              struct['visu_pars_list'][i]['VisuCorePosition']}

        if struct['method']['SpatDimEnum'] == '2D':
            if 'VisuCoreSlicePacksSlices' in struct['visu_pars_list'][i].keys():
                summary_info_i.update({i_label[1:] + "visu_pars['VisuCoreSlicePacksSlices']":
                                         struct['visu_pars_list'][i]['VisuCoreSlicePacksSlices']})

        summary_info.update(summary_info_i)

        # C) Save the summary info with the updated information.
        from_dict_to_txt_sorted(summary_info, jph(pfo_output, fin_scan + '_summary.txt'))

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
                    pfi_scan = jph(pfo_output, 'b0_scan' + i_label[:-1] + '.nii.gz')
                else:
                    pfi_scan = jph(pfo_output, 'b0_' + fin_scan + i_label[:-1] + '.nii.gz')
                nib.save(set_new_data(struct['nib_scans_list'][i], struct['nib_scans_list'][i].get_data()[..., 0]),
                         pfi_scan)
                if verbose > 0:
                    msg = 'b0 scan saved alone in ' + pfi_scan
                    print(msg)
