'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 9/5/20
'''
import logging
import os
from pkg_lib.pkg_bases.class_base import BaseClass
from pkg_lib.pkg_files.load_data_from_file import *
import matplotlib.pyplot as plt
import numpy as np
import numba
from copy import deepcopy


@numba.jit('Tuple((f8[:], f8[:]))(f8[:], f8[:], f8[:])', cache=True)
def numba_select_points_in_region(x, y, r_factor_region):
    # select only the points (X,Y) in the region:
    index_min = (np.abs(x - r_factor_region[0])).argmin()
    index_max = (np.abs(x - r_factor_region[1])).argmin()
    out_x = np.zeros(len(x[index_min:index_max]))
    out_y = np.empty_like(out_x)
    out_x = x[index_min:index_max]
    out_y = y[index_min:index_max]
    return out_x, out_y


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
    if a is not None and b is None:
        b = deepcopy(a)
    if b is not None and a is None:
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

    def plot_curve(self):
        self.update_label()
        self.transform_curve()
        plt.plot(self.new_coordinate.x,
                 self.new_coordinate.y,
                 lw=2,
                 label=self.curve_label_latex)
        if self.is_src_plotted:
            plt.plot(self.src_coordinate.x,
                     self.src_coordinate.y,
                     lw=2,
                     label='src:'+self.curve_label_latex)
        plt.ylabel(self.label.y, fontsize=20, fontweight='bold')
        plt.xlabel(self.label.x, fontsize=20, fontweight='bold')


if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
    from pkg_lib.pkg_files.load_data_from_file import load_experimental_data
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
    plt.show()

    # obj.src_coordinate.x = np.r_[-20:40.05:0.05]
    # obj.src_coordinate.y = np.sin(obj.src_coordinate.x)
    # obj.transform_coefficient.shift_factor.y = 0.5


