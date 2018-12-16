import os
import numpy as np
import warnings
import sys

from numpy.testing import assert_array_equal, assert_equal, assert_raises

from bruker2nifti._getters import get_stack_direction_from_VisuCorePosition


def test_get_stack_direction_from_VisuCorePosition_OK_dummy_multiple_cases():
    visu_core_position_ = np.array([[-20., -20.,  -4.],
                                    [-20., -20.,  -2.],
                                    [-20., -20.,   0.],
                                    [-20., -20.,   2.],
                                    [-20., -20.,   4.],
                                    [4., -20.,  20.],
                                    [2., -20.,  20.],
                                    [0., -20.,  20.],
                                    [-2., -20.,  20.],
                                    [-4., -20.,  20.],
                                    [-20.,  4., 20.],
                                    [-20.,  2., 20.],
                                    [-20., 0., 20.],
                                    [-20., - 2.,  20.],
                                    [-20., - 4., 20.]])
    a = get_stack_direction_from_VisuCorePosition(visu_core_position_, 3)
    assert_equal(a, 'z+x-y-')


def test_get_stack_direction_from_VisuCorePosition_OK_dummy_single_cases():
    vcp1 = np.array([[-4., -20.,  20.], [-2., -20., 20.],  [0., -20., 20.], [2., -20.,  20.], [4., -20., 20.]])
    vcp2 = np.array([[4., -20.,  20.], [2., -20.,  20.],  [0., -20.,  20.], [-2., -20.,  20.],  [-4., -20., 20.]])
    vcp3 = np.array([[-20.,  -4.,  20.], [-20.,  -2.,  20.], [-20.,   0.,  20.], [-20.,  2.,  20.], [-20.,  4., 20.]])
    vcp4 = np.array([[-20.,   4.,  20.], [-20.,   2.,  20.], [-20.,   0.,  20.], [-20.,  -2.,  20.], [-20.,  -4., 20.]])
    vcp5 = np.array([[-20., -20.,  -4.], [-20., -20.,  -2.], [-20., -20.,   0.], [-20., -20.,   2.], [-20., -20.,  4.]])
    vcp6 = np.array([[-20., -20.,  4.], [-20., -20.,  2.],  [-20., -20.,   0.], [-20., -20., -2.], [-20., -20., -4.]])

    a1 = get_stack_direction_from_VisuCorePosition(vcp1, 1)
    a2 = get_stack_direction_from_VisuCorePosition(vcp2, 1)
    a3 = get_stack_direction_from_VisuCorePosition(vcp3, 1)
    a4 = get_stack_direction_from_VisuCorePosition(vcp4, 1)
    a5 = get_stack_direction_from_VisuCorePosition(vcp5, 1)
    a6 = get_stack_direction_from_VisuCorePosition(vcp6, 1)

    assert_equal(a1, 'x+')
    assert_equal(a2, 'x-')
    assert_equal(a3, 'y+')
    assert_equal(a4, 'y-')
    assert_equal(a5, 'z+')
    assert_equal(a6, 'z-')


def test_get_stack_direction_from_VisuCorePosition_wrong_shape1():
    vcp = np.array([[-4., -20., 20.]])
    with assert_raises(IOError):
        get_stack_direction_from_VisuCorePosition(vcp, 1)
    vcp = np.array([-4., -20., 20.])
    with assert_raises(IOError):
        get_stack_direction_from_VisuCorePosition(vcp, 1)


def test_get_stack_direction_from_VisuCorePosition_wrong_shape2():
    vcp = np.array([[[-4., -20., 20.], [-2., -20., 20.]], [[0., -20., 20.], [2., -20., 20.]]])
    with assert_raises(IOError):
        get_stack_direction_from_VisuCorePosition(vcp, 1)


def test_get_stack_direction_from_VisuCorePosition_wrong_shape3():
    vcp = np.array([[-20., -20.], [-20., -20.],  [-20., -20.], [-20., -20.], [-20., -20.]])
    with assert_raises(IOError):
        get_stack_direction_from_VisuCorePosition(vcp, 1)


def test_get_stack_direction_from_VisuCorePosition_wrong_sub_volumes():
    visu_core_position_ = np.array([[-20., -20., -4.],
                                    [-20., -20., -2.],
                                    [-20., -20., 0.],
                                    [-20., -20., 2.],
                                    [-20., -20., 4.],
                                    [4., -20., 20.],
                                    [2., -20., 20.],
                                    [0., -20., 20.],
                                    [-2., -20., 20.],
                                    [-4., -20., 20.],
                                    [-20., 4., 20.],
                                    [-20., 2., 20.],
                                    [-20., 0., 20.],
                                    [-20., - 2., 20.],
                                    [-20., - 4., 20.]])
    with assert_raises(IOError):
        get_stack_direction_from_VisuCorePosition(visu_core_position_, 2)
