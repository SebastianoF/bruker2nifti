import numpy as np
import os
import nibabel as nib
import re
import warnings
from os.path import join as jph


# --- text-files utils ---


def unique_words_in_string(in_string):
    ulist = []
    [ulist.append(s) for s in in_string.split() if s not in ulist]
    return ulist[0]


def indians_file_parser(s, sh=None):
    """
    An here-called indians file is a string obtained from a sequence of rows from a Bruker parameter file
    whose shape needs to be changed, in function of its content and according to an optional parameter sh
    that defines the shape of the output.
    This function transform the indian file in a data structure,
    according to the information that can be parsed in the file:
    A - list of vectors transformed into a list
    B - list of numbers, transformed into a np.ndarray, or single number stored as a float.
    B bis - string of 'inf' repeated n times that will be transformed in a numpy array of 'inf'.
    C - list of strings separated by <>.
    D - everything else becomes a string.

    :param s: string indian file
    :param sh: shape related
    :return: parsed indian file of adequate output.
    """

    s = s.strip()  # removes initial and final spaces.

    # A
    if ("(" in s) and (")" in s):
        s = s[1:-1]  # removes initial and final ( )
        a = ["(" + v + ")" for v in s.split(") (")]
    # B
    elif (
        s.replace("-", "").replace(".", "").replace(" ", "").replace("e", "").isdigit()
    ):
        if " " in s:
            a = np.array([float(x) for x in s.split()])
            if sh is not None:
                a = a.reshape(sh)
        else:
            a = float(s)
    # B-bis
    elif "inf" in s:
        if "inf" == unique_words_in_string(s):
            num_occurrences = sum("inf" == word for word in s.split())
            a = [np.inf] * num_occurrences
        else:
            a = s[:]
    # C
    elif ("<" in s) and (">" in s):
        s = s[1:-1]  # removes initial and final < >
        a = [v for v in s.split("> <")]
    # D
    else:
        a = s[:]

    # added to work with ParaVision vers 6.0.1:
    if isinstance(a, list):
        if len(a) == 1:
            a = a[0]

    return a


def var_name_clean(line_in):
    """
    Removes #, $ and PVM_ from line_in, where line in is a string from a Bruker parameter list file.
    :param line_in: input string
    :return: output string cleaned from #, $ and PVM_
    """
    line_out = line_in.replace("#", "").replace("$", "").replace("PVM_", "").strip()
    return line_out


def from_dict_to_txt_sorted(dict_input, pfi_output):
    """
    Simple auxiliary to save the information contained in a dictionary into a txt file
    at the specified path to file (pfi).
    :param dict_input: input structure dictionary
    :param pfi_output: path to file.
    :return:
    """
    sorted_keys = sorted(dict_input.keys())

    with open(pfi_output, "w") as f:
        f.writelines("{0} = {1} \n".format(k, dict_input[k]) for k in sorted_keys)


def bruker_read_files(param_file, data_path, sub_scan_num="1"):
    """
    Reads parameters files of from Bruker raw data imaging format.
    It parses the files 'acqp', 'method', 'reco', 'visu_pars' and 'subject'.
    Even if only 'visu_pars' is relevant for the conversion to nifti, having a more general parser has turned out
    to be useful in many cases (e.g. in PV5.1 to check).
    :param param_file: file parameter, must be a string in the list ['acqp', 'method', 'reco', 'visu_pars', 'subject'].
    :param data_path: path to data.
    :param sub_scan_num: number of the sub-scan folder where usually the 'reco' and 'visu_pars' parameter files
    are stored.
    :return: dict_info dictionary with the parsed information from the input file.
    """
    if param_file.lower() == "reco":
        if os.path.exists(jph(data_path, "pdata", str(sub_scan_num), "reco")):
            f = open(jph(data_path, "pdata", str(sub_scan_num), "reco"), "r")
        else:
            print(
                "File {} does not exist".format(
                    jph(data_path, "pdata", str(sub_scan_num), "reco")
                )
            )
            return {}
    elif param_file.lower() == "acqp":
        if os.path.exists(jph(data_path, "acqp")):
            f = open(jph(data_path, "acqp"), "r")
        else:
            print("File {} does not exist".format(jph(data_path, "acqp")))
            return {}
    elif param_file.lower() == "method":
        if os.path.exists(jph(data_path, "method")):
            f = open(jph(data_path, "method"), "r")
        else:
            print("File {} does not exist".format(jph(data_path, "method")))
            return {}
    elif param_file.lower() == "visu_pars":
        if os.path.exists(jph(data_path, "pdata", str(sub_scan_num), "visu_pars")):
            f = open(jph(data_path, "pdata", str(sub_scan_num), "visu_pars"), "r")
        elif os.path.exists(
            jph(data_path, str(sub_scan_num), "pdata", "1", "visu_pars")
        ):
            f = open(jph(data_path, str(sub_scan_num), "pdata", "1", "visu_pars"), "r")
        else:
            print(
                "File {} does not exist".format(
                    jph(data_path, "pdata", str(sub_scan_num), "visu_pars")
                )
            )
            return {}
    elif param_file.lower() == "subject":
        if os.path.exists(jph(data_path, "subject")):
            f = open(jph(data_path, "subject"), "r")
        else:
            print("File {} does not exist".format(jph(data_path, "subject")))
            return {}
    else:
        raise IOError(
            "param_file input must be the string 'reco', 'acqp', 'method', 'visu_pars' or 'subject'"
        )

    dict_info = {}
    lines = f.readlines()

    for line_num in range(len(lines)):
        """
        Relevant information are in the lines with '##'.
        For the parameters that have arrays values specified between (), with values in the next line.
        Values in the next line can be parsed in lists or np.ndarray when they contains also characters or numbers.
        """

        line_in = lines[line_num]

        if "##" in line_in:

            if ("$" in line_in) and ("(" in line_in) and ("<" not in line_in):
                # A:
                splitted_line = line_in.split("=")
                # name of the variable contained in the row, and shape:
                var_name = var_name_clean(splitted_line[0][3:])

                done = False
                indian_file = ""
                pos = line_num
                sh = splitted_line[1]
                # this is not the shape of the vector but the beginning of a full vector.
                if sh.replace(" ", "").endswith(",\n"):
                    sh = sh.replace("(", "").replace(")", "").replace("\n", "").strip()
                    indian_file += sh
                    sh = None
                # this is not the shape of the vector but a full vector.
                elif sh.replace(" ", "").endswith(")\n") and "." in sh:
                    sh = sh.replace("(", "").replace(")", "").replace("\n", "").strip()
                    indian_file += sh
                    sh = None
                # this is finally the shape of the vector that will start in the next line.
                else:
                    sh = sh.replace("(", "").replace(")", "").replace("\n", "").strip()
                    sh = [int(num) for num in sh.split(",")]

                while not done:

                    pos += 1
                    # collect the indian file: info related to the same variables that can appears on multiple rows.
                    line_to_explore = lines[
                        pos
                    ]  # tell seek does not work in the line iterators...

                    if ("##" in line_to_explore) or ("$$" in line_to_explore):
                        # indian file is over
                        done = True

                    else:
                        # we store the rows in the indian file all in the same string.
                        indian_file += line_to_explore.replace("\n", "").strip() + " "

                dict_info[var_name] = indians_file_parser(indian_file, sh)

            elif ("$" in line_in) and ("(" not in line_in):
                # B:
                splitted_line = line_in.split("=")
                var_name = var_name_clean(splitted_line[0][3:])
                indian_file = splitted_line[1]

                dict_info[var_name] = indians_file_parser(indian_file)

            elif ("$" not in line_in) and ("(" in line_in):
                # C:
                splitted_line = line_in.split("=")
                var_name = var_name_clean(splitted_line[0][2:])

                done = False
                indian_file = splitted_line[1].strip() + " "
                pos = line_num

                while not done:
                    pos += 1
                    # collect the indian file: info related to the same variables that can appears on multiple rows.
                    line_to_explore = lines[
                        pos
                    ]  # tell seek does not work in the line iterators...
                    if ("##" in line_to_explore) or ("$$" in line_to_explore):
                        # indian file is over
                        done = True
                    else:
                        # we store the rows in the indian file all in the same string.
                        indian_file += line_to_explore.replace("\n", "").strip() + " "

                dict_info[var_name] = indians_file_parser(indian_file)

            elif ("$" not in line_in) and ("(" not in line_in):
                # D:
                splitted_line = line_in.split("=")
                var_name = var_name_clean(splitted_line[0])
                indian_file = splitted_line[1].replace("=", "").strip()
                dict_info[var_name] = indians_file_parser(indian_file)

            else:
                # General case: take it as a simple string.
                splitted_line = line_in.split("=")
                var_name = var_name_clean(splitted_line[0])
                dict_info[var_name] = (
                    splitted_line[1]
                    .replace("(", "")
                    .replace(")", "")
                    .replace("\n", "")
                    .replace("<", "")
                    .replace(">", "")
                    .replace(",", " ")
                    .strip()
                )

        else:
            # line does not contain any 'assignable' variable, so this information is not included in the info.
            pass

    return dict_info


# --- Slope correction utils ---


def eliminate_consecutive_duplicates(input_list):
    """
    Simple funcion to eliminate consecutive duplicates in a list or arrays or in a list of numbers.
    :param input_list: list with possible consecutive duplicates.
    :return: input_list with no consecutive duplicates.
    """
    if isinstance(input_list[0], np.ndarray):
        output_list = [input_list[0]]
        for k in input_list[1:]:
            if not list(k) == list(output_list[-1]):
                output_list.append(k)
        return output_list
    else:
        output_list = [input_list[0]]
        for i in range(1, len(input_list)):
            if not input_list[i] == input_list[i - 1]:
                output_list.append(input_list[i])
        return output_list


def data_corrector(
    data, factors, kind="slope", num_initial_dir_to_skip=None, dtype=np.float64
):
    """
    Slope is a float or a vector that needs to be multiplied to the data, to obtain the data as they are acquired.
    To reduce the weight of an image, each slice can be divided by a common float factor, so that at each voxel only the
    integer remaining is stored:

    real_value_acquired[slice_j][x] = data_integer_reminder[slice_j][x] * float_slope[slice_j][x]

    (where = is an almost equal, where the small loss of accuracy is justified by the huge amount of space saved)

    :param data: data as parsed from the data structure.
    :param factors: can be the slope or the offset as parsed from the data structure
    :param kind: is a string that can be 'slope' (multiplicative factor) or 'offset' additive factor.
    :param num_initial_dir_to_skip: in some cases (as some DWI) the number of slices in the image is higher than the
    provided slope/offset length. Usually it is because the initial directions have no weighted and the first element
    in the slope/offset can correct them all. If num_initial_direction_to_skip=j the slope/offset correction starts
    after j slices, and the initial j timepoint are trimmed by j.
    :param dtype: [np.float64] output datatype.
    :return: data after the slope/offset correction.
    ---
    NOTE 1: if used in sequence to correct for slope and offset, correct FIRST slope, then OFFSET.
    NOTE 2: when read 'factor' think slope or offset. The two are embeded in the same method to avoid code repetition.
    """

    if len(data.shape) > 5:
        raise IOError(
            "4d or lower dimensional images allowed. Input data has shape {} ".format(
                data.shape
            )
        )
    assert kind in ("slope", "offset")

    if hasattr(factors, "__contains__"):
        if np.inf in factors:
            warnings.warn(
                "bruker2nifti - Vector corresponding to {} has some inf values. Can not correct it.".format(
                    kind
                ),
                UserWarning,
            )
            return data

    data = data.astype(dtype)

    if num_initial_dir_to_skip is not None:
        factors = factors[num_initial_dir_to_skip:]
        data = data[..., num_initial_dir_to_skip:]

    # Check compatibility slope and data and if necessarily correct for possible consecutive duplicates
    # (as in some cases, when the size of the slope is larger than any timepoint or spatial point, the problem can
    # be in the fact that there are duplicates in the slope vector. This has been seein only in PV5.1).
    if not (isinstance(factors, int) or isinstance(factors, float)):
        if factors.ndim == 1:
            if (
                not factors.size == data.shape[-1]
                and not factors.size == data.shape[-2]
            ):
                factors = np.array(
                    eliminate_consecutive_duplicates(list(factors)), dtype=np.float64
                )
                if (
                    not factors.size == data.shape[-1]
                    and not factors.size == data.shape[-2]
                ):
                    msg = "Slope shape {0} and data shape {1} appears to be not compatible".format(
                        factors.shape, data.shape
                    )
                    raise IOError(msg)

    if isinstance(factors, int) or isinstance(factors, float):
        # scalar slope/offset times nd array data
        if kind == "slope":
            data *= factors
        elif kind == "offset":
            data += factors

    elif factors.size == 1:
        # scalar slope/offset embedded in a singleton times nd array data
        if kind == "slope":
            data *= factors[0]
        else:
            data += factors[0]

    elif len(data.shape) == 3 and len(factors.shape) == 1:
        # each slice of the 3d image is multiplied an element of the slope consecutively
        if data.shape[2] == factors.shape[0]:
            for t, fa in enumerate(factors):
                if kind == "slope":
                    data[..., t] = data[..., t] * fa
                elif kind == "offset":
                    data[..., t] = data[..., t] + fa
        else:
            raise IOError(
                "Shape of the 2d image and slope dimensions are not consistent"
            )

    elif (
        len(data.shape) == 4
        and len(factors.shape) == 1
        and factors.shape[0] == data.shape[2]
    ):
        # each slice of the 4d image, taken from the third dim, is multiplied by each element of the slope in sequence.
        if factors.size == data.shape[2]:
            for t in range(data.shape[3]):
                for k in range(factors.size):
                    if kind == "slope":
                        data[..., k, t] = data[..., k, t] * factors[k]
                    elif kind == "offset":
                        data[..., k, t] = data[..., k, t] + factors[k]
        else:
            raise IOError(
                "If you are here, your case cannot be converted. Further investigations required."
            )

    elif (
        len(data.shape) == 5
        and len(factors.shape) == 1
        and factors.shape[0] == data.shape[3]
    ):
        # each slice of the 5d image, taken from the fourth dim, is multiplied by each element of the slope in sequence.
        if factors.size == data.shape[3]:
            for t in range(data.shape[4]):
                for k in range(factors.size):
                    if kind == "slope":
                        data[..., k, t] = data[..., k, t] * factors[k]
                    elif kind == "offset":
                        data[..., k, t] = data[..., k, t] + factors[k]
        else:
            raise IOError(
                "If you are here, your case cannot be converted. Further investigations required."
            )

    else:
        # each slice of the nd image, taken from the last dimension, is multiplied by each element of the slope.
        if factors.size == data.shape[-1]:
            for t in range(data.shape[-1]):
                if kind == "slope":
                    data[..., t] = data[..., t] * factors[t]
                elif kind == "offset":
                    data[..., t] = data[..., t] + factors[t]
        else:
            msg = "Slope shape {0} and data shape {1} appears to be not compatible".format(
                factors.shape, data.shape
            )
            raise IOError(msg)

    return data


# -- nifti affine matrix utils --


def compute_resolution_from_visu_pars(vc_extent, vc_size, vc_frame_thickness):
    """
    Resolution parameter is provided as a vector in the 'reco' parameter file. To extract the information from the
    'visu_pars' only, as some scans can lack the reco file, some computation on its paramteres neesd to be performed.
    :param vc_extent: VisuCoreExtent parameter file from 'visu_pars'.
    :param vc_size: VisuCoreSize parameter file from 'visu_pars'.
    :param vc_frame_thickness: VisuCoreFrameThickness parameter file from 'visu_pars'.
    :return:
    """

    if len(vc_extent) == len(vc_size):
        resolution = [e / float(s) for e, s in zip(vc_extent, vc_size)]
    else:
        raise IOError

    if isinstance(vc_frame_thickness, np.ndarray) or isinstance(
        vc_frame_thickness, list
    ):
        vc_frame_thickness = vc_frame_thickness[0]

    if len(vc_extent) == 2:
        resolution += [vc_frame_thickness]
        return resolution
    elif len(vc_extent) == 3:
        return resolution
    else:
        raise IOError


def sanity_check_visu_core_subject_position(vc_subject_position):
    """
    The parameter VisuCoreSubjectPosition can be 'Head_Prone' or 'Head_Supine'. Tertium non datur.
    :param vc_subject_position: VisuCoreSubjectPosition from 'visu_pars'
    :return: Raise error if VisuCoreSubjectPosition is not 'Head_Prone' or 'Head_Supine'
    """
    if vc_subject_position not in ["Head_Prone", "Head_Supine"]:
        msg = "Known cases are 'Head_Prone' or  'Head_Supine' for the parameter 'visu_pars.VisuSubjectPosition."
        raise IOError(msg)


def filter_orientation(visu_parse_orientation):
    """
    Pre-process the paramter value VisuParseOrientation from the 'visu_pars' paramter file.
    :param visu_parse_orientation: VisuParseOrientation from the 'visu_pars' paramter file.
    :return: re-shaped and rounded VisuParseOrientation parameter.
    """

    if not np.prod(visu_parse_orientation.shape) == 9:
        # Take the first 9 elements:
        visu_parse_orientation = visu_parse_orientation.flat[:9]

    ans = np.around(visu_parse_orientation.reshape([3, 3], order="F"), decimals=4)
    return ans


def pivot(v):
    """
    :param v: vector or list
    :return: max in absolute value with original sign or max from origin.
    Corresponds to the main direction for each column of an orientation matrix.
    """
    return v[list(abs(v)).index(abs(v).max())]


def compute_affine_from_visu_pars(
    vc_orientation,
    vc_position,
    vc_subject_position,
    resolution,
    frame_body_as_frame_head=False,
    keep_same_det=True,
    consider_subject_position=False,
):
    """
    How the affine is computed (to the understanding acquired so far):

    0) resolution, orientation and translation are provided in separate arrays, we combine them together in a
    standard 4x4 matrix.

    1) We invert the resulting matrix - according to conventions ParaVision (scanner to image frame)
       and DICOM/Nifti (image to scanner frame).

    2) impose the signs of the first two columns (pivots) to be negative, and the third to be be positive.
    - according to the fact that the provided transformation is DICOM-like (LPS) instead of NIFTI like (RAS)
    (Left/Right, Anterior/Posterior, Inferior/Superior).

    -------- optional changes ----------

    3) frame_body_as_frame_head: Switching the last 2 columns of the rotational part, no matter the value of
    VisuCorePosition - According to the fact we are dealing with quadrupeds and not with humans,
    we need to switch the Anterior-Posterior with the Inferior-Superior direction.
    Set frame_body_as_frame_head=True to set the biped orientation.

    4) consider_subject_position: This can be 'head_prone' or 'head_supine'.
    Reason why sometimes this must be considered for a correct
    orientation and must be considered dis-jointly with frame_body_as_frame_head, is that this parameter is sometimes
    tuned to voluntarily switch from radiological to neurological coordinate systems.
    If the subject is Prone and the technician wants to have the coordinates in neurological he/she can consciously
    set the variable vc_subject_position to 'Head_Supine', even if the subject is not supine.

    5) keep_same_det: Finally, for safety, we can impose the same determinant as the input matrix.

    (If there is any b-vectors list, this is modified accordingly).

    :param vc_orientation: visu core orientation parameter.
    :param vc_position: visu core position parameter. -  corresponds to the translational part of the matrix.
    :param vc_subject_position: 'Head_Prone' or 'Head_Supine'. If head supine and if consider_subject_position is True
    it invert the direction of the axis anterior-posterior. - do not confuse subject_position with positon (read this
    last as 'translation').
    :param resolution: resolution of the image, output of compute_resolution_from_visu_pars in the same module.
    :param frame_body_as_frame_head: [False] to parametrise the difference between monkeys [True] and rats [False].
    :param keep_same_det: in case you want the determinant to be the same as the input one. Consider it in particular
    if frame_body_as_frame_head is set to False, and according to the choice of consider_subject_position.
    :param consider_subject_position: [False] The reason why sometimes this must be considered for a correct
    orientation and sometimes must not, is that this parameter is tuned to voluntarily switch from radiological
    to neurological coordinate systems. If the subject is Prone and the technician wants to have the coordinates
    in neurological he/she can consciously set the variable vc_subject_position to 'Head_Supine'.
    :return: final affine (qform) transformation according to the nifti convention

    NOTE: we are assuming that the angles parametrisation is the same for the input and the output.
    We hope this is the case as we do not have any mean to confirm that. The fslreorient2std from FSL
    should be applied afterwards to all the images (after DWI analysis if any).
    """

    sanity_check_visu_core_subject_position(vc_subject_position)
    vc_orientation = filter_orientation(vc_orientation)

    # 0) integrate resolution with the orientation and add the translation in the projective coordinates:

    result = np.eye(4, dtype=np.float32)
    result[0:3, 0:3] = vc_orientation
    result[0:3, 3] = vc_position

    # 1) Invert the orientation matrix, according to nifti convention and Bruker manual.
    # Round the decimals to avoid precision problems. Check if determinant makes sense.
    result = np.round(np.linalg.inv(result), decimals=4)
    result_det = np.linalg.det(result)
    if result_det == 0:
        raise IOError("Orientation determinant is 0. Cannot grasp this dataset.")

    # 2-3) impose pivot first column negative, second column negative, third column positive
    result_orientation = result[:3, :3]

    result_orientation = result_orientation.dot(
        np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    )
    if frame_body_as_frame_head:  # from SAR to ASL
        result_orientation = result_orientation.dot(
            np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
        )

    if pivot(result_orientation[:, 0]) > 0:
        result_orientation[:, 0] = -1 * result_orientation[:, 0]
    if pivot(result_orientation[:, 1]) > 0:
        result_orientation[:, 1] = -1 * result_orientation[:, 1]
    if pivot(result_orientation[:, 2]) < 0:
        result_orientation[:, 2] = -1 * result_orientation[:, 2]

    result_orientation = result_orientation.dot(np.diag(resolution))

    result[:3, :3] = result_orientation

    # 4) - optional
    if consider_subject_position:
        if vc_subject_position == "Head_Prone":
            result[1, :] = -1 * result[1, :]
    # 5) - optional
    if keep_same_det:
        if (np.linalg.det(result) < 0 < result_det) or (
            np.linalg.det(result) > 0 > result_det
        ):
            result[0, :3] = -1 * result[0, :3]

    return result


# --- b-vectors utils ---


def obtain_b_vectors_orient_matrix(
    vc_orientation,
    vc_subject_position,
    frame_body_as_frame_head=False,
    keep_same_det=True,
    consider_subject_position=False,
):

    """
    See _utils.compute_affine_from_visu_pars help for the same input parameters.
    :param vc_orientation: VisuCoreOrientation parameter file
    :param vc_subject_position: VisuCoreSubjectPosition parameter file
    :param frame_body_as_frame_head:
    :param keep_same_det:
    :param consider_subject_position:
    :return:
    """
    resolution = np.array([1, 1, 1])
    translation = np.array([0, 0, 0])

    aff = compute_affine_from_visu_pars(
        vc_orientation,
        translation,
        vc_subject_position,
        resolution,
        frame_body_as_frame_head=frame_body_as_frame_head,
        keep_same_det=keep_same_det,
        consider_subject_position=consider_subject_position,
    )

    return np.copy(aff[:3, :3])


def normalise_b_vect(b_vect, remove_nan=True):
    """
    Normalisation of the b_vector matrix (dim : num b-vectors x 3)
    :param b_vect: the b_vector matrix (dim : num b-vectors x 3)
    :param remove_nan: remove nan if appears in the b-vector matrix, applying np.nan_to_num.
    :return: normalised b-vectors.
    """

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


def apply_reorientation_to_b_vects(reorientation_matrix, row_b_vectors_in_rows):
    """
    :param reorientation_matrix: a 3x3 matrix representing a reorientation in the 3D space:
    Typically with det = 1 or -1.
    a b c
    d e f
    g h i

    :param row_b_vectors_in_rows:
     A nx3 matrix where n row-major b-vectors (v1, v2, v3, v4, ...) are aligned in rows
    v1_1 v1_2 v1_3
    v2_1 v2_2 v2_3
    v3_1 v3_2 v3_3
    v4_1 v4_2 v4_3
    ...

    :return:
    An nx3 matrix where each row is the corresponding b-vector multiplied by the same matrix reorientation_matrix:
    a.v1_1 +  b.v1_2 + c.v1_3 + d.v1_1 +  e.v1_2 + f.v1_3 + g.v1_1 +  h.v1_2 + i.v1_3
    a.v2_1 +  b.v2_2 + c.v2_3 + d.v2_1 +  e.v2_2 + f.v2_3 + g.v2_1 +  h.v2_2 + i.v2_3
    a.v3_1 +  b.v3_2 + c.v3_3 + d.v3_1 +  e.v3_2 + f.v3_3 + g.v3_1 +  h.v3_2 + i.v3_3
    a.v4_1 +  b.v4_2 + c.v4_3 + d.v4_1 +  e.v4_2 + f.v4_3 + g.v4_1 +  h.v4_2 + i.v4_3
    ...

    """
    b_vectors_in_column_reoriented = np.einsum(
        "ij, kj -> ki", reorientation_matrix, row_b_vectors_in_rows
    )
    return b_vectors_in_column_reoriented


# -- nibabel-related utils --


def set_new_data(image, new_data, new_dtype=None, remove_nan=True):
    """
    From a nibabel image and a numpy array it creates a new image with
    the same header of the image and the new_data as its data.
    :param image: nibabel image
    :param new_data: numpy array
    :param new_dtype:
    :param remove_nan:
    :return: nibabel image
    """
    if remove_nan:
        new_data = np.nan_to_num(new_data)

    # if nifty1
    if image.header["sizeof_hdr"] == 348:
        new_image = nib.Nifti1Image(new_data, image.affine, header=image.header)
    # if nifty2
    elif image.header["sizeof_hdr"] == 540:
        new_image = nib.Nifti2Image(new_data, image.affine, header=image.header)
    else:
        raise IOError("Input image header problem")

    # update data type:
    if new_dtype is None:
        new_image.set_data_dtype(new_data.dtype)
    else:
        new_image.set_data_dtype(new_dtype)

    return new_image


def path_contains_whitespace(*args):

    if re.search("\\s+", os.path.join(*args)):
        return True
    else:
        return False
