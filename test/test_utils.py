import numpy as np
import nibabel as nib

from numpy.testing import assert_array_equal, assert_equal, assert_raises, assert_almost_equal

from bruker2nifti._utils import indians_file_parser, normalise_b_vect, data_corrector, \
    eliminate_consecutive_duplicates, compute_resolution_from_visu_pars, compute_affine_from_visu_pars, \
    apply_reorientation_to_b_vects, set_new_data, obtain_b_vectors_orient_matrix


# --- TEST text-files utils ---


def test_indians_file_parser_A():

    indian_file_test_1 = "('<VisuCoreOrientation>, 0') ('<VisuCorePosition>, 0')"
    indian_file_test_2 = "(EPI (pmv))"
    indian_file_test_3 = "(5, <FG_SLICE>, <>, 0, 2)"
    indian_file_test_4 = "( SPAM )"

    a1 = indians_file_parser(indian_file_test_1)
    a2 = indians_file_parser(indian_file_test_2)
    a3 = indians_file_parser(indian_file_test_3)
    a4 = indians_file_parser(indian_file_test_4)

    assert_equal(a1, ["('<VisuCoreOrientation>, 0')", "('<VisuCorePosition>, 0')"])
    assert_equal(a2, indian_file_test_2)
    assert_equal(a3, indian_file_test_3)
    assert_equal(a4, indian_file_test_4)


def test_indians_file_parser_B():

    indian_file_test_1 = "4.24"
    indian_file_test_2 = "  4.24  "
    indian_file_test_3 = "1"
    indian_file_test_4 = "80 64e2"
    indian_file_test_5 = "22.3 5.3e12 4.4 5.62e-5 3.9 42.42"

    a1 = indians_file_parser(indian_file_test_1)
    a2 = indians_file_parser(indian_file_test_2)
    a3 = indians_file_parser(indian_file_test_3)
    a4 = indians_file_parser(indian_file_test_4, sh=[2])
    a5 = indians_file_parser(indian_file_test_5, sh=[2, 3])
    a6 = indians_file_parser(indian_file_test_5)

    assert_equal(a1, 4.24)
    assert_equal(a2, 4.24)
    assert_equal(a3, 1)
    np.testing.assert_array_equal(a4, np.array([80, 6400]))
    np.testing.assert_array_equal(a5, np.array([[22.3, 5.3e12, 4.4], [5.62e-05, 3.9, 42.42]]))
    np.testing.assert_array_equal(a6, np.array([22.3, 5.3e12, 4.4, 5.62e-05, 3.9, 42.42]))


def test_indians_file_parser_C():

    indian_file_test_1 = "<123.321.123>"
    indian_file_test_2 = "<123.321.123> <123.321.123>"
    indian_file_test_3 = "<20:19:47  1 Sep 2016>"

    a1 = indians_file_parser(indian_file_test_1)
    a2 = indians_file_parser(indian_file_test_2)
    a3 = indians_file_parser(indian_file_test_3)

    assert_equal(a1, '123.321.123')
    assert_equal(a2, ['123.321.123', '123.321.123'])
    assert_equal(a3, '20:19:47  1 Sep 2016')


def test_indians_file_parser_D():

    indian_file_test_1 = "Ultra-Spam"
    indian_file_test_2 = "OtherAnimal"
    indian_file_test_3 = "Prone_Supine"

    a1 = indians_file_parser(indian_file_test_1)
    a2 = indians_file_parser(indian_file_test_2)
    a3 = indians_file_parser(indian_file_test_3)

    assert_equal(a1, indian_file_test_1)
    assert_equal(a2, indian_file_test_2)
    assert_equal(a3, indian_file_test_3)


# --- TEST slope correction utils ---


def test_slope_corrector_int_float_slope():

    in_data = np.random.normal(5, 10, [3, 4, 5])
    sl1 = 5
    sl2 = 5.3

    out_data1 = data_corrector(in_data, sl1, kind='slope', dtype=np.float64)
    out_data2 = data_corrector(in_data, sl2, kind='slope', dtype=np.float64)

    assert_equal(out_data1.dtype, np.float64)
    assert_equal(out_data2.dtype, np.float64)
    assert_array_equal(out_data1, sl1 * in_data)
    assert_array_equal(out_data2, sl2 * in_data)


def test_slope_corrector_slice_wise_slope_3d():

    in_data = np.random.normal(5, 10, [4, 5, 3])
    sl = np.random.normal(5, 10, 3)

    out_data = data_corrector(in_data, sl, kind='slope', dtype=np.float64)

    for k in range(3):
        assert_array_equal(out_data[..., k], in_data[..., k]*sl[k])


def test_slope_corrector_slice_wise_slope_3d_fail():

    in_data = np.random.normal(5, 10, [4, 5, 3])
    sl = np.random.normal(5, 10, 5)

    with assert_raises(IOError):
        data_corrector(in_data, sl)


def test_slope_corrector_slice_wise_slope_4d():

    in_data = np.random.normal(5, 10, [2, 3, 4, 5])
    sl = np.random.normal(5, 10, 4)
    out_data = data_corrector(in_data, sl, kind='slope', dtype=np.float64)

    for t in range(5):
        for k in range(4):
            assert_array_equal(out_data[..., k, t], in_data[..., k, t] * sl[k])

# def test_slope_corrector_slice_wise_slope_4d_fail():
#
#     in_data = np.random.normal(5, 10, [2, 3, 4, 5])
#     sl = np.random.normal(5, 10, 5)
#
#     with assert_raises(IOError):
#         slope_corrector(in_data, sl)


def test_slope_corrector_slice_wise_slope_5d():

    in_data = np.random.normal(5, 10, [2, 3, 4, 5, 6])
    sl = np.random.normal(5, 10, 5)
    out_data = data_corrector(in_data, sl, kind='slope', dtype=np.float64)

    for t in range(6):
        for k in range(5):
            assert_array_equal(out_data[..., k, t], in_data[..., k, t] * sl[k])


def test_slope_corrector_slice_wise_slope_5d_fail():

    in_data = np.random.normal(5, 10, [2, 3, 4, 5, 6])
    sl = np.random.normal(5, 10, 7)

    with assert_raises(IOError):
        data_corrector(in_data, sl, kind='slope')

test_slope_corrector_slice_wise_slope_5d_fail()


# -- TEST nifti affine matrix utils --


def test_compute_resolution_from_visu_pars():

    # 1
    vc_extent = [25.0, 25.0]
    vc_size = [5, 5]
    vc_frame_thickness = 0.123
    res = compute_resolution_from_visu_pars(vc_extent, vc_size, vc_frame_thickness)

    assert_array_equal(res, [5, 5, 0.123])

    # 2
    vc_extent = [30.0, 30.0]
    vc_size = [5, 5]
    vc_frame_thickness = [0.123, 0.124, 0.125]
    res = compute_resolution_from_visu_pars(vc_extent, vc_size, vc_frame_thickness)

    assert_array_equal(res, [6.0, 6.0, 0.123])


# --- TEST b-vectors utils ---


def test_normalise_b_vect():

    num_vects = 30
    v = np.random.normal(5, 10, [num_vects, 3])
    v[5, :] = np.array([np.nan, ] * 3)
    v_normalised = normalise_b_vect(v)

    for k in list(set(range(num_vects)) - {5}):
        assert_almost_equal(np.linalg.norm(v_normalised[k, :]), 1.0)

    assert_equal(np.linalg.norm(v_normalised[5, :]), .0)


def test_apply_reorientation_to_b_vects_1():

    v = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9],
                  [10, 11, 12]])

    m = np.array([[1, 0, 0],
                  [0, 0, 1],
                  [0, 1, 0]])

    u = np.array([[1, 3, 2],
                  [4, 6, 5],
                  [7, 9, 8],
                  [10, 12, 11]])

    w = apply_reorientation_to_b_vects(m, v)

    np.testing.assert_array_equal(u, w)


def test_apply_reorientation_to_b_vects_2():

    v = np.array([[1,  2,  3],
                  [4,  5,  6],
                  [7,  8,  9],
                  [10, 11, 12]])

    m = np.array([[0, 1, 0],
                  [0, 0, 1],
                  [1, 0, 0]])

    u = np.array([[2,  3, 1],
                  [5,  6, 4],
                  [8,  9, 7],
                  [11, 12, 10]])

    w = apply_reorientation_to_b_vects(m, v)

    np.testing.assert_array_equal(u, w)


# -- TEST housekeeping utils --


def test_eliminate_consecutive_duplicates():

    l = [[3, 1, 4, 1], [3, 1, 4, 1], [5, 8, 2], [6, 5, 3], [6, 5, 3], [3, 1, 4, 1], [3, 1, 4, 1]]
    m = eliminate_consecutive_duplicates(l)
    n = [[3, 1, 4, 1], [5, 8, 2], [6, 5, 3], [3, 1, 4, 1]]

    assert_equal(m, n)


def test_set_new_data_basic():

    data_1 = np.random.normal(5, 10, [10, 10, 5])
    affine_1 = np.diag([1, 2, 3, 1])

    data_2 = np.random.normal(5, 10, [3, 2, 4]).astype(np.float32)
    im_data_1 = nib.Nifti1Image(data_1, affine_1)
    im_data_1.set_data_dtype(np.uint8)
    im_data_1.header['descrip'] = 'Spam'

    im_data_2 = set_new_data(im_data_1, data_2)

    assert_array_equal(im_data_2.get_data(), data_2)
    assert_array_equal(im_data_2.affine, affine_1)
    assert_equal(im_data_2.header['descrip'], b'Spam')
    assert_equal(im_data_1.get_data_dtype(), np.uint8)
    assert_equal(im_data_2.get_data_dtype(), np.float32)


def test_set_new_data_new_dtype():

    data_1 = np.random.normal(5, 10, [10, 10, 5])
    affine_1 = np.diag([1, 2, 3, 1])

    data_2 = np.random.normal(5, 10, [3, 2, 4])
    im_data_1 = nib.Nifti1Image(data_1, affine_1)
    im_data_1.set_data_dtype(np.float32)

    im_data_2 = set_new_data(im_data_1, data_2, new_dtype=np.uint16)

    assert_equal(im_data_1.get_data_dtype(), np.float32)
    assert_equal(im_data_2.get_data_dtype(), np.uint16)


def test_set_new_data_nan_no_nan():

    data_1 = np.random.normal(5, 10, [10, 10, 5])
    affine_1 = np.diag([1, 2, 3, 1])

    data_1[2, 2, 2] = np.nan
    data_1[1, 1, 1] = np.nan

    data_2 = np.random.normal(5, 10, [3, 2, 4])

    im_data_1 = nib.Nifti1Image(data_1, affine_1)
    im_data_2 = set_new_data(im_data_1, data_2, new_dtype=np.uint16)

    assert np.nan not in im_data_2.get_data()
