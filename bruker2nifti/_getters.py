import os
import sys
import numpy as np

from _utils import slope_corrector, bruker_read_files


def get_info(pfo_scan):

    if not os.path.isdir(pfo_scan):
        raise IOError('Input folder does not exists.')

    # Get information from relevant files in the folder structure
    acqp = bruker_read_files('acqp', pfo_scan)
    method = bruker_read_files('method', pfo_scan)
    reco = bruker_read_files('reco', pfo_scan)
    visu_pars = bruker_read_files('visu_pars', pfo_scan)

    # And store them in the final info data structure
    info = {'acqp': acqp, 'method': method, 'reco': reco, 'visu_pars': visu_pars}

    return info


def get_info_and_img_data(pfo_scan, correct_slope=True, verbose=0):
    """
    This is the first of the two main components of the bridge constituting the parser,
    going from a raw Bruker scan to a python array and a dictionary containing the additional information.
    Python arrays and dictionaries will be further saved into nifti by the method convert_a_scan.
    :param pfo_scan: path to folder scan (typically inside a study with an integer as folder name).
    :param correct_slope: [True] multiply the data of the image by the slope
    (in this version, the attribute of the nifti image scl_slope that
    usually stores the slope is never used due to possible misuse this value may cause).
    :param verbose: [0] 0 no, 1 yes, 2, debug.
    :return: [info, img_data], info that contains the future header information and img_data the numpy array with the
    data of the future nifti image.
    .. note:: Info is a dictionary of three dictionaries containing respectively the information in
    'acqp', 'method' and 'reco' of the raw format.
    """

    if not os.path.isdir(pfo_scan):
        raise IOError('Input folder does not exists.')

    pfi_seq_data = os.path.join(pfo_scan, 'pdata', '1', '2dseq')

    if not os.path.exists(pfi_seq_data):
        print('File {} not present'.format(pfi_seq_data))
        return False, False

    # Get information from relevant files in the folder structure
    acqp = bruker_read_files('acqp', pfo_scan)
    method = bruker_read_files('method', pfo_scan)
    reco = bruker_read_files('reco', pfo_scan)
    visu_pars = bruker_read_files('visu_pars', pfo_scan)

    # And store them in the final info data structure
    info = {'acqp': acqp, 'method': method, 'reco': reco, 'visu_pars': visu_pars}

    pv_version = info['acqp']['ACQ_sw_version']

    if pv_version == 'PV 5.1':

        # For sanity check:
        if verbose > 1:
            print('\n\nPARAVISION VERSION: {} \n\n'.format(acqp['ACQ_sw_version']))
            # said 2D or 3D
            print("method['SpatDimEnum'] = {} ".format(method['SpatDimEnum']))
            # size of the 2d or 3d stack from RECO
            print("reco['RECO_size'] = {} ".format(reco['RECO_size']))
            # size of the 2d or 3d stack from VISU
            print("visu_pars['VisuCoreSize']) = {} ".format(visu_pars['VisuCoreSize']))
            # number of repetitions
            print("acqp['NR']) = {} ".format(acqp['NR']))
            # number of echo and/or third dimension (can be the shape of the slope)
            print("acqp['NI']) = {} ".format(acqp['NI']))
            # number of echo to be disentagled from the NI, AFTER the slope correction
            print("acqp['ACQ_n_echo_images']) = {} ".format(acqp['ACQ_n_echo_images']))

        # From this point on we parse img_data, using the information obtained from the info.

        # Get data type
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

        # Get data endian_nes - default big!!
        if reco['RECO_byte_order'] == 'littleEndian':
            data_endian_ness = 'little'
        elif reco['RECO_byte_order'] == 'bigEndian':
            data_endian_ness = 'big'
        else:
            data_endian_ness = 'big'

        # Get system endian_nes
        system_endian_nes = sys.byteorder

        # Get image data from the 2d-seq file
        img_data = np.copy(np.fromfile(pfi_seq_data, dtype=dt))

        if not data_endian_ness == system_endian_nes:
            img_data.byteswap(True)

        # Get pre_dimensions: i.e. the dimension before correcting for the slope.
        if method['SpatDimEnum'] == '2D':
            pre_dimensions = reco['RECO_size'][0:2]
        elif method['SpatDimEnum'] == '3D':
            pre_dimensions = method['Matrix'][0:3]
        else:
            raise IOError('Unknown imaging acquisition dimensionality.')

        # Casting to a list of int:
        pre_dimensions = [int(d) for d in pre_dimensions]

        # Consider extra dimensions
        if int(acqp['NR']) > 1 and int(acqp['NI']) > 1:
            pre_dimensions += [int(acqp['NR'])*int(acqp['NI'])]
        else:
            if int(acqp['NR']) > 1:  # Extra dimension for DWI
                pre_dimensions += [int(acqp['NR'])]
            if int(acqp['NI']) > 1:  # Extra dimension for FieldMap, MSME_T2 and alike
                pre_dimensions += [int(acqp['NI'])]

        # Reshape the img_data according to the dimension: - note that we use the Fortran ordering. Swap x, y
        if method['SpatDimEnum'] == '2D':
            img_data = img_data.reshape(pre_dimensions, order='F')
        elif method['SpatDimEnum'] == '3D':

            # Swap x and y: (due to lack of coherence between dimensions reco and visu_pars in PV version 5)
            # TODO: NEED TO VERIFY THIS SWAP IS 'CORRECT'!
            pre_dimensions[0], pre_dimensions[1] = pre_dimensions[1], pre_dimensions[0]

            img_data = img_data.reshape(pre_dimensions, order='F')

        # Correct for the slope when the image is in pre_dimension:
        # this can be done when needed only after the slope correction,
        # as the slope has the length given by info['acqp']['NI']:
        # so echo and last dimension are stacked in the same dimension.
        if correct_slope:

            img_data = slope_corrector(img_data, visu_pars['VisuCoreDataSlope'])

        if int(acqp['ACQ_n_echo_images']) > 1:
            # disentangle last dimension and echo times.
            last_dim = img_data.shape[-1]
            eco_dim = int(acqp['ACQ_n_echo_images'])

            if last_dim % eco_dim is not 0:
                raise IOError('Echo dim and last dim are not compatible. Cannot disentangle them.')
            last_dim_new = int(last_dim / eco_dim)

            # new dimension after slope correction
            dimensions = list(img_data.shape[:-1]) + [last_dim_new, eco_dim]
            img_data = img_data.reshape(dimensions)  # NOT , order='F' don't know why!
            img_data = np.squeeze(img_data)

        elif int(acqp['NR']) > 1 and int(acqp['NI']) > 1:
            # acqp['ACQ_n_echo_images'] was stored in acqp['NI'] instead!
            last_dim = img_data.shape[-1]
            eco_dim = int(acqp['NI'])

            if last_dim % eco_dim is not 0:
                raise IOError('Echo dim and last dim are not compatible. Cannot disentangle them.')
            last_dim_new = int(last_dim / eco_dim)

            # new dimension after slope correction
            dimensions = list(img_data.shape[:-1]) + [eco_dim, last_dim_new]
            img_data = img_data.reshape(dimensions, order='F')
            img_data = np.squeeze(img_data)

        return [info, img_data]  # future header information and image voxel content

    elif pv_version == 'PV 6.0.1':

        # For sanity check:
        if verbose > 1:
            print('PARAVISION VERSION: {} \n\n'.format(info['acqp']['ACQ_sw_version']))
            # said 2D or 3D
            print("method['SpatDimEnum']      = {} ".format(info['method']['SpatDimEnum']))
            # size of the 2d or 3d stack from RECO
            print("reco['RECO_size']          = {} ".format(info['reco']['RECO_size']))
            # size of the 2d or 3d stack from VISU
            print("visu_pars['VisuCoreSize']) = {} ".format(info['visu_pars']['VisuCoreSize']))
            # number of repetitions
            print("acqp['NR'])                = {} ".format(info['acqp']['NR']))
            # number of echo and/or third dimension (can be the shape of the slope)
            print("acqp['NI'])                = {} ".format(info['acqp']['NI']))
            # number of echo to be disentagled from the NI, AFTER the slope correction
            print("acqp['ACQ_n_echo_images']) = {} ".format(info['acqp']['ACQ_n_echo_images']))
        # From this point on we parse img_data, using the information obtained from the info.

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

        # Get data endian_nes - default big!!
        if reco['RECO_byte_order'] == 'littleEndian':
            data_endian_ness = 'little'
        elif reco['RECO_byte_order'] == 'bigEndian':
            data_endian_ness = 'big'
        else:
            data_endian_ness = 'big'

        # Get system endian_nes
        system_endian_nes = sys.byteorder

        # Get image data from the 2d-seq file
        img_data = np.copy(np.fromfile(os.path.join(pfo_scan, 'pdata', '1', '2dseq'), dtype=dt))

        if not data_endian_ness == system_endian_nes:
            img_data.byteswap(True)

        # Get pre_dimensions: i.e. the dimension before correcting for the slope.

        pre_dimensions = list(method['Matrix'].astype(np.int))

        if method['SpatDimEnum'] == '2D':
            if int(acqp['NI']) > 1:  # Extra dimension for FieldMap, MSME_T2 and alike, when 2D
                pre_dimensions += [int(acqp['NI'])]

        elif method['SpatDimEnum'] == '3D':

            # Swap x and y: (due to lack of coherence between dimensions reco and visu_pars in PV version 5)
            if info['reco']['RECO_inp_order'] == 'NO_REORDERING':
                pre_dimensions[0], pre_dimensions[1] = pre_dimensions[1], pre_dimensions[0]

            # Consider extra dimensions for DWI - number of repetitions
            if int(acqp['NR']) > 1:
                pre_dimensions += [int(acqp['NR'])]

        img_data = img_data.reshape(pre_dimensions, order='F')

        # Correct for the slope when the image is in pre_dimension:
        # this can be done when needed only after the slope correction,
        # as the slope has the length given by info['acqp']['NI']:
        # so echo and last dimension are stacked in the same dimension.
        if correct_slope:

            img_data = slope_corrector(img_data, visu_pars['VisuCoreDataSlope'])

            if int(acqp['ACQ_n_echo_images']) > 1:
                # disentangle last dimension and echo times.
                last_dim = img_data.shape[-1]
                eco_dim = int(acqp['ACQ_n_echo_images'])

                if last_dim % eco_dim is not 0:
                    raise IOError('Echo dim and last dim are not compatible. Cannot disentangle them.')
                last_dim_new = int(last_dim / eco_dim)

                # new dimension after slope correction
                dimensions = list(img_data.shape[:-1]) + [last_dim_new, eco_dim]
                img_data = img_data.reshape(dimensions)
                img_data = np.squeeze(img_data)

        return [info, img_data]  # future header information and image voxel content


def get_spatial_resolution_from_info(info):
    """
    from the acqp file it extracts the spatial resolution of the acquisition.
    :param info: as provided as output from get_img_and_info
    :return: info['acqp']['ACQ_sw_version'] reordered 1, 0, 2
    """

    sp_resol = info['method']['SpatResol']
    if len(sp_resol) == 3:

        if info['reco']['RECO_inp_order'] == 'NO_REORDERING':
            return np.array([sp_resol[1], sp_resol[0], sp_resol[2]])
        else:
            return np.array([sp_resol[0], sp_resol[1], sp_resol[2]])

    elif len(sp_resol) == 2:

        slice_thick = info['acqp']['ACQ_slice_thick']  # (*)
        if slice_thick > 0 :
            return np.array([sp_resol[0],  sp_resol[1], slice_thick])
        else:
            return np.array([sp_resol[0], sp_resol[1]])
    else:
        raise IOError("The variable info['method']['SpatResol'] requires some more investigation")


def get_slope_from_info(info):
    """
    From the acqp file, the method extracts the slope of the acquisition.
    :param info: as provided as output from get_img_and_info
    :return: info['visu_pars']['VisuCoreDataSlope'] slope, as the data structure (int, float or array) containing the
    constant factor(s) multiplying each slice or echo aimed at optimising the img_data memory size reducing the number
    of bits used by its type.
    """
    return info['visu_pars']['VisuCoreDataSlope']


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
