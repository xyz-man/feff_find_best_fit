'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 9/5/20
'''
import logging
import os
import matplotlib as mpl
# mpl.use('Agg')
from pkg_lib.pkg_bases.class_base import BaseClass
from pkg_lib.pkg_files.load_data_from_file import *
import matplotlib.pyplot as plt
import numpy as np
import numba
from copy import deepcopy


@numba.jit('Tuple((f8[:], f8[:], f8[:]))(f8[:], f8[:], f8[:])', cache=True)
def numba_select_points_in_region(x, y, r_factor_region):
    # select only the points (X,Y) in the region:
    index_min = (np.abs(x - r_factor_region[0])).argmin()
    index_max = (np.abs(x - r_factor_region[1])).argmin()
    out_x = np.zeros(len(x[index_min:index_max]))
    out_y = np.empty_like(out_x)
    out_x = x[index_min:index_max]
    out_y = y[index_min:index_max]
    r_region = y
    r_region[0: index_min] = 0
    r_region[index_max: ] = 0
    # r_region is eq to y inside the r_factor_region and eq to 0 outside the region
    return out_x, out_y, r_region, index_min, index_max


def get_points_and_indices_in_region(x_vector=None, y_vector=None, r_factor_region=None):
    '''
    return arrays of points from two input X,Y vectors.
    :param x_vector:
    :param y_vector:
    :param r_factor_region: if is None then the Configuration.SPECTRUM_CALCULATION_R_FACTOR_REGION
    :return:
    out_x - cropped X vector,
    out_y - cropped Y vector,
    y_in_r_region - vector the same length like Y but nas nonzero values only inside selected region,
    index_min - min index value of selected region,
    index_max - max index value of selected region
    '''
    # replace by numba.jit
    out_x = None
    out_y = None
    y_in_r_region = None
    index_min = None
    index_max = None
    if r_factor_region is None:
        r_factor_region = Configuration.SPECTRUM_CALCULATION_R_FACTOR_REGION
    if x_vector is not None and y_vector is not None:
        out_x, out_y, y_in_r_region, index_min, index_max = numba_select_points_in_region(
            np.asarray(x_vector),
            np.asarray(y_vector),
            np.asarray(r_factor_region, dtype=float)
        )
    return out_x, out_y, y_in_r_region, index_min, index_max


@numba.jit('f8(f8[:], f8[:])', cache=True)
def get_r_factor_numba(y_ideal, y_probe):
    # calc R-factor
    # y_ideal - ideal curve
    # y_probe - probing curve
    A1 = np.power(np.abs(np.subtract(y_ideal, y_probe)), 2)
    A2 = np.power(np.abs(y_ideal), 2)
    return (np.sum(A1) / np.sum(A2))


@numba.jit('f8(f8[:], f8[:])', cache=True)
def get_r_factor_numba_v(y_ideal, y_probe):
    # calc R-factor
    # y_ideal - ideal curve
    # y_probe - probing curve
    N = y_ideal.size
    A1 = 0.0
    A2 = 0.0
    for i in range(N):
        A1 += (y_ideal[i]-y_probe[i])**2
        A2 += y_ideal[i]**2
    return A1/A2


def update_one_value_to_another_value(a, b):
    if (a is not None) and (b is None):
        b = deepcopy(a)
    if (b is not None) and (a is None):
        a = deepcopy(b)
    return a, b


class Descartes2D(BaseClass):
    def __init__(self):
        self.x = None
        self.y = None


class Coefficient(BaseClass):
    def __init__(self):
        self.scale_factor = Descartes2D()
        self.scale_factor.x = 1
        self.scale_factor.y = 1
        self.shift_factor = Descartes2D()
        self.shift_factor.x = 0
        self.shift_factor.y = 0


class Curve(BaseClass):
    def __init__(self):
        self.src_coordinate = Descartes2D()
        self.new_coordinate = Descartes2D()
        self.transform_coefficient = Coefficient()

        self.plot_region = Descartes2D()
        self.label = Descartes2D()
        self.label_latex = Descartes2D()
        self.curve_label = None
        self.curve_label_latex = None

        self.is_src_plotted = False

        self.axes = None

    def linear_transform(self, coordinates=None, scale=None, shift=None):
        if (coordinates is not None) and (scale is not None) and (shift is not None):
            return coordinates*scale + shift
        return None

    def transform_curve(self):
        self.new_coordinate.x = self.linear_transform(
            coordinates=self.src_coordinate.x,
            scale=self.transform_coefficient.scale_factor.x,
            shift=self.transform_coefficient.shift_factor.x,
        )
        self.new_coordinate.y = self.linear_transform(
            coordinates=self.src_coordinate.y,
            scale=self.transform_coefficient.scale_factor.y,
            shift=self.transform_coefficient.shift_factor.y,
        )

    def update_label(self):
        if self.label.x is None:
            self.label.x = 'X'
        if self.label.y is None:
            self.label.y = 'Y'

        self.curve_label, self.curve_label_latex = \
            update_one_value_to_another_value(self.curve_label, self.curve_label_latex)

        if self.curve_label is None:
            self.curve_label = 'Curve Y vs X'
            self.curve_label, self.curve_label_latex = \
                update_one_value_to_another_value(self.curve_label, self.curve_label_latex)

    def plot_curve(self, axes=None):
        self.update_label()
        self.transform_curve()
        if axes is None:
            plt.plot(self.new_coordinate.x,
                     self.new_coordinate.y,
                     lw=2,
                     label=self.curve_label_latex)
        else:
            plt.axes(axes)
            axes.plot(self.new_coordinate.x,
                     self.new_coordinate.y,
                     lw=2,
                     label=self.curve_label_latex)
        if self.is_src_plotted:
            if axes is None:
                plt.plot(self.src_coordinate.x,
                         self.src_coordinate.y,
                         lw=2,
                         label='src:'+self.curve_label_latex)
            else:
                plt.axes(axes)
                axes.plot(self.src_coordinate.x,
                         self.src_coordinate.y,
                         lw=2,
                         label='src:'+self.curve_label_latex)

        plt.ylabel(self.label.y, fontsize=20, fontweight='bold')
        plt.xlabel(self.label.x, fontsize=20, fontweight='bold')
        if axes is not None:
            axes.set_ylabel(self.label.y, fontsize=20, fontweight='bold')
            axes.set_xlabel(self.label.x, fontsize=20, fontweight='bold')


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    from pkg_lib.pkg_files.load_data_from_file import load_experimental_data

    fig = plt.figure()
    ax = fig.add_subplot(111)


    obj = Curve()
    file_path1 = os.path.join(
        Configuration.PATH_TO_LOCAL_DATA_DIRECTORY, 'tmp_theoretical', 'ZnO_ideal_p=[100]_0001', 'xmu.dat')
    file_path2 = os.path.join(
        Configuration.PATH_TO_LOCAL_DATA_DIRECTORY, 'tmp_theoretical', 'ZnO_ideal_p=[101]_0001', 'xmu.dat')
    file_path3 = os.path.join(
        Configuration.PATH_TO_LOCAL_DATA_DIRECTORY, 'tmp_theoretical', 'ZnO_ideal_p=[103]_0001', 'xmu.dat')

    obj.src_coordinate.x, obj.src_coordinate.y = load_theoretical_xmu_data(file_path1)
    obj.curve_label = 'ZnO_ideal_p=[100]'
    obj.plot_curve()

    obj.src_coordinate.x, obj.src_coordinate.y = load_theoretical_xmu_data(file_path2)
    obj.curve_label_latex = 'ZnO_ideal_p=[101]'
    obj.plot_curve()

    obj.src_coordinate.x, obj.src_coordinate.y = load_theoretical_xmu_data(file_path3)
    obj.curve_label_latex = 'ZnO_ideal_p=[103]'
    obj.plot_curve()

    data = load_experimental_data()

    obj.src_coordinate.x = data[:, 0]
    obj.src_coordinate.y = data[:, 1]
    obj.curve_label_latex = 'ZnO-0deg'
    obj.plot_curve()
    plt.draw()

    obj.src_coordinate.x = data[:, 0]
    obj.src_coordinate.y = data[:, 2]
    obj.curve_label_latex = 'ZnO-45deg'
    obj.plot_curve()

    obj.src_coordinate.x = data[:, 0]
    obj.src_coordinate.y = data[:, 3]
    obj.curve_label_latex = 'ZnO-75deg'
    obj.plot_curve()
    # obj.src_coordinate.x = np.r_[0:20.05:0.05]
    # obj.src_coordinate.y = np.sin(obj.src_coordinate.x)
    # obj.transform_coefficient.shift_factor.y = 0.5

    plt.legend()
    fig.savefig('temp.png')
    # plt.show()

    # obj.src_coordinate.x = np.r_[-20:40.05:0.05]
    # obj.src_coordinate.y = np.sin(obj.src_coordinate.x)
    # obj.transform_coefficient.shift_factor.y = 0.5


