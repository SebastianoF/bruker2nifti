import numpy as np
import os
import nibabel as nib
from sympy.core.cache import clear_cache


def indian_file_parser(s, sh=None):
    """
    An indian file is a string whose shape needs to be changed, in function of its content and an optional parameter sh
    that defines the shape of the output.
    This function transform the indian file in an hopefully meaningful data structure,
    according to the information that can be parsed in the file:
    A - list of vectors transformed into a np.ndarray.
    B - list of numbers, transformed into a np.ndarray, or single number stored as a single float.
    C - list of words separated by <>.
    D - everything else becomes a string.

    :param s: string indian file
    :param sh: shape related
    :return: parsed indian file of adequate output.
    """

    s = s.strip()  # removes initial and final spaces.

    if ('(' in s) and (')' in s):
        s = s[1:-1]  # removes initial and final ( )
        a = ['(' + v + ')' for v in s.split(') (')]
    elif s.replace('-', '').replace('.', '').replace(' ', '').replace('e', '').isdigit():
        if ' ' in s:
            a = np.array([float(x) for x in s.split()])
            if sh is not None:
                a = a.reshape(sh)
        else:
            a = float(s)
    elif ('<' in s) and ('>' in s):
        s = s[1:-1]  # removes initial and final < >
        a = [v for v in s.split('> <')]
    else:
        a = s[:]

    return a


def var_name_clean(line_in):
    """
    Removes #, $ and PVM_ from line_in
    :param line_in: input string
    :return: output string cleaned from #, $ and PVM_
    """
    line_out = line_in.replace('#', '').replace('$', '').replace('PVM_', '').strip()
    return line_out


def bruker_read_files(param_file, data_path, reco_num=1):
    """
    Reads parameters files of from Bruckert raw data imaging format.
    It parses the files 'acqp' 'method' and 'reco'
    :param param_file: file parameter.
    :param data_path: path to data.
    :param reco_num: number of the folder where reco is stored.
    :return: dict_info dictionary with the parsed informations from the input file.
    """

    if param_file.lower() == 'reco':
        f = open(os.path.join(data_path, 'pdata', str(reco_num), 'reco'), 'r')
    elif param_file.lower() == 'acqp':
        f = open(os.path.join(data_path, 'acqp'), 'r')
    elif param_file.lower() == 'method':
        f = open(os.path.join(data_path, 'method'), 'r')
    elif param_file.lower() == 'visu_pars':
        f = open(os.path.join(data_path, 'pdata', '1', 'visu_pars'), 'r')
    elif param_file.lower() == 'subject':
        f = open(os.path.join(data_path, 'subject'), 'r')
    else:
        raise IOError('param_file should be the string reco, acqp, method, visu_pars or subject')

    dict_info = {}
    lines = f.readlines()

    for line_num in range(len(lines)):
        '''
        Relevant information are in the lines with '##'.
        A: for the parameters that have arrays values specified between (), with values in the next line.
           Values in the next line can be parsed in lists or np.ndarray, if they contains also characters
           or only numbers.
        '''

        line_in = lines[line_num]

        if '##' in line_in:

            # A:
            if ('$' in line_in) and ('(' in line_in) and ('<' not in line_in):

                splitted_line = line_in.split('=')
                # name of the variable contained in the row, and shape:
                var_name = var_name_clean(splitted_line[0][3:])
                sh = splitted_line[1].replace('(', '').replace(')', '').replace('\n', '').strip()

                done = False
                indian_file = ''
                pos = line_num

                if '.' in sh:
                    indian_file += sh

                else:
                    sh = [int(num) for num in sh.split(',')]

                while not done:

                    pos += 1
                    # collect the indian file: info related to the same variables that can appears on multiple rows.
                    line_to_explore = lines[pos]  # tell seek does not work in the line iterators...

                    if ('##' in line_to_explore) or ('$$' in line_to_explore):
                        # indian file is over
                        done = True

                    else:
                        # we store the rows in the indian file all in the same string.
                        indian_file += line_to_explore.replace('\n', '').strip() + ' '

                dict_info[var_name] = indian_file_parser(indian_file, sh)

            # B:
            elif ('$' in line_in) and ('(' not in line_in):
                splitted_line = line_in.split('=')
                var_name = var_name_clean(splitted_line[0][3:])
                indian_file = splitted_line[1]

                dict_info[var_name] = indian_file_parser(indian_file)

            # C:
            elif ('$' not in line_in) and ('(' in line_in):

                splitted_line = line_in.split('=')
                var_name = var_name_clean(splitted_line[0][2:])

                done = False
                indian_file = splitted_line[1].strip() + ' '
                pos = line_num

                while not done:

                    pos += 1

                    # collect the indian file: info related to the same variables that can appears on multiple rows.
                    line_to_explore = lines[pos]  # tell seek does not work in the line iterators...

                    if ('##' in line_to_explore) or ('$$' in line_to_explore):
                        # indian file is over
                        done = True

                    else:
                        # we store the rows in the indian file all in the same string.
                        indian_file += line_to_explore.replace('\n', '').strip() + ' '

                dict_info[var_name] = indian_file_parser(indian_file)

            # D:
            elif ('$' not in line_in) and ('(' not in line_in):
                splitted_line = line_in.split('=')
                var_name = var_name_clean(splitted_line[0])
                indian_file = splitted_line[1].replace('=', '').strip()
                dict_info[var_name] = indian_file_parser(indian_file)
            # General case: take it as a simple and clean.
            else:
                splitted_line = line_in.split('=')
                var_name = var_name_clean(splitted_line[0])
                dict_info[var_name] = splitted_line[1].replace('(', '').replace(')', '').replace('\n', ''). \
                                                       replace('<', '').replace('>', '').replace(',', ' ').strip()

    return dict_info


def normalise_b_vect(b_vect, remove_nan=True):

    b_vect_normalised = np.zeros_like(b_vect)
    norms = np.linalg.norm(b_vect, axis=1)

    for r in range(b_vect.shape[0]):
        if norms[r] < 10e-5:
            b_vect_normalised[r, :] = np.nan
        else:
            b_vect_normalised[r, :] = (1 / float(norms[r])) * b_vect[r, :]

    if remove_nan:
        b_vect_normalised = np.nan_to_num(b_vect_normalised)

    return b_vect_normalised


def correct_for_the_slope(data, slope, num_initial_dir_to_skip=None):

    if len(data.shape) > 4:
        raise IOError('4d or lower dimensional images allowed. Input data has shape'.format(data.shape))

    if num_initial_dir_to_skip is not None:
        slope = slope[num_initial_dir_to_skip:]
        data = data[..., num_initial_dir_to_skip:]

    if isinstance(slope, int) or isinstance(slope, float) :
        data = slope * data  # scalar times 3d array

    else:
        if not slope.size == data.shape[3]:
            raise IOError('Shape of the image and slope dimensions are not consistent')
        for t in range(data.shape[3]):
            data[..., t] = data[..., t] * slope[t]

    return data


def list_files(start_path):

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
