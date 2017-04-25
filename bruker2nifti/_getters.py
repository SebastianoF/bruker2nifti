import os

from _utils import bruker_read_files


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
